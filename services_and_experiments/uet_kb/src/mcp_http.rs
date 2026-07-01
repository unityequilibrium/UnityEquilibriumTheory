use axum::{
    extract::State,
    routing::post,
    Json, Router,
};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use sqlx::{Pool, Postgres};
use tower_http::cors::{Any, CorsLayer};

use crate::db;
use crate::embeddings;

#[derive(Deserialize)]
struct McpHttpRequest {
    jsonrpc: String,
    method: String,
    params: Option<Value>,
    id: Option<Value>,
}

#[derive(Serialize)]
struct McpHttpResponse {
    jsonrpc: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    result: Option<Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    error: Option<McpError>,
    id: Option<Value>,
}

#[derive(Serialize)]
struct McpError {
    code: i32,
    message: String,
    data: Option<Value>,
}

pub async fn run_http_mcp_server(db_url: &str, port: u16) -> anyhow::Result<()> {
    let pool = db::init_db(db_url).await?;

    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    let app = Router::new()
        .route("/mcp", post(handle_mcp_http))
        .route("/health", axum::routing::get(|| async { Json(json!({"status": "ok"})) }))
        .layer(cors)
        .with_state(pool);

    let addr = format!("0.0.0.0:{}", port);
    eprintln!("MCP HTTP Server listening on http://{}", addr);

    let listener = tokio::net::TcpListener::bind(&addr).await?;
    axum::serve(listener, app).await?;
    Ok(())
}

async fn handle_mcp_http(
    State(pool): State<Pool<Postgres>>,
    Json(req): Json<McpHttpRequest>,
) -> Json<McpHttpResponse> {
    let result = dispatch_method(&req.method, req.params, &pool).await;

    match result {
        Ok(res) => Json(McpHttpResponse {
            jsonrpc: "2.0".to_string(),
            result: Some(res),
            error: None,
            id: req.id,
        }),
        Err(err) => Json(McpHttpResponse {
            jsonrpc: "2.0".to_string(),
            result: None,
            error: Some(err),
            id: req.id,
        }),
    }
}

async fn dispatch_method(method: &str, params: Option<Value>, pool: &Pool<Postgres>) -> Result<Value, McpError> {
    match method {
        "initialize" => Ok(json!({
            "protocolVersion": "2024-11-05",
            "serverInfo": {
                "name": "uet_kb_mcp",
                "version": "0.2.0"
            },
            "capabilities": {
                "tools": { "listChanged": false }
            }
        })),
        "notifications/initialized" => Ok(json!(true)),
        "tools/list" => Ok(json!({
            "tools": [
                {
                    "name": "search_knowledge_base",
                    "description": "Search the UET knowledge base using semantic hash-based vector search",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": { "type": "string", "description": "Natural language search query" },
                            "top_k": { "type": "integer", "description": "Number of results (default 10)" }
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "search_physics",
                    "description": "Search using UET physics-informed 20D vector (energy, information, gamma, ...)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "physics_vector": { "type": "array", "items": { "type": "number" } }
                        },
                        "required": ["physics_vector"]
                    }
                },
                {
                    "name": "ingest_document",
                    "description": "Ingest a text document into the knowledge base with automatic embedding",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "path": { "type": "string", "description": "Document path or title" },
                            "content": { "type": "string", "description": "Full text content to ingest" },
                            "metadata": { "type": "object", "description": "Optional metadata (topic_id, etc.)" }
                        },
                        "required": ["path", "content"]
                    }
                },
                {
                    "name": "get_document",
                    "description": "Retrieve a document by its UUID",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "doc_id": { "type": "string" }
                        },
                        "required": ["doc_id"]
                    }
                },
                {
                    "name": "count_documents",
                    "description": "Count total documents in the knowledge base",
                    "inputSchema": { "type": "object", "properties": {}, "required": [] }
                },
                {
                    "name": "list_topics",
                    "description": "List all unique topic IDs from document metadata",
                    "inputSchema": { "type": "object", "properties": {}, "required": [] }
                }
            ]
        })),
        "tools/call" => handle_tool_call(params, pool).await,
        "ping" => Ok(json!({})),
        _ => Err(McpError {
            code: -32601,
            message: format!("Method not found: {}", method),
            data: None,
        }),
    }
}

async fn handle_tool_call(params: Option<Value>, pool: &Pool<Postgres>) -> Result<Value, McpError> {
    let params = params.ok_or(McpError {
        code: -32602,
        message: "Missing params".to_string(),
        data: None,
    })?;

    let name = params.get("name").and_then(|v| v.as_str()).ok_or(McpError {
        code: -32602,
        message: "Missing tool name".to_string(),
        data: None,
    })?;

    let args = params.get("arguments").cloned().unwrap_or(json!({}));

    match name {
        "search_knowledge_base" => {
            let query = args.get("query").and_then(|v| v.as_str()).unwrap_or("");
            let top_k = args.get("top_k").and_then(|v| v.as_i64()).unwrap_or(10);

            let query_vec = embeddings::hash_embed(query, 1024);

            let results = db::search_similar(pool, &query_vec, top_k).await.map_err(|e| McpError {
                code: -32000,
                message: e.to_string(),
                data: None,
            })?;

            Ok(json!({ "content": [{ "type": "text", "text": serde_json::to_string_pretty(&results).unwrap_or_default() }] }))
        }
        "search_physics" => {
            let physics_vec_arg = args.get("physics_vector").and_then(|v| v.as_array());

            let query_vec: Vec<f64> = physics_vec_arg
                .map(|v| v.iter().map(|val| val.as_f64().unwrap_or(0.0)).collect())
                .ok_or(McpError {
                    code: -32602,
                    message: "Missing physics_vector".to_string(),
                    data: None,
                })?;

            let results = db::search_physics(pool, &query_vec, 10).await.map_err(|e| McpError {
                code: -32000,
                message: e.to_string(),
                data: None,
            })?;

            Ok(json!({ "content": [{ "type": "text", "text": serde_json::to_string_pretty(&results).unwrap_or_default() }] }))
        }
        "ingest_document" => {
            let path = args.get("path").and_then(|v| v.as_str()).unwrap_or("untitled");
            let content = args.get("content").and_then(|v| v.as_str()).ok_or(McpError {
                code: -32602,
                message: "Missing content".to_string(),
                data: None,
            })?;
            let metadata = args.get("metadata").cloned();

            let doc_id = db::insert_document(pool, None, path, content, metadata)
                .await
                .map_err(|e| McpError {
                    code: -32000,
                    message: e.to_string(),
                    data: None,
                })?;

            // Chunk and embed
            let chunks: Vec<&str> = content.split('\n').filter(|s| !s.trim().is_empty()).collect();
            let mut chunk_count = 0;
            for chunk_text in &chunks {
                let s_vec = embeddings::hash_embed(chunk_text, 1024);
                let p_vec = vec![0.0; 20];
                db::insert_chunk(pool, &doc_id, chunk_text, &s_vec, &p_vec)
                    .await
                    .map_err(|e| McpError {
                        code: -32000,
                        message: e.to_string(),
                        data: None,
                    })?;
                chunk_count += 1;
            }

            Ok(json!({
                "content": [{
                    "type": "text",
                    "text": format!("Ingested document '{}' (id: {}) with {} chunks", path, doc_id, chunk_count)
                }]
            }))
        }
        "get_document" => {
            let doc_id = args.get("doc_id").and_then(|v| v.as_str()).unwrap_or("");
            let doc = db::get_document(pool, doc_id).await.map_err(|e| McpError {
                code: -32000,
                message: e.to_string(),
                data: None,
            })?;

            Ok(json!({ "content": [{ "type": "text", "text": serde_json::to_string_pretty(&doc).unwrap_or_default() }] }))
        }
        "count_documents" => {
            let count = db::count_documents(pool).await.map_err(|e| McpError {
                code: -32000,
                message: e.to_string(),
                data: None,
            })?;

            Ok(json!({ "content": [{ "type": "text", "text": format!("Total documents: {}", count) }] }))
        }
        "list_topics" => {
            let topics = db::list_topics(pool).await.map_err(|e| McpError {
                code: -32000,
                message: e.to_string(),
                data: None,
            })?;

            Ok(json!({ "content": [{ "type": "text", "text": serde_json::to_string_pretty(&topics).unwrap_or_default() }] }))
        }
        _ => Err(McpError {
            code: -32601,
            message: format!("Tool not found: {}", name),
            data: None,
        }),
    }
}

use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use tokio::io::{self, AsyncBufReadExt, AsyncWriteExt, BufReader};
use crate::db;

#[derive(Serialize, Deserialize, Debug)]
struct JsonRpcRequest {
    jsonrpc: String,
    method: String,
    params: Option<Value>,
    id: Option<Value>,
}

#[derive(Serialize, Deserialize, Debug)]
struct JsonRpcResponse {
    jsonrpc: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    result: Option<Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    error: Option<JsonRpcError>,
    id: Option<Value>,
}

#[derive(Serialize, Deserialize, Debug)]
struct JsonRpcError {
    code: i32,
    message: String,
    data: Option<Value>,
}

pub async fn run_mcp_server(db_url: &str) -> anyhow::Result<()> {
    eprintln!("MCP Server Running... (Listening on Stdin)");

    // Connect to DB once
    let pool = db::init_db(db_url).await?;

    let stdin = io::stdin();
    let mut reader = BufReader::new(stdin);
    let mut stdout = io::stdout();

    let mut line = String::new();
    loop {
        line.clear();
        let bytes_read = reader.read_line(&mut line).await?;
        if bytes_read == 0 {
            break; // EOF
        }

        let trim_line = line.trim();
        if trim_line.is_empty() {
            continue;
        }

        eprintln!("Received: {}", trim_line);

        match serde_json::from_str::<JsonRpcRequest>(trim_line) {
            Ok(req) => {
                // Check if it's a notification (no id)
                let is_notification = req.id.is_none();

                let response = handle_request(req, &pool).await;

                // Only send response if it's NOT a notification
                if !is_notification {
                    let mut resp_str = serde_json::to_string(&response)?;
                    resp_str.push('\n');
                    stdout.write_all(resp_str.as_bytes()).await?;
                    stdout.flush().await?;
                } else {
                    eprintln!("Processed notification, no response sent.");
                }
            }
            Err(e) => {
                eprintln!("Failed to parse JSON: {}", e);
                let error_response = json!({
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32700,
                        "message": "Parse error",
                        "data": e.to_string()
                    },
                    "id": null
                });
                let mut resp_str = serde_json::to_string(&error_response)?;
                resp_str.push('\n');
                stdout.write_all(resp_str.as_bytes()).await?;
                stdout.flush().await?;
            }
        }
    }
    Ok(())
}

async fn handle_request(req: JsonRpcRequest, pool: &sqlx::Pool<sqlx::Postgres>) -> JsonRpcResponse {
    let result = match req.method.as_str() {
        "initialize" => Ok(json!({
            "protocolVersion": "2024-11-05",
            "serverInfo": {
                "name": "uet_kb_mcp",
                "version": "0.1.0"
            },
            "capabilities": {
                "tools": {
                    "listChanged": false
                }
            }
        })),
        "notifications/initialized" => Ok(json!(true)), // Acknowledgement
        "tools/list" => Ok(json!({
            "tools": [
                {
                    "name": "search_knowledge_base",
                    "description": "Search for relevant concepts using semantic vector search",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": { "type": "string" },
                            "query_vector": { "type": "array", "items": { "type": "number" } }
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "search_physics",
                    "description": "Search for relevant concepts using UET physics-informed vector search",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "physics_vector": { "type": "array", "items": { "type": "number" } }
                        },
                        "required": ["physics_vector"]
                    }
                },
                {
                    "name": "get_document",
                    "description": "Retrieve a document by ID (no vectors returned)",
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
                    "description": "Count total documents in knowledge base",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "list_topics",
                    "description": "List all unique topics from metadata",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            ]
        })),
        "tools/call" => handle_tool_call(req.params, pool).await,
        "ping" => Ok(json!({})),

        _ => Err(JsonRpcError {
            code: -32601,
            message: format!("Method not found: {}", req.method),
            data: None,
        }),
    };

    match result {
        Ok(res) => JsonRpcResponse {
            jsonrpc: "2.0".to_string(),
            result: Some(res),
            error: None,
            id: req.id,
        },
        Err(err) => JsonRpcResponse {
            jsonrpc: "2.0".to_string(),
            result: None,
            error: Some(err),
            id: req.id,
        },
    }
}

async fn handle_tool_call(params: Option<Value>, pool: &sqlx::Pool<sqlx::Postgres>) -> Result<Value, JsonRpcError> {
    let params = params.ok_or(JsonRpcError {
        code: -32602,
        message: "Missing params".to_string(),
        data: None,
    })?;

    let name = params.get("name").and_then(|v| v.as_str()).ok_or(JsonRpcError {
        code: -32602,
        message: "Missing tool name".to_string(),
        data: None,
    })?;

    let args = params.get("arguments").cloned().unwrap_or(json!({}));

    match name {
        "search_knowledge_base" => {
            let semantic_vec_arg = args.get("query_vector").and_then(|v| v.as_array());

            let query_vec: Vec<f64> = if let Some(v) = semantic_vec_arg {
                v.iter().map(|val| val.as_f64().unwrap_or(0.0)).collect()
            } else {
                vec![0.0; 1024] // Fallback to zero vector
            };

            let results = db::search_similar(pool, &query_vec, 10).await.map_err(|e| JsonRpcError {
                code: -32000,
                message: e.to_string(),
                data: None
            })?;

            Ok(json!({
                 "results": results
            }))
        },
        "search_physics" => {
            let physics_vec_arg = args.get("physics_vector").and_then(|v| v.as_array());

            let query_vec: Vec<f64> = if let Some(v) = physics_vec_arg {
                v.iter().map(|val| val.as_f64().unwrap_or(0.0)).collect()
            } else {
                return Err(JsonRpcError {
                    code: -32602,
                    message: "Missing physics_vector".to_string(),
                    data: None
                });
            };

            let results = db::search_physics(pool, &query_vec, 10).await.map_err(|e| JsonRpcError {
                code: -32000,
                message: e.to_string(),
                data: None
            })?;

            Ok(json!({
                 "results": results
            }))
        },
        "get_document" => {
            let doc_id = args.get("doc_id").and_then(|v| v.as_str()).unwrap_or("");
            let doc = db::get_document(pool, doc_id).await.map_err(|e| JsonRpcError {
                code: -32000,
                message: e.to_string(),
                data: None
            })?;

            Ok(json!({ "document": doc }))
        },
        "count_documents" => {
            let count = db::count_documents(pool).await.map_err(|e| JsonRpcError {
                code: -32000,
                message: e.to_string(),
                data: None
            })?;

            Ok(json!({ "count": count }))
        },
        "list_topics" => {
            let topics = db::list_topics(pool).await.map_err(|e| JsonRpcError {
                code: -32000,
                message: e.to_string(),
                data: None
            })?;

            Ok(json!({ "topics": topics }))
        },
        _ => Err(JsonRpcError {
            code: -32601,
            message: format!("Tool not found: {}", name),
            data: None,
        }),
    }
}

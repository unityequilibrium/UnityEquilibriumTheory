use anyhow::Result;
use fastembed::{TextEmbedding, InitOptions, EmbeddingModel};
use serde::{Deserialize, Serialize};
use sqlx::PgPool;
use std::sync::Arc;
use tokio::sync::OnceCell;

// Global lazy-loaded embedding model to avoid reloading for every request
static EMBEDDING_MODEL: OnceCell<Arc<tokio::sync::Mutex<TextEmbedding>>> = OnceCell::const_new();

async fn get_embedding_model() -> Result<Arc<tokio::sync::Mutex<TextEmbedding>>> {
    EMBEDDING_MODEL.get_or_try_init(|| async {
        // Initialize the BAAI/bge-m3 model (same as Python ingest)
        let model = TextEmbedding::try_new(
            InitOptions::new(EmbeddingModel::BGEM3)
                .with_show_download_progress(true)
        )?;
        Ok(Arc::new(tokio::sync::Mutex::new(model)))
    }).await.cloned()
}

#[derive(Debug, Deserialize)]
pub struct McpQueryRequest {
    /// Text query (will do text search if no embedding provided)
    pub query: String,
    /// Pre-computed embedding vector (optional, for semantic search)
    pub embedding: Option<Vec<f64>>,
    /// Number of results to return
    pub top_k: Option<i64>,
}

#[derive(Debug, Serialize)]
pub struct McpQueryResponse {
    pub results: Vec<McpSearchResult>,
    pub query_type: String,
    pub total: usize,
}

#[derive(Debug, Serialize, sqlx::FromRow)]
pub struct McpSearchResult {
    pub chunk_id: String,
    pub doc_id: String,
    pub text: String,
    pub path: String,
    pub score: f64,
    pub metadata: serde_json::Value,
}

/// MCP Query endpoint - searches UET knowledge base
pub async fn mcp_query(pool: &PgPool, req: McpQueryRequest) -> Result<McpQueryResponse> {
    let top_k = req.top_k.unwrap_or(5);

    // If embedding provided, do semantic search
    if let Some(embedding) = &req.embedding {
        return semantic_search(pool, embedding, top_k).await;
    }

    // Try to generate embedding from text query
    match generate_embedding(&req.query).await {
        Ok(embedding) => {
            // Semantic search with generated embedding
            semantic_search(pool, &embedding, top_k).await
        }
        Err(e) => {
            tracing::warn!("Failed to generate embedding: {}. Falling back to text search.", e);
            // Fallback to text search if model fails
            text_search(pool, &req.query, top_k).await
        }
    }
}

/// Generate embedding using fastembed
async fn generate_embedding(text: &str) -> Result<Vec<f64>> {
    let model = get_embedding_model().await?;
    let mut model_lock = model.lock().await;
    let embeddings = model_lock.embed(vec![text], None)?;

    // Convert f32 vector to f64 for our DB schema
    let first_embedding = embeddings.into_iter().next()
        .ok_or_else(|| anyhow::anyhow!("No embedding generated"))?;

    Ok(first_embedding.into_iter().map(|v| v as f64).collect())
}

/// Semantic search using pgvector
async fn semantic_search(pool: &PgPool, embedding: &[f64], top_k: i64) -> Result<McpQueryResponse> {
    let vector_string = format!(
        "[{}]",
        embedding.iter().map(|f| f.to_string()).collect::<Vec<_>>().join(",")
    );

    let rows = sqlx::query_as::<_, McpSearchResult>(
        r#"
        SELECT
            c.id::text as chunk_id,
            c.doc_id::text as doc_id,
            c.text,
            d.source_path as path,
            (1 - (c.embedding <=> $1::vector))::float8 as score,
            d.metadata
        FROM document_chunks c
        JOIN documents d ON c.doc_id = d.id
        ORDER BY c.embedding <=> $1::vector
        LIMIT $2
        "#
    )
    .bind(&vector_string)
    .bind(top_k)
    .fetch_all(pool)
    .await?;

    let total = rows.len();
    Ok(McpQueryResponse {
        results: rows,
        query_type: "semantic".to_string(),
        total,
    })
}

/// Full-text search using ILIKE
async fn text_search(pool: &PgPool, query: &str, top_k: i64) -> Result<McpQueryResponse> {
    // Create search pattern with wildcards
    let pattern = format!("%{}%", query.to_lowercase());

    let rows = sqlx::query_as::<_, McpSearchResult>(
        r#"
        SELECT
            c.id::text as chunk_id,
            c.doc_id::text as doc_id,
            c.text,
            d.source_path as path,
            (CASE WHEN c.text ILIKE $1 THEN 1.0 ELSE 0.5 END)::float8 as score,
            d.metadata
        FROM document_chunks c
        JOIN documents d ON c.doc_id = d.id
        WHERE c.text ILIKE $1
        ORDER BY score DESC
        LIMIT $2
        "#
    )
    .bind(&pattern)
    .bind(top_k)
    .fetch_all(pool)
    .await?;

    let total = rows.len();
    Ok(McpQueryResponse {
        results: rows,
        query_type: "text".to_string(),
        total,
    })
}

/// Get equation by name/topic (structured query)
pub async fn get_equation(pool: &PgPool, name: &str) -> Result<Option<McpSearchResult>> {
    let pattern = format!("%{}%", name.to_lowercase());

    let row = sqlx::query_as::<_, McpSearchResult>(
        r#"
        SELECT
            c.id::text as chunk_id,
            c.doc_id::text as doc_id,
            c.text,
            d.path,
            1.0 as score,
            d.metadata
        FROM chunks c
        JOIN documents d ON c.doc_id = d.id
        WHERE c.text ILIKE $1
           OR d.metadata->>'title' ILIKE $1
           OR d.metadata->>'equation' ILIKE $1
        LIMIT 1
        "#
    )
    .bind(&pattern)
    .fetch_optional(pool)
    .await?;

    Ok(row)
}

/// List all available topics/documents
pub async fn list_topics(pool: &PgPool) -> Result<Vec<TopicInfo>> {
    let rows = sqlx::query_as::<_, TopicInfo>(
        r#"
        SELECT DISTINCT
            d.path,
            d.metadata->>'title' as title,
            d.metadata->>'type' as doc_type
        FROM documents d
        ORDER BY d.path
        "#
    )
    .fetch_all(pool)
    .await?;

    Ok(rows)
}

#[derive(Debug, Serialize, sqlx::FromRow)]
pub struct TopicInfo {
    pub path: String,
    pub title: Option<String>,
    pub doc_type: Option<String>,
}

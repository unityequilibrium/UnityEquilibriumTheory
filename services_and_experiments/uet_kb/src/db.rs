use sqlx::{postgres::PgPoolOptions, Pool, Postgres, Row};
use uuid::Uuid;
use chrono::Utc;
use anyhow::Result;
use serde::{Serialize, Deserialize};
use serde_json::Value;

#[derive(Debug, Serialize, Deserialize, sqlx::FromRow)]
pub struct Document {
    pub id: Uuid,
    pub path: String,
    pub extracted_text: String,
    pub created_at:  chrono::DateTime<Utc>,
    pub metadata: Value,
}

#[derive(Debug, sqlx::FromRow)]
pub struct Chunk {
    pub id: String,
    pub doc_id: String,
    pub text: String,
    // We don't necessarily need to fetch the embedding back into Rust for basic RAG,
    // but if we did, we'd need a mapping. For search, we just return text.
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SearchResult {
    pub chunk_id: String,
    pub doc_id: String,
    pub text: String,
    pub score: f64,
    pub path: String,
    pub metadata: Value,
}

pub async fn init_db(database_url: &str) -> Result<Pool<Postgres>> {
    let pool = PgPoolOptions::new()
        .max_connections(5)
        .connect(database_url)
        .await?;

    // Enable pgvector extension
    sqlx::query("CREATE EXTENSION IF NOT EXISTS vector")
        .execute(&pool)
        .await?;

    // Create documents table with JSONB metadata
    sqlx::query(
        r#"
        CREATE TABLE IF NOT EXISTS documents (
            id UUID PRIMARY KEY,
            path TEXT NOT NULL,
            extracted_text TEXT,
            created_at TIMESTAMPTZ NOT NULL,
            metadata JSONB DEFAULT '{}'::jsonb
        )
        "#
    )
    .execute(&pool)
    .await?;

    // Create chunks table with Vector(1024) for semantic and Vector(20) for physics
    sqlx::query(
        r#"
        CREATE TABLE IF NOT EXISTS chunks (
            id UUID PRIMARY KEY,
            doc_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
            text TEXT NOT NULL,
            embedding vector(1024),
            physics_vector vector(20)
        )
        "#
    )
    .execute(&pool)
    .await?;

    Ok(pool)
}

pub async fn insert_document(pool: &Pool<Postgres>, id: Option<Uuid>, path: &str, text: &str, metadata: Option<Value>) -> Result<String> {
    // Use provided ID or generate new one
    let id = id.unwrap_or_else(Uuid::new_v4);
    let now = Utc::now();
    let meta = metadata.unwrap_or(serde_json::json!({}));

    sqlx::query(
        r#"
        INSERT INTO documents (id, path, extracted_text, created_at, metadata)
        VALUES ($1, $2, $3, $4, $5)
        "#
    )
    .bind(id)
    .bind(path)
    .bind(text)
    .bind(now)
    .bind(meta)
    .execute(pool)
    .await?;

    Ok(id.to_string())
}

pub async fn insert_chunk(
    pool: &Pool<Postgres>,
    doc_id: &str,
    text: &str,
    semantic_vec: &[f64],
    physics_vec: &[f64]
) -> Result<()> {
    let id = Uuid::new_v4();
    let doc_uuid = Uuid::parse_str(doc_id)?;

    // Format semantic vector
    let sem_vector_string = format!(
        "[{}]",
        semantic_vec.iter().map(|f| f.to_string()).collect::<Vec<_>>().join(",")
    );

    // Format physics vector
    let phys_vector_string = format!(
        "[{}]",
        physics_vec.iter().map(|f| f.to_string()).collect::<Vec<_>>().join(",")
    );

    sqlx::query(
        r#"
        INSERT INTO chunks (id, doc_id, text, embedding, physics_vector)
        VALUES ($1, $2, $3, $4::vector, $5::vector)
        "#
    )
    .bind(id)
    .bind(doc_uuid)
    .bind(text)
    .bind(sem_vector_string)
    .bind(phys_vector_string)
    .execute(pool)
    .await?;

    Ok(())
}

// Search using Cosine Distance (<=> operator)
pub async fn search_similar(pool: &Pool<Postgres>, query_vec: &[f64], top_k: i64) -> Result<Vec<SearchResult>> {
    let vector_string = format!(
        "[{}]",
        query_vec.iter().map(|f| f.to_string()).collect::<Vec<_>>().join(",")
    );

    let rows = sqlx::query(
        r#"
        SELECT c.id, c.doc_id, c.text, d.path, d.metadata, 1 - (c.embedding <=> $1::vector) as similarity
        FROM chunks c
        JOIN documents d ON c.doc_id = d.id
        ORDER BY c.embedding <=> $1::vector
        LIMIT $2
        "#
    )
    .bind(vector_string)
    .bind(top_k)
    .fetch_all(pool)
    .await?;

    let results = rows.into_iter().map(|row| {
        SearchResult {
            chunk_id: row.get::<Uuid, _>("id").to_string(),
            doc_id: row.get::<Uuid, _>("doc_id").to_string(),
            text: row.get("text"),
            path: row.get("path"),
            score: row.get("similarity"),
            metadata: row.get("metadata"),
        }
    }).collect();

    Ok(results)
}

// Search using Physics Vector (Euclidean Distance <->)
pub async fn search_physics(pool: &Pool<Postgres>, query_vec: &[f64], top_k: i64) -> Result<Vec<SearchResult>> {
    let vector_string = format!(
        "[{}]",
        query_vec.iter().map(|f| f.to_string()).collect::<Vec<_>>().join(",")
    );

    let rows = sqlx::query(
        r#"
        SELECT c.id, c.doc_id, c.text, d.path, d.metadata, c.physics_vector <-> $1::vector as distance
        FROM chunks c
        JOIN documents d ON c.doc_id = d.id
        ORDER BY c.physics_vector <-> $1::vector
        LIMIT $2
        "#
    )
    .bind(vector_string)
    .bind(top_k)
    .fetch_all(pool)
    .await?;

    let results = rows.into_iter().map(|row| {
        SearchResult {
            chunk_id: row.get::<Uuid, _>("id").to_string(),
            doc_id: row.get::<Uuid, _>("doc_id").to_string(),
            text: row.get("text"),
            path: row.get("path"),
            score: row.get("distance"),
            metadata: row.get("metadata"),
        }
    }).collect();

    Ok(results)
}

// --- CRUD Operations ---

pub async fn get_document(pool: &Pool<Postgres>, doc_id: &str) -> Result<Option<Document>> {
    let uuid_val = match Uuid::parse_str(doc_id) {
        Ok(u) => u,
        Err(_) => return Ok(None),
    };

    let doc = sqlx::query_as::<_, Document>(
        "SELECT id, path, extracted_text, created_at, metadata FROM documents WHERE id = $1"
    )
    .bind(uuid_val)
    .fetch_optional(pool)
    .await?;

    Ok(doc)
}

pub async fn delete_document(pool: &Pool<Postgres>, doc_id: &str) -> Result<bool> {
    let uuid_val = match Uuid::parse_str(doc_id) {
        Ok(u) => u,
        Err(_) => return Ok(false),
    };

    // Because of ON DELETE CASCADE in chunks table def above, this deletes chunks too.
    let result = sqlx::query("DELETE FROM documents WHERE id = $1")
        .bind(uuid_val)
        .execute(pool)
        .await?;

    Ok(result.rows_affected() > 0)
}

pub async fn count_documents(pool: &Pool<Postgres>) -> Result<i64> {
    let result: (i64,) = sqlx::query_as("SELECT COUNT(*) FROM documents")
        .fetch_one(pool)
        .await?;
    Ok(result.0)
}

pub async fn list_topics(pool: &Pool<Postgres>) -> Result<Vec<String>> {
    // Assuming metadata has a key "topic_id"
    let rows = sqlx::query(
        "SELECT DISTINCT metadata->>'topic_id' as topic FROM documents WHERE metadata->>'topic_id' IS NOT NULL ORDER BY topic"
    )
    .fetch_all(pool)
    .await?;

    let topics = rows.into_iter().map(|r| r.get("topic")).collect();
    Ok(topics)
}

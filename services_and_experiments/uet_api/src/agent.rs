use axum::{
    extract::{Json, State},
    http::StatusCode,
};
use serde::{Deserialize, Serialize};

use crate::handlers::{ApiError, AppState, CurrentUser};
use crate::db;

#[derive(Deserialize)]
pub struct WorkchatRequest {
    pub prompt: String,
    pub source_data: Option<String>, // Document or data to ingest
    pub is_numerical: bool,          // False for semantic/chat, True for calculation
}

#[derive(Serialize)]
pub struct WorkchatResponse {
    pub response: String,
    pub status: String,
    pub work_computed: f64,
}

// Request to Python Semantic Engine
#[derive(Serialize)]
struct PythonChatRequest {
    prompt: String,
    doc_context: Option<String>,
}

#[derive(Deserialize)]
struct PythonChatResponse {
    response: String,
    // equilibrium_data omitted for brevity, or we can parse it
    work_computed: f64,
}

#[derive(Serialize, Deserialize)]
pub struct IngestRequest {
    pub doc_id: String,
    pub text: String,
}

#[derive(Serialize, Deserialize)]
pub struct IngestResponse {
    pub status: String,
    pub message: String,
}

pub async fn ingest_handler(
    State(_state): State<AppState>,
    Json(req): Json<IngestRequest>,
) -> Result<Json<IngestResponse>, ApiError> {
    let client = reqwest::Client::new();
    let python_url = "http://localhost:8001/ingest";

    let res = client.post(python_url)
        .json(&req)
        .send()
        .await
        .map_err(|e| ApiError {
            status: StatusCode::INTERNAL_SERVER_ERROR,
            message: format!("Failed to contact Semantic Engine: {}", e),
        })?;

    let py_res: IngestResponse = res.json()
        .await
        .map_err(|e| ApiError {
            status: StatusCode::INTERNAL_SERVER_ERROR,
            message: format!("Invalid response from Semantic Engine: {}", e),
        })?;

    Ok(Json(py_res))
}

pub async fn workchat_handler(
    State(_state): State<AppState>,
    Json(req): Json<WorkchatRequest>,
) -> Result<Json<WorkchatResponse>, ApiError> {

    // In a real mining scenario, this would create a task in the DB,
    // wait for miners to pick it up, and return the result.
    // For this bridge, we'll directly call the Python Agent API (Port 8001) as a "mock" miner.

    let client = reqwest::Client::new();

    let python_url = "http://localhost:8001/chat";
    let py_req = PythonChatRequest {
        prompt: req.prompt.clone(),
        doc_context: req.source_data.clone(),
    };

    let res = client.post(python_url)
        .json(&py_req)
        .send()
        .await
        .map_err(|e| ApiError {
            status: StatusCode::INTERNAL_SERVER_ERROR,
            message: format!("Failed to contact Semantic Engine: {}", e),
        })?;

    let py_res: PythonChatResponse = res.json()
        .await
        .map_err(|e| ApiError {
            status: StatusCode::INTERNAL_SERVER_ERROR,
            message: format!("Invalid response from Semantic Engine: {}", e),
        })?;

    // Removed DB record_usage temporarily to fix connection pool crash
    // when PostgreSQL is not running in Docker.

    Ok(Json(WorkchatResponse {
        response: py_res.response,
        status: "Equilibrium Found".to_string(),
        work_computed: py_res.work_computed,
    }))
}

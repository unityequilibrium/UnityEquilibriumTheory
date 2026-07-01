mod agent;
mod auth;
mod config;
mod db;
mod email;
mod handlers;
mod mcp;
mod models;
mod oauth;

use axum::{
    routing::{get, post},
    Router,
};
use sqlx::postgres::PgPoolOptions;
use std::net::SocketAddr;
use tower_http::cors::{Any, CorsLayer};
use tracing::info;

use crate::config::CONFIG;
use crate::handlers::AppState;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt()
        .with_env_filter(tracing_subscriber::EnvFilter::from_default_env())
        .init();

    dotenvy::dotenv().ok();

    info!("Connecting to database: {}", CONFIG.database_url);

    let pool = PgPoolOptions::new()
        .max_connections(10)
        .connect(&CONFIG.database_url)
        .await?;

    info!("Running migrations...");
    sqlx::migrate!("./migrations")
        .run(&pool)
        .await?;

    let oauth_clients = oauth::OAuthClients::new();
    let email_service = email::EmailService::new();

    let state = AppState {
        pool,
        oauth: oauth_clients,
        email: email_service,
    };

    // CORS for frontend
    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    // Public routes (no auth required)
    let public_routes = Router::new()
        .route("/api/health", get(health_check))
        .route("/api/auth/register", post(handlers::register))
        .route("/api/auth/login", post(handlers::login))
        .route("/api/auth/refresh", post(handlers::refresh_token))
        .route("/api/auth/verify-email", post(handlers::verify_email))
        .route("/api/auth/request-reset", post(handlers::request_password_reset))
        .route("/api/auth/reset-password", post(handlers::reset_password))
        .route("/api/auth/oauth/google", get(handlers::google_auth))
        .route("/api/auth/oauth/google/callback", get(handlers::google_callback))
        .route("/api/auth/oauth/github", get(handlers::github_auth))
        .route("/api/auth/oauth/github/callback", get(handlers::github_callback))
        .route("/api/workchat", post(agent::workchat_handler))
        .route("/api/workchat/ingest", post(agent::ingest_handler));

    // Protected routes (auth middleware applied)
    let protected_routes = Router::new()
        .route("/api/auth/logout", post(handlers::logout))
        .route("/api/auth/me", get(handlers::get_me))
        .route("/api/auth/quota", get(handlers::get_quota))
        .route("/api/auth/api-keys", get(handlers::list_keys).post(handlers::create_key))
        .route("/api/auth/api-keys/:id", axum::routing::delete(handlers::delete_key))
        .route("/api/mcp/query", post(handlers::mcp_query))
        .route("/api/mcp/equation/:name", get(handlers::mcp_get_equation))
        .route("/api/mcp/topics", get(handlers::mcp_list_topics));

    let app = public_routes
        .merge(protected_routes)
        .layer(cors)
        .with_state(state);

    let addr = SocketAddr::from(([0, 0, 0, 0], 3001));
    info!("UET API listening on {}", addr);

    let listener = tokio::net::TcpListener::bind(&addr).await?;
    axum::serve(listener, app).await?;

    Ok(())
}

async fn health_check() -> &'static str {
    "OK"
}

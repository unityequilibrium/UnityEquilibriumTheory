use once_cell::sync::Lazy;
use std::env;

pub struct Config {
    pub database_url: String,
    pub jwt_secret: String,
    pub jwt_expiry_hours: i64,
    pub refresh_expiry_days: i64,
    pub google_client_id: String,
    pub google_client_secret: String,
    pub github_client_id: String,
    pub github_client_secret: String,
    pub oauth_redirect_url: String,
    pub frontend_url: String,
}

pub static CONFIG: Lazy<Config> = Lazy::new(|| {
    dotenvy::dotenv().ok();

    Config {
        database_url: env::var("DATABASE_URL")
            .unwrap_or_else(|_| "postgres://postgres:postgres@localhost:5433/uet_kb".to_string()),
        jwt_secret: env::var("JWT_SECRET")
            .unwrap_or_else(|_| "dev-secret-change-in-production".to_string()),
        jwt_expiry_hours: env::var("JWT_EXPIRY_HOURS")
            .unwrap_or_else(|_| "24".to_string())
            .parse()
            .unwrap_or(24),
        refresh_expiry_days: env::var("REFRESH_EXPIRY_DAYS")
            .unwrap_or_else(|_| "30".to_string())
            .parse()
            .unwrap_or(30),
        google_client_id: env::var("GOOGLE_CLIENT_ID")
            .unwrap_or_default(),
        google_client_secret: env::var("GOOGLE_CLIENT_SECRET")
            .unwrap_or_default(),
        github_client_id: env::var("GITHUB_CLIENT_ID")
            .unwrap_or_default(),
        github_client_secret: env::var("GITHUB_CLIENT_SECRET")
            .unwrap_or_default(),
        oauth_redirect_url: env::var("OAUTH_REDIRECT_URL")
            .unwrap_or_else(|_| "http://localhost:3000/auth/callback".to_string()),
        frontend_url: env::var("FRONTEND_URL")
            .unwrap_or_else(|_| "http://localhost:3000".to_string()),
    }
});

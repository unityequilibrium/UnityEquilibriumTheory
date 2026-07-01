use axum::{
    async_trait,
    extract::{FromRequestParts, Json, Path, Query, State},
    http::{header, request::Parts, StatusCode},
    middleware::Next,
    response::{IntoResponse, Response},
    Router,
};
use axum::http::Request;
use axum_extra::{
    headers::{authorization::Bearer, Authorization},
    TypedHeader,
};
use serde::{Deserialize, Serialize};
use sqlx::PgPool;
use uuid::Uuid;

use crate::auth::{validate_access_token, AuthError};
use crate::config::CONFIG;
use crate::db;
use crate::email::EmailService;
use crate::mcp;
use crate::models::*;
use crate::oauth::{self, OAuthClients};

pub fn auth_routes() -> Router<AppState> {
    Router::new()
        .route("/register", axum::routing::post(register))
        .route("/login", axum::routing::post(login))
        .route("/refresh", axum::routing::post(refresh_token))
        .route("/logout", axum::routing::post(logout))
        .route("/verify-email", axum::routing::post(verify_email))
        .route("/request-reset", axum::routing::post(request_password_reset))
        .route("/reset-password", axum::routing::post(reset_password))
        .route("/oauth/google", axum::routing::get(google_auth))
        .route("/oauth/google/callback", axum::routing::get(google_callback))
        .route("/oauth/github", axum::routing::get(github_auth))
        .route("/oauth/github/callback", axum::routing::get(github_callback))
        .route("/me", axum::routing::get(get_me))
        .route("/quota", axum::routing::get(get_quota))
        .route("/api-keys", axum::routing::get(list_keys))
        .route("/api-keys", axum::routing::post(create_key))
        .route("/api-keys/:id", axum::routing::delete(delete_key))
}

#[derive(Clone)]
pub struct AppState {
    pub pool: PgPool,
    pub oauth: OAuthClients,
    pub email: EmailService,
}

// ==================== Error Handling ====================

#[derive(Debug)]
pub struct ApiError {
    pub status: StatusCode,
    pub message: String,
}

impl IntoResponse for ApiError {
    fn into_response(self) -> Response {
        let body = Json(serde_json::json!({
            "error": self.message
        }));
        (self.status, body).into_response()
    }
}

impl From<AuthError> for ApiError {
    fn from(err: AuthError) -> Self {
        match err {
            AuthError::InvalidCredentials => ApiError {
                status: StatusCode::UNAUTHORIZED,
                message: "Invalid credentials".to_string(),
            },
            AuthError::UserExists => ApiError {
                status: StatusCode::CONFLICT,
                message: "User already exists".to_string(),
            },
            AuthError::InvalidToken | AuthError::TokenExpired => ApiError {
                status: StatusCode::UNAUTHORIZED,
                message: "Invalid or expired token".to_string(),
            },
            _ => ApiError {
                status: StatusCode::INTERNAL_SERVER_ERROR,
                message: err.to_string(),
            },
        }
    }
}

impl From<anyhow::Error> for ApiError {
    fn from(err: anyhow::Error) -> Self {
        ApiError {
            status: StatusCode::INTERNAL_SERVER_ERROR,
            message: err.to_string(),
        }
    }
}

impl From<sqlx::Error> for ApiError {
    fn from(err: sqlx::Error) -> Self {
        if let sqlx::Error::Database(db_err) = &err {
            if db_err.constraint().map(|c| c.contains("email")).unwrap_or(false) {
                return ApiError {
                    status: StatusCode::CONFLICT,
                    message: "Email already registered".to_string(),
                };
            }
        }
        ApiError {
            status: StatusCode::INTERNAL_SERVER_ERROR,
            message: "Database error".to_string(),
        }
    }
}

// ==================== Auth Handlers ====================

#[derive(Deserialize)]
pub struct RefreshRequest {
    refresh_token: String,
}

pub async fn register(
    State(state): State<AppState>,
    Json(req): Json<RegisterRequest>,
) -> Result<Json<serde_json::Value>, ApiError> {
    // Check if user exists
    if db::get_user_by_email(&state.pool, &req.email).await?.is_some() {
        return Err(ApiError {
            status: StatusCode::CONFLICT,
            message: "Email already registered".to_string(),
        });
    }

    let user = db::create_user(&state.pool, &req.email, &req.password, req.display_name.as_deref()).await?;
    db::init_user_quota(&state.pool, user.id).await?;

    // Generate verification token
    let verification_token = crate::auth::generate_refresh_token(); // Reuse as random token
    db::set_verification_token(&state.pool, user.id, &verification_token).await?;

    // Send verification email (non-fatal)
    let verify_url = format!("{}/auth/verify?token={}", CONFIG.frontend_url, verification_token);
    let username = user.display_name.as_deref().unwrap_or("there");
    if let Err(e) = state.email.send_verification_email(&user.email, username, &verify_url).await {
        tracing::warn!("Failed to send verification email: {}", e);
    }

    db::log_audit(&state.pool, Some(user.id), "register", None, None, None).await?;

    Ok(Json(serde_json::json!({
        "message": "Registration successful. Please check your email to verify your account.",
        "email": user.email
    })))
}

pub async fn login(
    State(state): State<AppState>,
    Json(req): Json<LoginRequest>,
) -> Result<Json<AuthResponse>, ApiError> {
    let (user, access_token, refresh_token) = db::authenticate_user(&state.pool, &req.email, &req.password)
        .await?
        .ok_or_else(|| ApiError {
            status: StatusCode::UNAUTHORIZED,
            message: "Invalid credentials".to_string(),
        })?;

    // Check if email is verified (skip for OAuth users without password)
    if user.password_hash.is_some() && !user.is_verified {
        return Err(ApiError {
            status: StatusCode::FORBIDDEN,
            message: "Please verify your email before logging in".to_string(),
        });
    }

    db::log_audit(&state.pool, Some(user.id), "login", None, None, None).await?;

    Ok(Json(AuthResponse {
        access_token,
        refresh_token,
        expires_in: CONFIG.jwt_expiry_hours * 3600,
        user: user.into(),
    }))
}

pub async fn refresh_token(
    State(state): State<AppState>,
    Json(req): Json<RefreshRequest>,
) -> Result<Json<AuthResponse>, ApiError> {
    let user = db::validate_refresh_token(&state.pool, &req.refresh_token)
        .await?
        .ok_or_else(|| ApiError {
            status: StatusCode::UNAUTHORIZED,
            message: "Invalid refresh token".to_string(),
        })?;

    db::revoke_refresh_token(&state.pool, &req.refresh_token).await?;

    let access_token = crate::auth::generate_access_token(&user)?;
    let refresh_token = crate::auth::generate_refresh_token();
    let refresh_hash = crate::auth::hash_token(&refresh_token);

    let expires_at = chrono::Utc::now() + chrono::Duration::days(CONFIG.refresh_expiry_days);
    sqlx::query(
        "INSERT INTO refresh_tokens (user_id, token_hash, expires_at) VALUES ($1, $2, $3)",
    )
    .bind(user.id)
    .bind(&refresh_hash)
    .bind(expires_at)
    .execute(&state.pool)
    .await?;

    Ok(Json(AuthResponse {
        access_token,
        refresh_token,
        expires_in: CONFIG.jwt_expiry_hours * 3600,
        user: user.into(),
    }))
}

pub async fn logout(
    State(state): State<AppState>,
    user: CurrentUser,
    Json(req): Json<RefreshRequest>,
) -> Result<StatusCode, ApiError> {
    db::revoke_refresh_token(&state.pool, &req.refresh_token).await?;
    db::log_audit(&state.pool, Some(user.0), "logout", None, None, None).await?;
    Ok(StatusCode::NO_CONTENT)
}

// ==================== Email Verification ====================

pub async fn verify_email(
    State(state): State<AppState>,
    Json(req): Json<VerifyEmailRequest>,
) -> Result<Json<AuthResponse>, ApiError> {
    let user = db::verify_email(&state.pool, &req.token)
        .await?
        .ok_or_else(|| ApiError {
            status: StatusCode::BAD_REQUEST,
            message: "Invalid or expired verification token".to_string(),
        })?;

    // Send welcome email
    let username = user.display_name.as_deref().unwrap_or("there");
    state.email.send_welcome_email(&user.email, username).await?;

    // Generate tokens for auto-login
    let access_token = crate::auth::generate_access_token(&user)?;
    let refresh_token = crate::auth::generate_refresh_token();
    let refresh_hash = crate::auth::hash_token(&refresh_token);

    let expires_at = chrono::Utc::now() + chrono::Duration::days(CONFIG.refresh_expiry_days);
    sqlx::query(
        "INSERT INTO refresh_tokens (user_id, token_hash, expires_at) VALUES ($1, $2, $3)",
    )
    .bind(user.id)
    .bind(&refresh_hash)
    .bind(expires_at)
    .execute(&state.pool)
    .await?;

    db::log_audit(&state.pool, Some(user.id), "email_verified", None, None, None).await?;

    Ok(Json(AuthResponse {
        access_token,
        refresh_token,
        expires_in: CONFIG.jwt_expiry_hours * 3600,
        user: user.into(),
    }))
}

pub async fn request_password_reset(
    State(state): State<AppState>,
    Json(req): Json<RequestResetRequest>,
) -> Result<Json<serde_json::Value>, ApiError> {
    // Generate reset token
    let reset_token = crate::auth::generate_refresh_token();

    // Try to set reset token (returns None if email not found)
    let user = db::set_password_reset_token(&state.pool, &req.email, &reset_token).await?;

    if let Some(user) = user {
        // Send reset email
        let reset_url = format!("{}/auth/reset?token={}", CONFIG.frontend_url, reset_token);
        let username = user.display_name.as_deref().unwrap_or("there");
        if let Err(e) = state.email.send_password_reset_email(&user.email, username, &reset_url).await {
            tracing::warn!("Failed to send password reset email: {}", e);
        }

        db::log_audit(&state.pool, Some(user.id), "password_reset_requested", None, None, None).await?;
    }

    // Always return success to prevent email enumeration
    Ok(Json(serde_json::json!({
        "message": "If an account exists with this email, a reset link has been sent."
    })))
}

pub async fn reset_password(
    State(state): State<AppState>,
    Json(req): Json<ResetPasswordRequest>,
) -> Result<Json<AuthResponse>, ApiError> {
    // Validate password strength
    if req.new_password.len() < 8 {
        return Err(ApiError {
            status: StatusCode::BAD_REQUEST,
            message: "Password must be at least 8 characters".to_string(),
        });
    }

    let password_hash = crate::auth::hash_password(&req.new_password)?;

    let user = db::reset_password(&state.pool, &req.token, &password_hash)
        .await?
        .ok_or_else(|| ApiError {
            status: StatusCode::BAD_REQUEST,
            message: "Invalid or expired reset token".to_string(),
        })?;

    // Generate tokens for auto-login
    let access_token = crate::auth::generate_access_token(&user)?;
    let refresh_token = crate::auth::generate_refresh_token();
    let refresh_hash = crate::auth::hash_token(&refresh_token);

    let expires_at = chrono::Utc::now() + chrono::Duration::days(CONFIG.refresh_expiry_days);
    sqlx::query(
        "INSERT INTO refresh_tokens (user_id, token_hash, expires_at) VALUES ($1, $2, $3)",
    )
    .bind(user.id)
    .bind(&refresh_hash)
    .bind(expires_at)
    .execute(&state.pool)
    .await?;

    db::log_audit(&state.pool, Some(user.id), "password_reset", None, None, None).await?;

    Ok(Json(AuthResponse {
        access_token,
        refresh_token,
        expires_in: CONFIG.jwt_expiry_hours * 3600,
        user: user.into(),
    }))
}

// ==================== OAuth Handlers ====================

#[derive(Deserialize)]
pub struct CallbackQuery {
    code: String,
    state: String,
}

pub async fn google_auth(
    State(state): State<AppState>,
) -> Result<Json<oauth::OAuthUrl>, ApiError> {
    let client = state.oauth.google.as_ref().ok_or_else(|| ApiError {
        status: StatusCode::SERVICE_UNAVAILABLE,
        message: "Google OAuth not configured".to_string(),
    })?;

    Ok(Json(oauth::get_google_auth_url(client)))
}

pub async fn google_callback(
    State(state): State<AppState>,
    Query(query): Query<CallbackQuery>,
) -> Result<Response, ApiError> {
    let client = state.oauth.google.as_ref().ok_or_else(|| ApiError {
        status: StatusCode::SERVICE_UNAVAILABLE,
        message: "Google OAuth not configured".to_string(),
    })?;

    let user_info = oauth::exchange_google_code(client, &query.code).await?;

    let user = db::find_or_create_oauth_user(
        &state.pool,
        "google",
        &user_info.id,
        &user_info.email,
        user_info.name.as_deref(),
        user_info.picture.as_deref(),
    ).await?;

    db::init_user_quota(&state.pool, user.id).await?;

    let access_token = crate::auth::generate_access_token(&user)?;
    let refresh_token = crate::auth::generate_refresh_token();
    let refresh_hash = crate::auth::hash_token(&refresh_token);

    let expires_at = chrono::Utc::now() + chrono::Duration::days(CONFIG.refresh_expiry_days);
    sqlx::query(
        "INSERT INTO refresh_tokens (user_id, token_hash, expires_at) VALUES ($1, $2, $3)",
    )
    .bind(user.id)
    .bind(&refresh_hash)
    .bind(expires_at)
    .execute(&state.pool)
    .await?;

    // Redirect to frontend with tokens
    let redirect_url = format!(
        "{}/auth/callback?access_token={}&refresh_token={}",
        CONFIG.frontend_url, access_token, refresh_token
    );

    let response = Response::builder()
        .status(StatusCode::FOUND)
        .header(header::LOCATION, redirect_url)
        .body(axum::body::Body::empty())
        .unwrap();
    Ok(response)
}

pub async fn github_auth(
    State(state): State<AppState>,
) -> Result<Json<oauth::OAuthUrl>, ApiError> {
    let client = state.oauth.github.as_ref().ok_or_else(|| ApiError {
        status: StatusCode::SERVICE_UNAVAILABLE,
        message: "GitHub OAuth not configured".to_string(),
    })?;

    Ok(Json(oauth::get_github_auth_url(client)))
}

pub async fn github_callback(
    State(state): State<AppState>,
    Query(query): Query<CallbackQuery>,
) -> Result<Response, ApiError> {
    let client = state.oauth.github.as_ref().ok_or_else(|| ApiError {
        status: StatusCode::SERVICE_UNAVAILABLE,
        message: "GitHub OAuth not configured".to_string(),
    })?;

    let user_info = oauth::exchange_github_code(client, &query.code).await?;

    // GitHub may not return email directly, use login as fallback
    let email = user_info.email.clone().unwrap_or_else(|| format!("{}@github", user_info.login));

    let user = db::find_or_create_oauth_user(
        &state.pool,
        "github",
        &user_info.id.to_string(),
        &email,
        Some(&user_info.login),
        user_info.avatar_url.as_deref(),
    ).await?;

    db::init_user_quota(&state.pool, user.id).await?;

    let access_token = crate::auth::generate_access_token(&user)?;
    let refresh_token = crate::auth::generate_refresh_token();
    let refresh_hash = crate::auth::hash_token(&refresh_token);

    let expires_at = chrono::Utc::now() + chrono::Duration::days(CONFIG.refresh_expiry_days);
    sqlx::query(
        "INSERT INTO refresh_tokens (user_id, token_hash, expires_at) VALUES ($1, $2, $3)",
    )
    .bind(user.id)
    .bind(&refresh_hash)
    .bind(expires_at)
    .execute(&state.pool)
    .await?;

    let redirect_url = format!(
        "{}/auth/callback?access_token={}&refresh_token={}",
        CONFIG.frontend_url, access_token, refresh_token
    );

    let response = Response::builder()
        .status(StatusCode::FOUND)
        .header(header::LOCATION, redirect_url)
        .body(axum::body::Body::empty())
        .unwrap();
    Ok(response)
}

// ==================== User Handlers ====================

#[derive(Clone)]
pub struct CurrentUser(pub Uuid);

#[async_trait]
impl<S> FromRequestParts<S> for CurrentUser
where
    S: Send + Sync,
{
    type Rejection = ApiError;

    async fn from_request_parts(parts: &mut Parts, _state: &S) -> Result<Self, Self::Rejection> {
        use axum::RequestPartsExt;
        let TypedHeader(bearer) = parts
            .extract::<TypedHeader<Authorization<Bearer>>>()
            .await
            .map_err(|_| ApiError {
                status: StatusCode::UNAUTHORIZED,
                message: "Missing or invalid Authorization header".to_string(),
            })?;

        let claims = validate_access_token(bearer.token()).map_err(|_| ApiError {
            status: StatusCode::UNAUTHORIZED,
            message: "Invalid or expired token".to_string(),
        })?;

        let user_id = Uuid::parse_str(&claims.sub).map_err(|_| ApiError {
            status: StatusCode::UNAUTHORIZED,
            message: "Invalid token subject".to_string(),
        })?;

        Ok(CurrentUser(user_id))
    }
}

pub async fn auth_middleware(
    TypedHeader(bearer): TypedHeader<Authorization<Bearer>>,
    request: Request<axum::body::Body>,
    next: Next,
) -> Result<Response, ApiError> {
    let _claims = validate_access_token(bearer.token()).map_err(|_| ApiError {
        status: StatusCode::UNAUTHORIZED,
        message: "Invalid or expired token".to_string(),
    })?;
    Ok(next.run(request).await)
}

pub async fn get_me(
    user: CurrentUser,
    State(state): State<AppState>,
) -> Result<Json<UserPublic>, ApiError> {
    let user = db::get_user_by_id(&state.pool, user.0)
        .await?
        .ok_or_else(|| ApiError {
            status: StatusCode::NOT_FOUND,
            message: "User not found".to_string(),
        })?;

    Ok(Json(user.into()))
}

pub async fn get_quota(
    user: CurrentUser,
    State(state): State<AppState>,
) -> Result<Json<QuotaResponse>, ApiError> {
    let (quota, plan) = db::get_user_quota(&state.pool, user.0)
        .await?
        .ok_or_else(|| ApiError {
            status: StatusCode::NOT_FOUND,
            message: "Quota not found".to_string(),
        })?;

    Ok(Json(QuotaResponse {
        tokens_used: quota.tokens_used,
        tokens_limit: plan.token_limit,
        requests_used: quota.requests_used,
        requests_limit: plan.request_limit,
        period_start: quota.period_start,
        plan_name: plan.name,
    }))
}

// ==================== API Key Handlers ====================

#[derive(Deserialize)]
pub struct CreateKeyRequest {
    name: Option<String>,
}

#[derive(Serialize)]
pub struct CreateKeyResponse {
    key: String,
    id: Uuid,
    prefix: String,
    name: Option<String>,
    created_at: chrono::DateTime<chrono::Utc>,
}

pub async fn list_keys(
    user: CurrentUser,
    State(state): State<AppState>,
) -> Result<Json<Vec<ApiKey>>, ApiError> {
    let keys = db::list_api_keys(&state.pool, user.0).await?;
    Ok(Json(keys))
}

pub async fn create_key(
    user: CurrentUser,
    State(state): State<AppState>,
    Json(req): Json<CreateKeyRequest>,
) -> Result<Json<CreateKeyResponse>, ApiError> {
    let (key, api_key) = db::create_api_key(&state.pool, user.0, req.name.as_deref()).await?;

    db::log_audit(&state.pool, Some(user.0), "api_key_created", None, None, None).await?;

    Ok(Json(CreateKeyResponse {
        key,
        id: api_key.id,
        prefix: api_key.prefix,
        name: api_key.name,
        created_at: api_key.created_at,
    }))
}

pub async fn delete_key(
    user: CurrentUser,
    State(state): State<AppState>,
    Path(key_id): Path<Uuid>,
) -> Result<StatusCode, ApiError> {
    let deleted = db::delete_api_key(&state.pool, user.0, key_id).await?;

    if deleted {
        db::log_audit(&state.pool, Some(user.0), "api_key_deleted", None, None, None).await?;
        Ok(StatusCode::NO_CONTENT)
    } else {
        Err(ApiError {
            status: StatusCode::NOT_FOUND,
            message: "API key not found".to_string(),
        })
    }
}

// ==================== MCP Query Handlers ====================

pub async fn mcp_query(
    user: CurrentUser,
    State(state): State<AppState>,
    Json(req): Json<mcp::McpQueryRequest>,
) -> Result<Json<mcp::McpQueryResponse>, ApiError> {
    // Check quota
    let (quota, plan) = db::get_user_quota(&state.pool, user.0)
        .await?
        .ok_or_else(|| ApiError {
            status: StatusCode::FORBIDDEN,
            message: "No quota found".to_string(),
        })?;

    if quota.requests_used >= plan.request_limit {
        return Err(ApiError {
            status: StatusCode::TOO_MANY_REQUESTS,
            message: "Quota exceeded. Please upgrade your plan.".to_string(),
        });
    }

    // Execute query
    let response = mcp::mcp_query(&state.pool, req).await?;

    // Record usage
    db::record_usage(
        &state.pool,
        user.0,
        "mcp_query",
        response.total as i64,
        Some(serde_json::json!({ "query_type": response.query_type })),
    ).await?;

    Ok(Json(response))
}

pub async fn mcp_get_equation(
    user: CurrentUser,
    State(state): State<AppState>,
    Path(name): Path<String>,
) -> Result<Json<mcp::McpSearchResult>, ApiError> {
    let result = mcp::get_equation(&state.pool, &name)
        .await?
        .ok_or_else(|| ApiError {
            status: StatusCode::NOT_FOUND,
            message: format!("Equation '{}' not found", name),
        })?;

    // Record usage
    db::record_usage(&state.pool, user.0, "mcp_get_equation", 1, None).await?;

    Ok(Json(result))
}

pub async fn mcp_list_topics(
    user: CurrentUser,
    State(state): State<AppState>,
) -> Result<Json<Vec<mcp::TopicInfo>>, ApiError> {
    let topics = mcp::list_topics(&state.pool).await?;
    Ok(Json(topics))
}

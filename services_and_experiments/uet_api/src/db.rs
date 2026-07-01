use anyhow::Result;
use chrono::{Duration, Utc};
use sqlx::{PgPool, Postgres, QueryBuilder};
use uuid::Uuid;

use crate::auth::{hash_password, hash_token, verify_password, generate_access_token, generate_refresh_token};
use crate::config::CONFIG;
use crate::models::*;

// ==================== User Operations ====================

pub async fn create_user(
    pool: &PgPool,
    email: &str,
    password: &str,
    display_name: Option<&str>,
) -> Result<User> {
    let password_hash = hash_password(password)?;
    let now = Utc::now();
    let id = Uuid::new_v4();

    sqlx::query_as::<_, User>(
        r#"
        INSERT INTO users (id, email, password_hash, display_name, created_at, updated_at)
        VALUES ($1, $2, $3, $4, $5, $5)
        RETURNING *
        "#,
    )
    .bind(id)
    .bind(email)
    .bind(&password_hash)
    .bind(display_name)
    .bind(now)
    .fetch_one(pool)
    .await
    .map_err(Into::into)
}

pub async fn get_user_by_email(pool: &PgPool, email: &str) -> Result<Option<User>> {
    let user = sqlx::query_as::<_, User>(
        "SELECT * FROM users WHERE email = $1"
    )
    .bind(email)
    .fetch_optional(pool)
    .await?;

    Ok(user)
}

pub async fn get_user_by_id(pool: &PgPool, id: Uuid) -> Result<Option<User>> {
    let user = sqlx::query_as::<_, User>(
        "SELECT * FROM users WHERE id = $1"
    )
    .bind(id)
    .fetch_optional(pool)
    .await?;

    Ok(user)
}

// ==================== Auth Operations ====================

pub async fn authenticate_user(
    pool: &PgPool,
    email: &str,
    password: &str,
) -> Result<Option<(User, String, String)>> {
    let user = match get_user_by_email(pool, email).await? {
        Some(u) => u,
        None => return Ok(None),
    };

    let hash = match &user.password_hash {
        Some(h) => h,
        None => return Ok(None),
    };

    if !verify_password(password, hash)? {
        return Ok(None);
    }

    let access_token = generate_access_token(&user)?;
    let refresh_token = generate_refresh_token();
    let refresh_hash = hash_token(&refresh_token);

    // Store refresh token
    let expires_at = Utc::now() + Duration::days(CONFIG.refresh_expiry_days);
    sqlx::query(
        r#"
        INSERT INTO refresh_tokens (user_id, token_hash, expires_at)
        VALUES ($1, $2, $3)
        "#,
    )
    .bind(user.id)
    .bind(&refresh_hash)
    .bind(expires_at)
    .execute(pool)
    .await?;

    Ok(Some((user, access_token, refresh_token)))
}

pub async fn validate_refresh_token(pool: &PgPool, token: &str) -> Result<Option<User>> {
    let hash = hash_token(token);

    let rt = sqlx::query_as::<_, RefreshToken>(
        "SELECT * FROM refresh_tokens WHERE token_hash = $1 AND revoked = false AND expires_at > NOW()"
    )
    .bind(&hash)
    .fetch_optional(pool)
    .await?;

    match rt {
        Some(rt) => get_user_by_id(pool, rt.user_id).await,
        None => Ok(None),
    }
}

pub async fn revoke_refresh_token(pool: &PgPool, token: &str) -> Result<()> {
    let hash = hash_token(token);
    sqlx::query(
        "UPDATE refresh_tokens SET revoked = true WHERE token_hash = $1"
    )
    .bind(&hash)
    .execute(pool)
    .await?;
    Ok(())
}

// ==================== OAuth Operations ====================

pub async fn find_or_create_oauth_user(
    pool: &PgPool,
    provider: &str,
    provider_id: &str,
    email: &str,
    name: Option<&str>,
    avatar: Option<&str>,
) -> Result<User> {
    // Check if OAuth identity exists
    let existing = sqlx::query_as::<_, OAuthIdentity>(
        "SELECT * FROM oauth_identities WHERE provider = $1 AND provider_id = $2"
    )
    .bind(provider)
    .bind(provider_id)
    .fetch_optional(pool)
    .await?;

    if let Some(identity) = existing {
        return get_user_by_id(pool, identity.user_id)
            .await?
            .ok_or_else(|| anyhow::anyhow!("User not found"));
    }

    // Check if user with this email exists
    let existing_user = get_user_by_email(pool, email).await?;

    let user = if let Some(user) = existing_user {
        // Link OAuth to existing user
        sqlx::query(
            r#"
            INSERT INTO oauth_identities (user_id, provider, provider_id, provider_email, provider_name, provider_avatar)
            VALUES ($1, $2, $3, $4, $5, $6)
            "#,
        )
        .bind(user.id)
        .bind(provider)
        .bind(provider_id)
        .bind(email)
        .bind(name)
        .bind(avatar)
        .execute(pool)
        .await?;

        user
    } else {
        // Create new user
        let now = Utc::now();
        let id = Uuid::new_v4();

        let user = sqlx::query_as::<_, User>(
            r#"
            INSERT INTO users (id, email, display_name, avatar_url, is_verified, created_at, updated_at)
            VALUES ($1, $2, $3, $4, true, $5, $5)
            RETURNING *
            "#,
        )
        .bind(id)
        .bind(email)
        .bind(name)
        .bind(avatar)
        .bind(now)
        .fetch_one(pool)
        .await?;

        // Create OAuth identity
        sqlx::query(
            r#"
            INSERT INTO oauth_identities (user_id, provider, provider_id, provider_email, provider_name, provider_avatar)
            VALUES ($1, $2, $3, $4, $5, $6)
            "#,
        )
        .bind(user.id)
        .bind(provider)
        .bind(provider_id)
        .bind(email)
        .bind(name)
        .bind(avatar)
        .execute(pool)
        .await?;

        user
    };

    Ok(user)
}

// ==================== API Key Operations ====================

pub async fn create_api_key(pool: &PgPool, user_id: Uuid, name: Option<&str>) -> Result<(String, ApiKey)> {
    let (key, prefix, key_hash) = crate::auth::generate_api_key();

    let api_key = sqlx::query_as::<_, ApiKey>(
        r#"
        INSERT INTO api_keys (user_id, key_hash, name, prefix)
        VALUES ($1, $2, $3, $4)
        RETURNING *
        "#,
    )
    .bind(user_id)
    .bind(&key_hash)
    .bind(name)
    .bind(&prefix)
    .fetch_one(pool)
    .await?;

    Ok((key, api_key))
}

pub async fn list_api_keys(pool: &PgPool, user_id: Uuid) -> Result<Vec<ApiKey>> {
    let keys = sqlx::query_as::<_, ApiKey>(
        "SELECT * FROM api_keys WHERE user_id = $1 ORDER BY created_at DESC"
    )
    .bind(user_id)
    .fetch_all(pool)
    .await?;

    Ok(keys)
}

pub async fn delete_api_key(pool: &PgPool, user_id: Uuid, key_id: Uuid) -> Result<bool> {
    let result = sqlx::query(
        "DELETE FROM api_keys WHERE id = $1 AND user_id = $2"
    )
    .bind(key_id)
    .bind(user_id)
    .execute(pool)
    .await?;

    Ok(result.rows_affected() > 0)
}

// ==================== Quota Operations ====================

#[derive(sqlx::FromRow)]
pub struct QuotaWithPlan {
    pub user_id: Uuid,
    pub plan_id: Uuid,
    pub tokens_used: i64,
    pub requests_used: i32,
    pub period_start: chrono::DateTime<Utc>,
    pub updated_at: chrono::DateTime<Utc>,
    pub p_id: Uuid,
    pub plan_name: String,
    pub token_limit: i64,
    pub request_limit: i32,
    pub price_monthly_cents: i32,
    pub plan_created_at: chrono::DateTime<Utc>,
}

pub async fn get_user_quota(pool: &PgPool, user_id: Uuid) -> Result<Option<(UserQuota, Plan)>> {
    let row = sqlx::query_as::<_, QuotaWithPlan>(
        r#"
        SELECT
            uq.user_id, uq.plan_id, uq.tokens_used, uq.requests_used, uq.period_start, uq.updated_at,
            p.id as p_id, p.name as plan_name, p.token_limit, p.request_limit, p.price_monthly_cents, p.created_at as plan_created_at
        FROM user_quotas uq
        JOIN plans p ON uq.plan_id = p.id
        WHERE uq.user_id = $1
        "#,
    )
    .bind(user_id)
    .fetch_optional(pool)
    .await?;

    Ok(row.map(|r| {
        let quota = UserQuota {
            user_id: r.user_id,
            plan_id: r.plan_id,
            tokens_used: r.tokens_used,
            requests_used: r.requests_used,
            period_start: r.period_start,
            updated_at: r.updated_at,
        };
        let plan = Plan {
            id: r.p_id,
            name: r.plan_name,
            token_limit: r.token_limit,
            request_limit: r.request_limit,
            price_monthly_cents: r.price_monthly_cents,
            created_at: r.plan_created_at,
        };
        (quota, plan)
    }))
}

pub async fn init_user_quota(pool: &PgPool, user_id: Uuid) -> Result<()> {
    sqlx::query(
        r#"
        INSERT INTO user_quotas (user_id, plan_id)
        SELECT $1, id FROM plans WHERE name = 'free'
        ON CONFLICT (user_id) DO NOTHING
        "#
    )
    .bind(user_id)
    .execute(pool)
    .await?;

    Ok(())
}

pub async fn record_usage(
    pool: &PgPool,
    user_id: Uuid,
    event_type: &str,
    tokens: i64,
    metadata: Option<serde_json::Value>,
) -> Result<()> {
    let mut tx = pool.begin().await?;

    // Insert usage event
    sqlx::query(
        r#"
        INSERT INTO usage_events (user_id, event_type, tokens_consumed, metadata)
        VALUES ($1, $2, $3, $4)
        "#,
    )
    .bind(user_id)
    .bind(event_type)
    .bind(tokens)
    .bind(&metadata)
    .execute(&mut *tx)
    .await?;

    // Update quota
    sqlx::query(
        r#"
        UPDATE user_quotas
        SET tokens_used = tokens_used + $2,
            requests_used = requests_used + 1,
            updated_at = NOW()
        WHERE user_id = $1
        "#
    )
    .bind(user_id)
    .bind(tokens)
    .execute(&mut *tx)
    .await?;

    tx.commit().await?;
    Ok(())
}

// ==================== Audit Log ====================

pub async fn log_audit(
    pool: &PgPool,
    user_id: Option<Uuid>,
    action: &str,
    ip: Option<&str>,
    user_agent: Option<&str>,
    metadata: Option<serde_json::Value>,
) -> Result<()> {
    sqlx::query(
        r#"
        INSERT INTO audit_logs (user_id, action, ip_address, user_agent, metadata)
        VALUES ($1, $2, $3, $4, $5)
        "#,
    )
    .bind(user_id)
    .bind(action)
    .bind(ip)
    .bind(user_agent)
    .bind(&metadata)
    .execute(pool)
    .await?;

    Ok(())
}

// ==================== Email Verification ====================

/// Set verification token for a user
pub async fn set_verification_token(pool: &PgPool, user_id: Uuid, token: &str) -> Result<()> {
    let expires_at = Utc::now() + Duration::hours(24);

    sqlx::query(
        r#"
        UPDATE users
        SET verification_token = $2,
            verification_token_expires_at = $3,
            updated_at = NOW()
        WHERE id = $1
        "#
    )
    .bind(user_id)
    .bind(token)
    .bind(expires_at)
    .execute(pool)
    .await?;

    Ok(())
}

/// Verify email with token
pub async fn verify_email(pool: &PgPool, token: &str) -> Result<Option<User>> {
    let user = sqlx::query_as::<_, User>(
        r#"
        UPDATE users
        SET is_verified = true,
            verification_token = null,
            verification_token_expires_at = null,
            updated_at = NOW()
        WHERE verification_token = $1
          AND verification_token_expires_at > NOW()
        RETURNING *
        "#
    )
    .bind(token)
    .fetch_optional(pool)
    .await?;

    Ok(user)
}

/// Get user by verification token
pub async fn get_user_by_verification_token(pool: &PgPool, token: &str) -> Result<Option<User>> {
    let user = sqlx::query_as::<_, User>(
        r#"
        SELECT * FROM users
        WHERE verification_token = $1
          AND verification_token_expires_at > NOW()
        "#
    )
    .bind(token)
    .fetch_optional(pool)
    .await?;

    Ok(user)
}

// ==================== Password Reset ====================

/// Set password reset token for a user
pub async fn set_password_reset_token(pool: &PgPool, email: &str, token: &str) -> Result<Option<User>> {
    let expires_at = Utc::now() + Duration::hours(1);

    let user = sqlx::query_as::<_, User>(
        r#"
        UPDATE users
        SET password_reset_token = $2,
            password_reset_expires_at = $3,
            updated_at = NOW()
        WHERE email = $1
        RETURNING *
        "#
    )
    .bind(email)
    .bind(token)
    .bind(expires_at)
    .fetch_optional(pool)
    .await?;

    Ok(user)
}

/// Reset password with token
pub async fn reset_password(pool: &PgPool, token: &str, new_password_hash: &str) -> Result<Option<User>> {
    let user = sqlx::query_as::<_, User>(
        r#"
        UPDATE users
        SET password_hash = $2,
            password_reset_token = null,
            password_reset_expires_at = null,
            is_verified = true,
            updated_at = NOW()
        WHERE password_reset_token = $1
          AND password_reset_expires_at > NOW()
        RETURNING *
        "#
    )
    .bind(token)
    .bind(new_password_hash)
    .fetch_optional(pool)
    .await?;

    Ok(user)
}

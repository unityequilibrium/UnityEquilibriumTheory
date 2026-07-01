use argon2::{
    password_hash::{rand_core::OsRng, PasswordHash, PasswordHasher, PasswordVerifier, SaltString},
    Argon2,
};
use chrono::{Duration, Utc};
use jsonwebtoken::{decode, encode, DecodingKey, EncodingKey, Header, Validation};
use rand::Rng;
use sha2::{Digest, Sha256};

use crate::config::CONFIG;
use crate::models::User;

pub type AuthResult<T> = Result<T, AuthError>;

#[derive(Debug)]
pub enum AuthError {
    InvalidCredentials,
    UserExists,
    InvalidToken,
    TokenExpired,
    PasswordHashError(String),
    JwtError(String),
}

impl std::fmt::Display for AuthError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            AuthError::InvalidCredentials => write!(f, "Invalid credentials"),
            AuthError::UserExists => write!(f, "User already exists"),
            AuthError::InvalidToken => write!(f, "Invalid token"),
            AuthError::TokenExpired => write!(f, "Token expired"),
            AuthError::PasswordHashError(e) => write!(f, "Password hashing error: {}", e),
            AuthError::JwtError(e) => write!(f, "JWT error: {}", e),
        }
    }
}

impl std::error::Error for AuthError {}

impl From<argon2::password_hash::Error> for AuthError {
    fn from(e: argon2::password_hash::Error) -> Self {
        AuthError::PasswordHashError(e.to_string())
    }
}

impl From<jsonwebtoken::errors::Error> for AuthError {
    fn from(e: jsonwebtoken::errors::Error) -> Self {
        AuthError::JwtError(e.to_string())
    }
}

#[derive(Debug, serde::Serialize, serde::Deserialize)]
pub struct Claims {
    pub sub: String,      // User ID
    pub email: String,
    pub exp: i64,
    pub iat: i64,
    pub type_: String,    // "access" or "refresh"
}

/// Hash a password using Argon2
pub fn hash_password(password: &str) -> AuthResult<String> {
    let salt = SaltString::generate(&mut OsRng);
    let argon2 = Argon2::default();
    Ok(argon2.hash_password(password.as_bytes(), &salt)?.to_string())
}

/// Verify a password against a hash
pub fn verify_password(password: &str, hash: &str) -> AuthResult<bool> {
    let parsed_hash = PasswordHash::new(hash)?;
    let argon2 = Argon2::default();
    Ok(argon2.verify_password(password.as_bytes(), &parsed_hash).is_ok())
}

/// Generate an access token (JWT)
pub fn generate_access_token(user: &User) -> AuthResult<String> {
    let now = Utc::now();
    let exp = now + Duration::hours(CONFIG.jwt_expiry_hours);

    let claims = Claims {
        sub: user.id.to_string(),
        email: user.email.clone(),
        exp: exp.timestamp(),
        iat: now.timestamp(),
        type_: "access".to_string(),
    };

    encode(
        &Header::default(),
        &claims,
        &EncodingKey::from_secret(CONFIG.jwt_secret.as_bytes()),
    )
    .map_err(AuthError::from)
}

/// Generate a refresh token (random string)
pub fn generate_refresh_token() -> String {
    let mut rng = rand::thread_rng();
    (0..64)
        .map(|_| rng.sample(rand::distributions::Alphanumeric) as char)
        .collect()
}

/// Hash a token for storage (SHA256)
pub fn hash_token(token: &str) -> String {
    let mut hasher = Sha256::new();
    hasher.update(token.as_bytes());
    format!("{:x}", hasher.finalize())
}

/// Validate an access token
pub fn validate_access_token(token: &str) -> AuthResult<Claims> {
    let token_data = decode::<Claims>(
        token,
        &DecodingKey::from_secret(CONFIG.jwt_secret.as_bytes()),
        &Validation::default(),
    )
    .map_err(AuthError::from)?;

    if token_data.claims.type_ != "access" {
        return Err(AuthError::InvalidToken);
    }

    Ok(token_data.claims)
}

/// Generate a secure API key
pub fn generate_api_key() -> (String, String, String) {
    let mut rng = rand::thread_rng();
    let key: String = (0..32)
        .map(|_| rng.sample(rand::distributions::Alphanumeric) as char)
        .collect();

    let prefix = format!("uet_{}", &key[..8]);
    let key_hash = hash_token(&key);

    (key, prefix, key_hash)
}

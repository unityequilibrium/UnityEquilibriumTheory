use anyhow::Result;
use oauth2::{AuthUrl, ClientId, ClientSecret, CsrfToken, RedirectUrl, Scope, TokenUrl, TokenResponse};
use oauth2::basic::BasicClient;
use oauth2::reqwest::async_http_client;
use serde::{Deserialize, Serialize};

use crate::config::CONFIG;

#[derive(Clone)]
pub struct OAuthClients {
    pub google: Option<BasicClient>,
    pub github: Option<BasicClient>,
}

impl OAuthClients {
    pub fn new() -> Self {
        let google = if !CONFIG.google_client_id.is_empty() {
            let auth_url = AuthUrl::new("https://accounts.google.com/o/oauth2/v2/auth".to_string())
                .expect("Invalid Google auth URL");
            let token_url = TokenUrl::new("https://oauth2.googleapis.com/token".to_string())
                .expect("Invalid Google token URL");
            let redirect_url = RedirectUrl::new(format!("{}/google", CONFIG.oauth_redirect_url))
                .expect("Invalid redirect URL");

            Some(
                BasicClient::new(
                    ClientId::new(CONFIG.google_client_id.clone()),
                    Some(ClientSecret::new(CONFIG.google_client_secret.clone())),
                    auth_url,
                    Some(token_url),
                )
                .set_redirect_uri(redirect_url)
            )
        } else {
            None
        };

        let github = if !CONFIG.github_client_id.is_empty() {
            let auth_url = AuthUrl::new("https://github.com/login/oauth/authorize".to_string())
                .expect("Invalid GitHub auth URL");
            let token_url = TokenUrl::new("https://github.com/login/oauth/access_token".to_string())
                .expect("Invalid GitHub token URL");
            let redirect_url = RedirectUrl::new(format!("{}/github", CONFIG.oauth_redirect_url))
                .expect("Invalid redirect URL");

            Some(
                BasicClient::new(
                    ClientId::new(CONFIG.github_client_id.clone()),
                    Some(ClientSecret::new(CONFIG.github_client_secret.clone())),
                    auth_url,
                    Some(token_url),
                )
                .set_redirect_uri(redirect_url)
            )
        } else {
            None
        };

        Self { google, github }
    }
}

#[derive(Debug, Serialize)]
pub struct OAuthUrl {
    pub url: String,
    pub state: String,
}

#[derive(Debug, Deserialize)]
pub struct GoogleUserInfo {
    pub id: String,
    pub email: String,
    pub name: Option<String>,
    pub picture: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct GitHubUserInfo {
    pub id: i64,
    pub email: Option<String>,
    pub login: String,
    pub avatar_url: Option<String>,
}

/// Generate Google OAuth authorization URL
pub fn get_google_auth_url(client: &BasicClient) -> OAuthUrl {
    let (url, csrf) = client
        .authorize_url(CsrfToken::new_random)
        .add_scope(Scope::new("email".to_string()))
        .add_scope(Scope::new("profile".to_string()))
        .url();

    OAuthUrl {
        url: url.to_string(),
        state: csrf.secret().clone(),
    }
}

/// Exchange Google auth code for user info
pub async fn exchange_google_code(client: &BasicClient, code: &str) -> Result<GoogleUserInfo> {
    let token = client
        .exchange_code(oauth2::AuthorizationCode::new(code.to_string()))
        .request_async(async_http_client)
        .await?;

    let access_token = token.access_token().secret();

    let user_info = reqwest::Client::new()
        .get("https://www.googleapis.com/oauth2/v3/userinfo")
        .bearer_auth(access_token)
        .send()
        .await?
        .json::<GoogleUserInfo>()
        .await?;

    Ok(user_info)
}

/// Generate GitHub OAuth authorization URL
pub fn get_github_auth_url(client: &BasicClient) -> OAuthUrl {
    let (url, csrf) = client
        .authorize_url(CsrfToken::new_random)
        .add_scope(Scope::new("user:email".to_string()))
        .url();

    OAuthUrl {
        url: url.to_string(),
        state: csrf.secret().clone(),
    }
}

/// Exchange GitHub auth code for user info
pub async fn exchange_github_code(client: &BasicClient, code: &str) -> Result<GitHubUserInfo> {
    let token = client
        .exchange_code(oauth2::AuthorizationCode::new(code.to_string()))
        .request_async(async_http_client)
        .await?;

    let access_token = token.access_token().secret();

    let user_info = reqwest::Client::new()
        .get("https://api.github.com/user")
        .bearer_auth(access_token)
        .header("User-Agent", "UET-Platform")
        .send()
        .await?
        .json::<GitHubUserInfo>()
        .await?;

    Ok(user_info)
}

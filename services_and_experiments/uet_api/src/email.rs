use anyhow::Result;
use reqwest::Client;
use serde::{Deserialize, Serialize};
use tracing::info;

use crate::config::CONFIG;

#[derive(Debug, Serialize)]
struct ResendEmailRequest {
    from: String,
    to: Vec<String>,
    subject: String,
    html: String,
}

#[derive(Debug, Deserialize)]
struct ResendResponse {
    id: String,
}

pub struct EmailService {
    client: Client,
    api_key: String,
    from_email: String,
}

impl Clone for EmailService {
    fn clone(&self) -> Self {
        Self {
            client: Client::new(),
            api_key: self.api_key.clone(),
            from_email: self.from_email.clone(),
        }
    }
}

impl EmailService {
    pub fn new() -> Self {
        Self {
            client: Client::new(),
            api_key: std::env::var("RESEND_API_KEY").unwrap_or_default(),
            from_email: std::env::var("EMAIL_FROM")
                .unwrap_or_else(|_| "noreply@uet.ai".to_string()),
        }
    }

    /// Send verification email
    pub async fn send_verification_email(
        &self,
        to: &str,
        username: &str,
        verify_url: &str,
    ) -> Result<()> {
        let html = format!(
            r#"
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: #0a0a0f; font-family: 'Inter', -apple-system, sans-serif;">
    <table width="100%" cellpadding="0" cellspacing="0" style="padding: 40px 20px;">
        <tr>
            <td align="center">
                <table width="100%" style="max-width: 500px; background: linear-gradient(180deg, #1a1a2e 0%, #0a0a0f 100%); border-radius: 16px; border: 1px solid rgba(255,255,255,0.1);">
                    <tr>
                        <td style="padding: 40px 30px; text-align: center;">
                            <!-- Logo -->
                            <div style="font-size: 32px; font-weight: 800; margin-bottom: 8px;">
                                <span style="background: linear-gradient(to right, #818cf8, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">⚛ UET</span>
                            </div>
                            <p style="color: #9ca3af; font-size: 14px; margin-bottom: 32px;">Unity Equilibrium Theory</p>

                            <!-- Greeting -->
                            <h1 style="color: #f3f4f6; font-size: 24px; font-weight: 600; margin: 0 0 16px 0;">
                                Welcome, {username}!
                            </h1>
                            <p style="color: #9ca3af; font-size: 15px; line-height: 1.6; margin: 0 0 32px 0;">
                                Verify your email to start exploring the equations of the universe.
                            </p>

                            <!-- Button -->
                            <a href="{verify_url}" style="display: inline-block; background: linear-gradient(to right, #6366f1, #8b5cf6); color: white; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-weight: 600; font-size: 15px;">
                                Verify Email
                            </a>

                            <!-- Footer -->
                            <p style="color: #6b7280; font-size: 12px; margin-top: 32px; line-height: 1.6;">
                                This link expires in 24 hours.<br>
                                If you didn't create an account, ignore this email.
                            </p>
                        </td>
                    </tr>
                </table>

                <p style="color: #4b5563; font-size: 11px; margin-top: 24px;">
                    © 2026 UET Platform · Unity Equilibrium Theory
                </p>
            </td>
        </tr>
    </table>
</body>
</html>
"#,
            username = username,
            verify_url = verify_url
        );

        self.send_email(to, "Verify your UET account", &html).await
    }

    /// Send password reset email
    pub async fn send_password_reset_email(
        &self,
        to: &str,
        username: &str,
        reset_url: &str,
    ) -> Result<()> {
        let html = format!(
            r#"
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: #0a0a0f; font-family: 'Inter', -apple-system, sans-serif;">
    <table width="100%" cellpadding="0" cellspacing="0" style="padding: 40px 20px;">
        <tr>
            <td align="center">
                <table width="100%" style="max-width: 500px; background: linear-gradient(180deg, #1a1a2e 0%, #0a0a0f 100%); border-radius: 16px; border: 1px solid rgba(255,255,255,0.1);">
                    <tr>
                        <td style="padding: 40px 30px; text-align: center;">
                            <div style="font-size: 32px; font-weight: 800; margin-bottom: 8px;">
                                <span style="background: linear-gradient(to right, #818cf8, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">⚛ UET</span>
                            </div>

                            <h1 style="color: #f3f4f6; font-size: 24px; font-weight: 600; margin: 32px 0 16px 0;">
                                Reset Password
                            </h1>
                            <p style="color: #9ca3af; font-size: 15px; line-height: 1.6; margin: 0 0 32px 0;">
                                Hi {username}, click below to reset your password.
                            </p>

                            <a href="{reset_url}" style="display: inline-block; background: linear-gradient(to right, #6366f1, #8b5cf6); color: white; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-weight: 600; font-size: 15px;">
                                Reset Password
                            </a>

                            <p style="color: #6b7280; font-size: 12px; margin-top: 32px; line-height: 1.6;">
                                This link expires in 1 hour.<br>
                                If you didn't request this, ignore this email.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"#,
            username = username,
            reset_url = reset_url
        );

        self.send_email(to, "Reset your UET password", &html).await
    }

    /// Send welcome email after verification
    pub async fn send_welcome_email(&self, to: &str, username: &str) -> Result<()> {
        let html = format!(
            r#"
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: #0a0a0f; font-family: 'Inter', -apple-system, sans-serif;">
    <table width="100%" cellpadding="0" cellspacing="0" style="padding: 40px 20px;">
        <tr>
            <td align="center">
                <table width="100%" style="max-width: 500px; background: linear-gradient(180deg, #1a1a2e 0%, #0a0a0f 100%); border-radius: 16px; border: 1px solid rgba(255,255,255,0.1);">
                    <tr>
                        <td style="padding: 40px 30px; text-align: center;">
                            <div style="font-size: 32px; font-weight: 800; margin-bottom: 8px;">
                                <span style="background: linear-gradient(to right, #10b981, #34d399); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">✓ Verified</span>
                            </div>

                            <h1 style="color: #f3f4f6; font-size: 24px; font-weight: 600; margin: 32px 0 16px 0;">
                                Welcome to UET, {username}!
                            </h1>
                            <p style="color: #9ca3af; font-size: 15px; line-height: 1.6; margin: 0 0 24px 0;">
                                Your account is ready. Start exploring the equations that describe our universe.
                            </p>

                            <div style="background: rgba(99, 102, 241, 0.1); border-radius: 8px; padding: 20px; margin: 24px 0;">
                                <p style="color: #818cf8; font-size: 13px; font-weight: 600; margin: 0 0 8px 0;">Quick Start</p>
                                <code style="color: #10b981; font-size: 12px; font-family: monospace;">pip install uet</code>
                            </div>

                            <a href="https://uet.ai/docs" style="display: inline-block; background: linear-gradient(to right, #6366f1, #8b5cf6); color: white; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-weight: 600; font-size: 15px;">
                                Read the Docs
                            </a>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"#,
            username = username
        );

        self.send_email(to, "Welcome to UET!", &html).await
    }

    /// Core send function via Resend API
    async fn send_email(&self, to: &str, subject: &str, html: &str) -> Result<()> {
        if self.api_key.is_empty() {
            info!("Email skipped (no API key): to={}, subject={}", to, subject);
            return Ok(());
        }

        let request = ResendEmailRequest {
            from: self.from_email.clone(),
            to: vec![to.to_string()],
            subject: subject.to_string(),
            html: html.to_string(),
        };

        let response = self
            .client
            .post("https://api.resend.com/emails")
            .header("Authorization", format!("Bearer {}", self.api_key))
            .header("Content-Type", "application/json")
            .json(&request)
            .send()
            .await?;

        if response.status().is_success() {
            let result: ResendResponse = response.json().await?;
            info!("Email sent: id={}, to={}", result.id, to);
        } else {
            let error = response.text().await?;
            anyhow::bail!("Resend API error: {}", error);
        }

        Ok(())
    }
}

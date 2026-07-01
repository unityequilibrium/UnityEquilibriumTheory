mod db;
mod mcp;
mod mcp_http;
mod embeddings;

use clap::{Parser, Subcommand};
use std::path::Path;

#[derive(Parser)]
#[command(name = "uet_kb")]
#[command(about = "UET Knowledge Base Server (Rust + Postgres)", long_about = None)]
struct Cli {
    #[arg(short, long, default_value = "postgres://postgres:postgres@localhost:5433/uet_kb")]
    db_url: String,

    #[command(subcommand)]
    command: Option<Commands>,
}

#[derive(Subcommand)]
enum Commands {
    /// Initialize the database (Install extensions & Tables)
    InitDb,
    /// Ingest a text file with real hash-based embeddings
    Ingest {
        #[arg(short, long)]
        file: String,
    },
    /// Search for concepts
    Search {
        #[arg(short, long)]
        query: String,
    },
    /// Start the MCP JSON-RPC Server (stdin/stdout)
    StartMcpServer,
    /// Start the MCP HTTP Server
    StartHttpServer {
        #[arg(short, long, default_value = "3002")]
        port: u16,
    },
}

#[tokio::main]
async fn main() {
    let cli = Cli::parse();

    match &cli.command {
        Some(Commands::InitDb) => {
            println!("Initializing database at: {}", cli.db_url);
            match db::init_db(&cli.db_url).await {
                Ok(_) => println!("✅ Database initialized (pgvector enabled)."),
                Err(e) => eprintln!("❌ Error: {}", e),
            }
        }
        Some(Commands::Ingest { file }) => {
            println!("Ingesting file: {}", file);
            // Connect to DB
            let pool = match db::init_db(&cli.db_url).await {
                Ok(p) => p,
                Err(e) => {
                    eprintln!("❌ Failed to connect/init DB: {}", e);
                    return;
                }
            };

            // Read Content
            let content = if Path::new(file).exists() {
                std::fs::read_to_string(file).expect("Failed to read file")
            } else {
                file.clone() // Treat as raw text
            };

            // Insert Doc
            let doc_id = db::insert_document(&pool, None, file, &content, None).await.expect("Failed to insert doc");
            println!("Created Document ID: {}", doc_id);

            // Chunk & Embed with real hash-based embeddings
            let chunks: Vec<&str> = content.split('\n').filter(|s| !s.trim().is_empty()).collect();
            for chunk_text in &chunks {
                let s_vec = embeddings::hash_embed(chunk_text, 1024);
                let p_vec = vec![0.0; 20]; // Physics vector filled by domain-specific tools

                db::insert_chunk(&pool, &doc_id, chunk_text, &s_vec, &p_vec).await.expect("Failed to insert chunk");
            }
            println!("✅ Ingested {} chunks with embeddings.", chunks.len());
        }
        Some(Commands::Search { query }) => {
            println!("Searching for: '{}'", query);
             let pool = match db::init_db(&cli.db_url).await {
                Ok(p) => p,
                Err(e) => {
                    eprintln!("❌ Failed to connect/init DB: {}", e);
                    return;
                }
            };

            // Generate query embedding
            let vec = embeddings::hash_embed(query, 1024);

            // Top K = 5
            match db::search_similar(&pool, &vec, 5).await {
                Ok(results) => {
                    for res in results {
                        println!("- [Score: {:.4}] (Doc: {}) {}", res.score, res.path, res.text.trim());
                    }
                }
                Err(e) => eprintln!("❌ Search failed: {}", e),
            }
        }
        Some(Commands::StartMcpServer) => {
            if let Err(e) = mcp::run_mcp_server(&cli.db_url).await {
                eprintln!("MCP Server Error: {}", e);
            }
        }
        Some(Commands::StartHttpServer { port }) => {
            if let Err(e) = mcp_http::run_http_mcp_server(&cli.db_url, *port).await {
                eprintln!("MCP HTTP Server Error: {}", e);
            }
        }
        None => {
            println!("UET Knowledge Base Server v0.1.0 (Postgres Edition)");
            println!("Use --help for commands.");
        }
    }
}

use libp2p::{
    gossipsub, noise, swarm::NetworkBehaviour, tcp, yamux, identity,
    PeerId, Swarm, SwarmBuilder, Multiaddr,
};
use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};
use std::time::Duration;
use std::str::FromStr;
use thiserror::Error;
use tracing::info;

#[derive(Error, Debug)]
pub enum P2pError {
    #[error("Swarm build error")]
    BuildError,
    #[error("Network error: {0}")]
    NetworkError(String),
}

// Custom behaviour combining Gossipsub (for blocks/txs)
#[derive(NetworkBehaviour)]
pub struct UetBehaviour {
    pub gossipsub: gossipsub::Behaviour,
}

pub struct UetNode {
    swarm: Swarm<UetBehaviour>,
}

impl UetNode {
    pub fn new() -> Result<Self, P2pError> {
        // Generate a random PeerId
        let id_keys = identity::Keypair::generate_ed25519();
        let peer_id = PeerId::from(id_keys.public());
        info!("Local peer id: {peer_id}");

        // Setup Gossipsub config
        let message_id_fn = |message: &gossipsub::Message| {
            let mut s = DefaultHasher::new();
            message.data.hash(&mut s);
            gossipsub::MessageId::from(s.finish().to_string())
        };

        let gossipsub_config = gossipsub::ConfigBuilder::default()
            .heartbeat_interval(Duration::from_secs(10))
            .validation_mode(gossipsub::ValidationMode::Strict)
            .message_id_fn(message_id_fn)
            .build()
            .map_err(|e| P2pError::NetworkError(e.to_string()))?;

        let gossipsub = gossipsub::Behaviour::new(
            gossipsub::MessageAuthenticity::Signed(id_keys.clone()),
            gossipsub_config,
        ).map_err(|e| P2pError::NetworkError(e.to_string()))?;

        let behaviour = UetBehaviour { gossipsub };

        // Build the Swarm
        let swarm = SwarmBuilder::with_existing_identity(id_keys)
            .with_tokio()
            .with_tcp(
                tcp::Config::default(),
                noise::Config::new,
                yamux::Config::default,
            )
            .map_err(|_| P2pError::BuildError)?
            .with_behaviour(|_| behaviour)
            .map_err(|_| P2pError::BuildError)?
            .with_swarm_config(|cfg| cfg.with_idle_connection_timeout(Duration::from_secs(60)))
            .build();

        Ok(Self { swarm })
    }

    pub fn listen(&mut self, addr: &str) -> Result<(), P2pError> {
        let multiaddr = Multiaddr::from_str(addr)
            .map_err(|e| P2pError::NetworkError(format!("Invalid address: {}", e)))?;
        self.swarm.listen_on(multiaddr).map_err(|e| P2pError::NetworkError(e.to_string()))?;
        Ok(())
    }

    pub fn dial(&mut self, addr: &str) -> Result<(), P2pError> {
        let multiaddr = Multiaddr::from_str(addr)
            .map_err(|e| P2pError::NetworkError(format!("Invalid address: {}", e)))?;
        self.swarm.dial(multiaddr).map_err(|e| P2pError::NetworkError(e.to_string()))?;
        Ok(())
    }

    pub fn subscribe(&mut self, topic_name: &str) -> Result<(), P2pError> {
        let topic = gossipsub::IdentTopic::new(topic_name);
        self.swarm.behaviour_mut().gossipsub.subscribe(&topic)
            .map_err(|e| P2pError::NetworkError(e.to_string()))?;
        Ok(())
    }

    pub fn publish(&mut self, topic_name: &str, data: Vec<u8>) -> Result<(), P2pError> {
        let topic = gossipsub::IdentTopic::new(topic_name);
        self.swarm.behaviour_mut().gossipsub.publish(topic, data)
            .map_err(|e| P2pError::NetworkError(e.to_string()))?;
        Ok(())
    }
}
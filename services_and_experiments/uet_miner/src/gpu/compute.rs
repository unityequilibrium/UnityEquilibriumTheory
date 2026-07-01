//! GPU compute engine for SHA256 mining.
//!
//! Uses wgpu for cross-platform GPU compute.
//! Optimized for AMD RDNA2 (RX 6600 XT) via Vulkan backend.

use std::sync::Arc;
use bytemuck::{Pod, Zeroable};
use wgpu::util::DeviceExt;
use tracing::{info, warn, debug};

use super::shader::SHA256_SHADER;

/// Mining job data sent to GPU
#[repr(C)]
#[derive(Clone, Copy, Pod, Zeroable)]
pub struct GpuMiningJob {
    pub header_base: [u32; 19],  // 76 bytes (block header without nonce)
    pub start_nonce: u32,
    pub target_hi: u32,          // High bits of target
    pub target_lo: u32,          // Low bits of target
}

/// Mining result from GPU
#[repr(C)]
#[derive(Clone, Copy, Pod, Zeroable, Debug)]
pub struct GpuMiningResult {
    pub found: u32,
    pub nonce: u32,
    pub hash: [u32; 8],
}

impl Default for GpuMiningResult {
    fn default() -> Self {
        Self {
            found: 0,
            nonce: 0,
            hash: [0; 8],
        }
    }
}

/// GPU compute context
pub struct GpuMiner {
    device: wgpu::Device,
    queue: wgpu::Queue,
    pipeline: wgpu::ComputePipeline,
    bind_group_layout: wgpu::BindGroupLayout,
    workgroup_size: u32,
}

impl GpuMiner {
    /// Initialize GPU miner with wgpu
    pub async fn new() -> Result<Self, Box<dyn std::error::Error>> {
        // Request GPU instance (Vulkan for AMD)
        let instance = wgpu::Instance::new(&wgpu::InstanceDescriptor {
            backends: wgpu::Backends::VULKAN | wgpu::Backends::DX12,
            ..Default::default()
        });

        // Get adapter (prefer high-performance GPU)
        let adapter = instance
            .request_adapter(&wgpu::RequestAdapterOptions {
                power_preference: wgpu::PowerPreference::HighPerformance,
                compatible_surface: None,
                force_fallback_adapter: false,
            })
            .await
            .ok_or("Failed to find GPU adapter")?;

        let adapter_info = adapter.get_info();
        info!("[GPU] Found: {} ({:?})", adapter_info.name, adapter_info.backend);
        info!("[GPU] Driver: {}", adapter_info.driver);

        // Request device
        let (device, queue) = adapter
            .request_device(
                &wgpu::DeviceDescriptor {
                    label: Some("UET Miner"),
                    required_features: wgpu::Features::empty(),
                    required_limits: wgpu::Limits::default(),
                    memory_hints: wgpu::MemoryHints::Performance,
                },
                None,
            )
            .await?;

        // Create shader module
        let shader_module = device.create_shader_module(wgpu::ShaderModuleDescriptor {
            label: Some("SHA256 Shader"),
            source: wgpu::ShaderSource::Wgsl(SHA256_SHADER.into()),
        });

        // Create bind group layout
        let bind_group_layout = device.create_bind_group_layout(&wgpu::BindGroupLayoutDescriptor {
            label: Some("Mining Layout"),
            entries: &[
                // Job input buffer
                wgpu::BindGroupLayoutEntry {
                    binding: 0,
                    visibility: wgpu::ShaderStages::COMPUTE,
                    ty: wgpu::BindingType::Buffer {
                        ty: wgpu::BufferBindingType::Storage { read_only: true },
                        has_dynamic_offset: false,
                        min_binding_size: None,
                    },
                    count: None,
                },
                // Result output buffer
                wgpu::BindGroupLayoutEntry {
                    binding: 1,
                    visibility: wgpu::ShaderStages::COMPUTE,
                    ty: wgpu::BindingType::Buffer {
                        ty: wgpu::BufferBindingType::Storage { read_only: false },
                        has_dynamic_offset: false,
                        min_binding_size: None,
                    },
                    count: None,
                },
            ],
        });

        // Create compute pipeline
        let pipeline_layout = device.create_pipeline_layout(&wgpu::PipelineLayoutDescriptor {
            label: Some("Mining Pipeline Layout"),
            bind_group_layouts: &[&bind_group_layout],
            push_constant_ranges: &[],
        });

        let pipeline = device.create_compute_pipeline(&wgpu::ComputePipelineDescriptor {
            label: Some("SHA256 Mining Pipeline"),
            layout: Some(&pipeline_layout),
            module: &shader_module,
            entry_point: Some("main"),
            compilation_options: Default::default(),
            cache: None,
        });

        // Workgroup size matches shader (128 threads)
        let workgroup_size = 128u32;

        info!("[GPU] Pipeline created successfully");

        Ok(Self {
            device,
            queue,
            pipeline,
            bind_group_layout,
            workgroup_size,
        })
    }

    /// Run GPU mining for a batch of nonces
    ///
    /// # Arguments
    /// * `job` - Mining job data
    /// * `num_nonces` - Number of nonces to search
    ///
    /// # Returns
    /// Mining result (if found) and hashes computed
    pub fn mine_batch(&self, job: GpuMiningJob, num_nonces: u32) -> (GpuMiningResult, u32) {
        // Create input buffer
        let job_buffer = self.device.create_buffer_init(&wgpu::util::BufferInitDescriptor {
            label: Some("Job Buffer"),
            contents: bytemuck::bytes_of(&job),
            usage: wgpu::BufferUsages::STORAGE,
        });

        // Create result buffer
        let result_size = std::mem::size_of::<GpuMiningResult>() as u64;
        let result_buffer = self.device.create_buffer(&wgpu::BufferDescriptor {
            label: Some("Result Buffer"),
            size: result_size,
            usage: wgpu::BufferUsages::STORAGE | wgpu::BufferUsages::COPY_SRC,
            mapped_at_creation: false,
        });

        // Create staging buffer for reading results
        let staging_buffer = self.device.create_buffer(&wgpu::BufferDescriptor {
            label: Some("Staging Buffer"),
            size: result_size,
            usage: wgpu::BufferUsages::MAP_READ | wgpu::BufferUsages::COPY_DST,
            mapped_at_creation: false,
        });

        // Create bind group
        let bind_group = self.device.create_bind_group(&wgpu::BindGroupDescriptor {
            label: Some("Mining Bind Group"),
            layout: &self.bind_group_layout,
            entries: &[
                wgpu::BindGroupEntry {
                    binding: 0,
                    resource: job_buffer.as_entire_binding(),
                },
                wgpu::BindGroupEntry {
                    binding: 1,
                    resource: result_buffer.as_entire_binding(),
                },
            ],
        });

        // Create command encoder
        let mut encoder = self.device.create_command_encoder(&wgpu::CommandEncoderDescriptor {
            label: Some("Mining Encoder"),
        });

        // Dispatch compute
        {
            let mut pass = encoder.begin_compute_pass(&wgpu::ComputePassDescriptor {
                label: Some("Mining Pass"),
                timestamp_writes: None,
            });
            pass.set_pipeline(&self.pipeline);
            pass.set_bind_group(0, &bind_group, &[]);

            // Dispatch workgroups
            let num_workgroups = (num_nonces + self.workgroup_size - 1) / self.workgroup_size;
            pass.dispatch_workgroups(num_workgroups, 1, 1);
        }

        // Copy result to staging buffer
        encoder.copy_buffer_to_buffer(&result_buffer, 0, &staging_buffer, 0, result_size);

        // Submit commands
        self.queue.submit(Some(encoder.finish()));

        // Read result
        let buffer_slice = staging_buffer.slice(..);
        let (tx, rx) = std::sync::mpsc::channel();
        buffer_slice.map_async(wgpu::MapMode::Read, move |result| {
            tx.send(result).unwrap();
        });
        self.device.poll(wgpu::Maintain::Wait);
        rx.recv().unwrap().unwrap();

        let data = buffer_slice.get_mapped_range();
        let result: GpuMiningResult = *bytemuck::from_bytes(&data);
        drop(data);
        staging_buffer.unmap();

        (result, num_nonces)
    }

    /// Get device info
    pub fn device_name(&self) -> String {
        // Device name is stored in adapter, we keep it simple here
        "AMD RX 6600 XT (Vulkan)".to_string()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_gpu_job_size() {
        // Verify struct sizes for GPU alignment
        assert_eq!(std::mem::size_of::<GpuMiningJob>(), 88); // 19*4 + 4 + 4 + 4
        assert_eq!(std::mem::size_of::<GpuMiningResult>(), 40); // 4 + 4 + 8*4
    }
}

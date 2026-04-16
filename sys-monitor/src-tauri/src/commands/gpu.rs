use crate::error::AppError;
use serde::{Deserialize, Serialize};
use std::process::Command;

/// GPU vendor detection
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum GpuVendor {
    Nvidia,
    Amd,
    Intel,
    AppleSilicon,
    Unknown,
}

/// GPU information structure
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GpuInfo {
    pub vendor: String,
    pub model: String,
    pub usage_percent: f32,
    pub memory_used: u64,         // MB
    pub memory_total: u64,        // MB
    pub temperature: Option<u32>, // Celsius
}

/// Detect GPU vendor (platform-specific)
fn detect_gpu_vendor() -> GpuVendor {
    #[cfg(target_os = "windows")]
    {
        // Try to detect via nvidia-smi first
        if Command::new("nvidia-smi").arg("--version").output().is_ok() {
            return GpuVendor::Nvidia;
        }

        // Check for AMD or Intel via WMI (simplified - would need proper WMI implementation)
        // For now, default to Unknown
        GpuVendor::Unknown
    }

    #[cfg(target_os = "linux")]
    {
        // Check for nvidia-smi
        if Command::new("nvidia-smi").arg("--version").output().is_ok() {
            return GpuVendor::Nvidia;
        }

        // Check /sys/class/drm for AMD/Intel
        use std::path::Path;
        if Path::new("/sys/class/drm").exists() {
            // Simplified detection - would need to parse lspci or sysfs
            return GpuVendor::Unknown;
        }

        GpuVendor::Unknown
    }

    #[cfg(target_os = "macos")]
    {
        // macOS with Apple Silicon
        GpuVendor::AppleSilicon
    }

    #[cfg(not(any(target_os = "windows", target_os = "linux", target_os = "macos")))]
    {
        GpuVendor::Unknown
    }
}

/// Get NVIDIA GPU info via nvidia-smi
fn get_nvidia_gpu_info() -> Result<Option<GpuInfo>, AppError> {
    let output = Command::new("nvidia-smi")
        .args(&[
            "--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu,name",
            "--format=csv,noheader,nounits",
        ])
        .output();

    match output {
        Ok(output) if output.status.success() => {
            let stdout = String::from_utf8_lossy(&output.stdout);
            let line = stdout.lines().next().unwrap_or("");
            let parts: Vec<&str> = line.split(',').map(|s| s.trim()).collect();

            if parts.len() >= 5 {
                let usage = parts[0].parse::<f32>().unwrap_or(0.0);
                let memory_used = parts[1].parse::<u64>().unwrap_or(0);
                let memory_total = parts[2].parse::<u64>().unwrap_or(0);
                let temp = parts[3].parse::<u32>().ok();
                let model = parts[4].to_string();

                Ok(Some(GpuInfo {
                    vendor: "NVIDIA".to_string(),
                    model,
                    usage_percent: usage,
                    memory_used,
                    memory_total,
                    temperature: temp,
                }))
            } else {
                Ok(None)
            }
        }
        _ => Ok(None), // nvidia-smi not available
    }
}

/// Get AMD GPU info from sysfs (Linux)
#[cfg(target_os = "linux")]
fn get_amd_gpu_info() -> Result<Option<GpuInfo>, AppError> {
    use std::fs;
    use std::path::Path;

    // This is a simplified example - real implementation would need to:
    // 1. Find the correct DRM device
    // 2. Read from hwmon for temperature
    // 3. Parse utilization from various sources

    let drm_path = Path::new("/sys/class/drm");
    if !drm_path.exists() {
        return Ok(None);
    }

    // Placeholder - would need proper implementation
    Ok(None)
}

/// Get GPU information (main entry point)
#[tauri::command]
pub fn get_gpu_info() -> Result<Option<GpuInfo>, AppError> {
    let vendor = detect_gpu_vendor();

    match vendor {
        GpuVendor::Nvidia => get_nvidia_gpu_info(),
        #[cfg(target_os = "linux")]
        GpuVendor::Amd => get_amd_gpu_info(),
        _ => {
            // GPU not supported or not detected
            Ok(None)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_detect_gpu_vendor() {
        let vendor = detect_gpu_vendor();
        // Just ensure it doesn't panic
        println!("Detected GPU vendor: {:?}", vendor);
    }
}

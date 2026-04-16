use crate::error::AppError;
use crate::models::metrics::{ProcessInfo, SystemMetric};
use std::collections::HashMap;
use std::sync::LazyLock;
use std::sync::Mutex;
use std::time::Instant;
use sysinfo::{CpuRefreshKind, Disks, Networks, RefreshKind, System};
use tauri::command;

static SYSTEM: LazyLock<Mutex<System>> = LazyLock::new(|| {
    Mutex::new(System::new_with_specifics(
        RefreshKind::new()
            .with_cpu(CpuRefreshKind::everything())
            .with_memory(sysinfo::MemoryRefreshKind::everything()),
    ))
});

// Network statistics cache for calculating real-time speeds
static NETWORK_CACHE: LazyLock<Mutex<NetworkCache>> = LazyLock::new(|| {
    Mutex::new(NetworkCache::new())
});

struct NetworkCache {
    last_stats: HashMap<String, (u64, u64)>, // (bytes_received, bytes_sent)
    last_update: Option<Instant>,
}

impl NetworkCache {
    fn new() -> Self {
        Self {
            last_stats: HashMap::new(),
            last_update: None,
        }
    }

    fn calculate_speeds(
        &mut self,
        current_stats: &HashMap<String, (u64, u64)>,
    ) -> HashMap<String, (f64, f64)> {
        let now = Instant::now();
        let mut speeds = HashMap::new();

        if let Some(last_update) = self.last_update {
            let elapsed = now.duration_since(last_update).as_secs_f64();
            if elapsed > 0.0 {
                for (interface, (curr_rx, curr_tx)) in current_stats {
                    if let Some((last_rx, last_tx)) = self.last_stats.get(interface) {
                        // Handle counter wrap-around
                        let rx_diff = if curr_rx >= last_rx {
                            curr_rx - last_rx
                        } else {
                            // Counter wrapped around
                            *curr_rx
                        };
                        let tx_diff = if curr_tx >= last_tx {
                            curr_tx - last_tx
                        } else {
                            *curr_tx
                        };

                        let download_speed = rx_diff as f64 / elapsed;
                        let upload_speed = tx_diff as f64 / elapsed;
                        speeds.insert(interface.clone(), (download_speed, upload_speed));
                    } else {
                        // First time seeing this interface
                        speeds.insert(interface.clone(), (0.0, 0.0));
                    }
                }
            }
        }

        // Update cache
        self.last_stats = current_stats.clone();
        self.last_update = Some(now);

        speeds
    }
}

fn get_system() -> std::sync::MutexGuard<'static, System> {
    let mut sys = SYSTEM.lock().unwrap();
    if sys.cpus().is_empty() {
        sys.refresh_cpu();
        std::thread::sleep(std::time::Duration::from_millis(200));
        sys.refresh_cpu();
    }
    sys
}

fn get_global_cpu_usage(sys: &System) -> f32 {
    if sys.cpus().is_empty() {
        return 0.0;
    }
    sys.global_cpu_info().cpu_usage()
}

fn get_global_memory_usage(sys: &System) -> f64 {
    sys.used_memory() as f64
}

fn get_global_memory_total(sys: &System) -> f64 {
    sys.total_memory() as f64
}

fn get_global_disk_usage(disks: &Disks) -> f64 {
    let mut total = 0;
    let mut available = 0;
    for disk in disks.iter() {
        total += disk.total_space();
        available += disk.available_space();
    }
    if total == 0 {
        return 0.0;
    }
    ((total - available) as f64 / total as f64) * 100.0
}

fn get_global_disk_total(disks: &Disks) -> f64 {
    disks.iter().map(|d| d.total_space() as f64).sum()
}

#[command]
pub fn get_system_metrics() -> Result<SystemMetric, AppError> {
    let mut sys = get_system();
    sys.refresh_all();

    let disks = Disks::new_with_refreshed_list();
    let metric = SystemMetric {
        id: None,
        timestamp: chrono::Utc::now().timestamp(),
        cpu_usage: get_global_cpu_usage(&sys) as f64,
        memory_usage: get_global_memory_usage(&sys),
        memory_total: Some(get_global_memory_total(&sys)),
        disk_usage: Some(get_global_disk_usage(&disks)),
        disk_total: Some(get_global_disk_total(&disks)),
    };

    Ok(metric)
}

#[command]
pub fn get_cpu_info() -> Result<serde_json::Value, AppError> {
    let sys = get_system();

    let cpus: Vec<serde_json::Value> = sys
        .cpus()
        .iter()
        .map(|cpu| {
            serde_json::json!({
                "name": cpu.brand(),
                "usage": cpu.cpu_usage(),
                "frequency": cpu.frequency()
            })
        })
        .collect();

    Ok(serde_json::json!({
        "cpu_count": cpus.len(),
        "cpus": cpus
    }))
}

#[command]
pub fn get_memory_info() -> Result<serde_json::Value, AppError> {
    let sys = get_system();

    Ok(serde_json::json!({
        "total": sys.total_memory(),
        "available": sys.available_memory(),
        "used": sys.used_memory(),
        "usage_percent": (sys.used_memory() as f64 / sys.total_memory() as f64) * 100.0
    }))
}

#[command]
pub fn get_disk_info() -> Result<serde_json::Value, AppError> {
    let disks = Disks::new_with_refreshed_list();

    let disks_json: Vec<serde_json::Value> = disks
        .iter()
        .map(|disk: &sysinfo::Disk| {
            let total_space = disk.total_space();
            let available_space = disk.available_space();
            serde_json::json!({
                "name": disk.name().to_string_lossy(),
                "mount_point": disk.mount_point().to_string_lossy(),
                "total_space": total_space,
                "available_space": available_space,
                "used_space": total_space - available_space,
                "usage_percent": ((total_space - available_space) as f64 / total_space as f64) * 100.0,
                "file_system": disk.file_system().to_string_lossy()
            })
        })
        .collect();

    Ok(serde_json::json!({
        "disk_count": disks_json.len(),
        "disks": disks_json
    }))
}

#[command]
pub fn get_network_info() -> Result<serde_json::Value, AppError> {
    let networks = Networks::new_with_refreshed_list();

    // Collect current network statistics
    let mut current_stats = HashMap::new();
    let interfaces: Vec<serde_json::Value> = networks
        .list()
        .iter()
        .map(|(name, data): (&String, &sysinfo::NetworkData)| {
            let bytes_received = data.total_received();
            let bytes_sent = data.total_transmitted();
            
            // Store for speed calculation
            current_stats.insert(name.clone(), (bytes_received, bytes_sent));

            serde_json::json!({
                "name": name,
                "bytes_received": bytes_received,
                "bytes_sent": bytes_sent
            })
        })
        .collect();

    // Calculate real-time speeds
    let mut cache = NETWORK_CACHE.lock().unwrap();
    let speeds = cache.calculate_speeds(&current_stats);

    // Enhance interface data with speeds
    let enhanced_interfaces: Vec<serde_json::Value> = interfaces
        .into_iter()
        .map(|iface| {
            let name = iface["name"].as_str().unwrap_or("").to_string();
            let (download_speed, upload_speed) = speeds
                .get(&name)
                .copied()
                .unwrap_or((0.0, 0.0));

            serde_json::json!({
                "name": name,
                "bytes_received": iface["bytes_received"],
                "bytes_sent": iface["bytes_sent"],
                "download_speed": download_speed,
                "upload_speed": upload_speed
            })
        })
        .collect();

    Ok(serde_json::json!({
        "interface_count": enhanced_interfaces.len(),
        "interfaces": enhanced_interfaces
    }))
}

/// Get top N processes sorted by CPU or memory usage
#[command]
pub fn get_process_list(limit: u32, sort_by: Option<String>) -> Result<Vec<ProcessInfo>, AppError> {
    let mut sys = get_system();
    sys.refresh_all();

    let total_memory = sys.total_memory() as f64;
    let sort_field = sort_by.unwrap_or_else(|| "cpu".to_string());

    let mut processes: Vec<ProcessInfo> = sys
        .processes()
        .values()
        .map(|p| {
            let memory = p.memory();
            let memory_percent = if total_memory > 0.0 {
                (memory as f64 / total_memory * 100.0) as f32
            } else {
                0.0
            };

            ProcessInfo {
                pid: p.pid().as_u32(),
                name: p.name().to_string(),
                cpu_usage: p.cpu_usage(),
                memory,
                memory_percent,
            }
        })
        .collect();

    // Sort by specified field
    match sort_field.as_str() {
        "memory" => {
            processes.sort_by(|a, b| b.memory.cmp(&a.memory));
        }
        _ => {
            // Default to CPU usage
            processes.sort_by(|a, b| {
                b.cpu_usage
                    .partial_cmp(&a.cpu_usage)
                    .unwrap_or(std::cmp::Ordering::Equal)
            });
        }
    }

    // Limit the number of results (max 100)
    let actual_limit = limit.min(100) as usize;
    processes.truncate(actual_limit);

    Ok(processes)
}

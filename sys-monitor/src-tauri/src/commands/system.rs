use sysinfo::{System, Disks, Networks, CpuRefreshKind, RefreshKind};
use tauri::command;
use crate::models::metrics::SystemMetric;
use crate::error::AppError;
use std::sync::Mutex;
use std::sync::LazyLock;

static SYSTEM: LazyLock<Mutex<System>> = LazyLock::new(|| {
    Mutex::new(System::new_with_specifics(
        RefreshKind::new()
            .with_cpu(CpuRefreshKind::everything())
            .with_memory(sysinfo::MemoryRefreshKind::everything())
    ))
});

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
    
    let cpus: Vec<serde_json::Value> = sys.cpus()
        .iter()
        .map(|cpu| serde_json::json!({
            "name": cpu.brand(),
            "usage": cpu.cpu_usage(),
            "frequency": cpu.frequency()
        }))
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
    
    let interfaces: Vec<serde_json::Value> = networks
        .list()
        .iter()
        .map(|(name, data): (&String, &sysinfo::NetworkData)| {
            serde_json::json!({
                "name": name,
                "bytes_received": data.total_received(),
                "bytes_sent": data.total_transmitted()
            })
        })
        .collect();
    
    Ok(serde_json::json!({
        "interface_count": interfaces.len(),
        "interfaces": interfaces
    }))
}

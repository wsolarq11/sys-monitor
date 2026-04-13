use sysinfo::{System, Disks};
use tauri::command;
use crate::models::metrics::SystemMetric;
use crate::error::AppError;

fn get_global_cpu_usage(sys: &System) -> f32 {
    if sys.cpus().is_empty() {
        return 0.0;
    }
    sys.cpus().iter().map(|cpu| cpu.cpu_usage()).sum::<f32>() / sys.cpus().len() as f32
}

#[command]
pub fn get_system_metrics() -> Result<SystemMetric, AppError> {
    let mut sys = System::new_all();
    sys.refresh_all();
    sys.refresh_cpu();

    let total_memory = sys.total_memory() as f64;
    let used_memory = sys.used_memory() as f64;
    
    // Get disk information using Disks struct
    let disks = Disks::new_with_refreshed_list();
    let total_disk = disks.iter().map(|d| d.total_space()).sum::<u64>() as f64;
    let available_disk = disks.iter().map(|d| d.available_space()).sum::<u64>() as f64;
    let used_disk = total_disk - available_disk;

    Ok(SystemMetric {
        id: None,
        timestamp: chrono::Utc::now().timestamp(),
        cpu_usage: get_global_cpu_usage(&sys) as f64,
        memory_usage: used_memory,
        memory_total: Some(total_memory),
        disk_usage: Some(used_disk),
        disk_total: Some(total_disk),
    })
}

#[command]
pub fn get_cpu_info() -> Result<serde_json::Value, AppError> {
    let mut sys = System::new_all();
    sys.refresh_cpu();

    let cores: Vec<serde_json::Value> = sys.cpus().iter().map(|cpu| {
        serde_json::json!({
            "name": cpu.name(),
            "brand": cpu.brand(),
            "frequency": cpu.frequency(),
            "usage": cpu.cpu_usage()
        })
    }).collect();

    Ok(serde_json::json!({
        "cores": cores,
        "global_usage": get_global_cpu_usage(&sys) as f64
    }))
}

#[command]
pub fn get_memory_info() -> Result<serde_json::Value, AppError> {
    let mut sys = System::new_all();
    sys.refresh_memory();

    Ok(serde_json::json!({
        "total": sys.total_memory(),
        "used": sys.used_memory(),
        "free": sys.free_memory(),
        "available": sys.available_memory(),
        "usage_percent": (sys.used_memory() as f64 / sys.total_memory() as f64) * 100.0
    }))
}

#[command]
pub fn get_disk_info() -> Result<serde_json::Value, AppError> {
    use sysinfo::Disk;
    
    let disks = Disks::new_with_refreshed_list();

    let disks_data: Vec<serde_json::Value> = disks.iter().map(|disk: &Disk| {
        serde_json::json!({
            "mount_point": disk.mount_point().to_string_lossy(),
            "total_bytes": disk.total_space(),
            "available_bytes": disk.available_space(),
            "used_bytes": disk.total_space() - disk.available_space(),
            "usage_percent": ((disk.total_space() - disk.available_space()) as f64 / disk.total_space() as f64) * 100.0,
            "disk_type": match disk.kind() {
                sysinfo::DiskKind::SSD => "SSD",
                sysinfo::DiskKind::HDD => "HDD",
                _ => "Unknown"
            }
        })
    }).collect();

    Ok(serde_json::json!({
        "disks": disks_data
    }))
}

#[command]
pub fn get_network_info() -> Result<serde_json::Value, AppError> {
    // Network monitoring requires additional setup in sysinfo 0.30+
    // For now, return basic placeholder data
    Ok(serde_json::json!({
        "interfaces": [],
        "note": "Network monitoring requires additional setup"
    }))
}

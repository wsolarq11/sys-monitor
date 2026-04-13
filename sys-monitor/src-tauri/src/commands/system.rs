use sysinfo::System;
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

    Ok(SystemMetric {
        id: None,
        timestamp: chrono::Utc::now().timestamp(),
        cpu_usage: get_global_cpu_usage(&sys) as f64,
        memory_usage: sys.used_memory() as f64,
        disk_usage: None,
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

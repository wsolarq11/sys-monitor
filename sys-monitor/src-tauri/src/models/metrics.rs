use serde::{Deserialize, Serialize};

/// Core system metrics (CPU, Memory, Disk summary)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SystemMetric {
    pub id: Option<i64>,
    pub timestamp: i64,
    pub cpu_usage: f64,
    pub memory_usage: f64,
    pub memory_total: Option<f64>,
    pub disk_usage: Option<f64>,
    pub disk_total: Option<f64>,
}

/// Per-core CPU usage
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CpuCoreMetric {
    pub id: Option<i64>,
    pub metric_id: i64,
    pub core_name: String,
    pub usage_percent: f64,
}

/// Per-disk usage statistics
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DiskMetric {
    pub id: Option<i64>,
    pub metric_id: i64,
    pub mount_point: String,
    pub total_bytes: u64,
    pub available_bytes: u64,
    pub disk_type: Option<String>,
}

/// Network interface statistics
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NetworkMetric {
    pub id: Option<i64>,
    pub timestamp: i64,
    pub interface_name: String,
    pub bytes_sent: u64,
    pub bytes_received: u64,
}

/// Process information for monitoring
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProcessInfo {
    pub pid: u32,
    pub name: String,
    pub cpu_usage: f32,
    pub memory: u64,  // bytes
    pub memory_percent: f32,
}

/// Alert system
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Alert {
    pub id: Option<i64>,
    pub timestamp: i64,
    pub metric_type: String,
    pub metric_name: String,
    pub threshold_value: f64,
    pub actual_value: f64,
    pub acknowledged: bool,
}

/// Settings key-value store
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Setting {
    pub key: String,
    pub value: String,
}

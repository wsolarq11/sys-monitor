use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SystemMetric {
    pub id: Option<i64>,
    pub timestamp: i64,
    pub cpu_usage: f64,
    pub memory_usage: f64,
    pub disk_usage: Option<f64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NetworkMetric {
    pub id: Option<i64>,
    pub timestamp: i64,
    pub interface_name: String,
    pub bytes_sent: u64,
    pub bytes_received: u64,
}

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

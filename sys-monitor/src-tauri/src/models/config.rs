use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Setting {
    pub key: String,
    pub value: String,
    pub updated_at: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AppConfig {
    pub monitoring_interval: u64,
    pub retention_days: u32,
    pub alert_thresholds: AlertThresholds,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AlertThresholds {
    pub cpu_usage: f64,
    pub memory_usage: f64,
    pub disk_usage: f64,
}

impl Default for AppConfig {
    fn default() -> Self {
        Self {
            monitoring_interval: 2000, // 2 seconds
            retention_days: 30,
            alert_thresholds: AlertThresholds {
                cpu_usage: 80.0,
                memory_usage: 80.0,
                disk_usage: 90.0,
            },
        }
    }
}

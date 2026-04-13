use tauri::command;
use crate::db::repository::DatabaseRepository;
use crate::models::metrics::SystemMetric;
use crate::error::AppError;

#[command]
pub fn save_system_metric(metric: SystemMetric) -> Result<(), AppError> {
    let repo = DatabaseRepository::new("sysmonitor.db")
        .map_err(|e| AppError::System(e.to_string()))?;
    
    repo.init()
        .map_err(|e| AppError::Database(e))?;
    
    repo.insert_system_metric(&metric)
        .map_err(|e| AppError::Database(e))?;
    
    Ok(())
}

#[command]
pub fn get_recent_metrics(limit: u32) -> Result<Vec<SystemMetric>, AppError> {
    let repo = DatabaseRepository::new("sysmonitor.db")
        .map_err(|e| AppError::System(e.to_string()))?;
    
    repo.init()
        .map_err(|e| AppError::Database(e))?;
    
    repo.get_recent_metrics(limit)
        .map_err(|e| AppError::Database(e))
}

use tauri::command;
use crate::error::AppError;
use std::path::Path;

#[command]
pub fn get_db_path() -> Result<String, AppError> {
    // 使用当前工作目录来存储数据库文件
    let current_dir = std::env::current_dir()
        .map_err(|e| AppError::file_system(format!("Failed to get current directory: {}", e)))?;
    
    let db_path = current_dir.join("sysmonitor.db");
    
    println!("Database path: {}", db_path.display());
    
    Ok(db_path.to_string_lossy().to_string())
}

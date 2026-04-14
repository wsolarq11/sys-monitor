use crate::db::repository::DatabaseRepository;
use crate::models::folder::{FileTypeStat, FolderItem, FolderScan};
use crate::utils::file_types::classify_file;
use crate::error::AppError;
use crate::logger;
use std::path::Path;
use std::time::Instant;
use tauri::{Manager, Runtime};
use tauri_plugin_dialog::DialogExt;

#[tauri::command]
pub async fn scan_folder<R: Runtime>(_app: tauri::AppHandle<R>, path: String, db_path: String) -> Result<FolderScan, AppError> {
    logger::log_info(&format!("scan_folder 命令被调用 - 路径：{}, 数据库路径：{}", path, db_path));
    
    let path_clean = path.trim().to_string();
    
    if path_clean.is_empty() {
        logger::log_error("扫描路径为空");
        return Err(AppError::invalid_parameter("Path cannot be empty"));
    }
    
    if !Path::new(&path_clean).exists() {
        logger::log_error(&format!("路径不存在：{}", path_clean));
        return Err(AppError::file_system(format!("Path does not exist: {}", path_clean)));
    }

    if !Path::new(&path_clean).is_dir() {
        logger::log_error(&format!("路径不是目录：{}", path_clean));
        return Err(AppError::file_system(format!("Path is not a directory: {}", path_clean)));
    }

    logger::log_info(&format!("开始创建数据库连接：{}", db_path));
    let mut repo = DatabaseRepository::new(&db_path)
        .map_err(|e| {
            logger::log_error(&format!("数据库连接失败：{}", e));
            AppError::database(format!("Database connection failed: {}", e))
        })?;
    logger::log_info("数据库连接创建成功");

    let start_time = Instant::now();

    let mut total_size: u64 = 0;
    let mut file_count: u64 = 0;
    let mut folder_count: u64 = 0;

    let mut file_type_map: std::collections::HashMap<String, u64> = std::collections::HashMap::new();
    let mut folder_items: Vec<FolderItem> = Vec::new();

    logger::log_info(&format!("开始扫描文件夹：{}", path));

    let mut processed_count = 0;
    for entry in walkdir::WalkDir::new(&path).into_iter().filter_map(|e| e.ok()) {
        processed_count += 1;
        if processed_count % 1000 == 0 {
            logger::log_debug(&format!("已处理 {} 个项目...", processed_count));
        }
        
        let metadata = match entry.metadata() {
            Ok(m) => m,
            Err(e) => {
                logger::log_warn(&format!("无法获取文件元数据 {}: {}", entry.path().display(), e));
                continue;
            }
        };

        if metadata.is_file() {
            file_count += 1;
            total_size += metadata.len();

            let file_type = classify_file(entry.path().to_string_lossy().as_ref());
            *file_type_map.entry(file_type.clone()).or_insert(0) += 1;

            if let Some(ext) = entry.path().extension().and_then(|e| e.to_str()) {
                let item = FolderItem {
                    id: None,
                    scan_id: 0,
                    path: entry.path().to_string_lossy().to_string(),
                    name: entry.file_name().to_string_lossy().to_string(),
                    size: metadata.len(),
                    item_type: "file".to_string(),
                    extension: Some(ext.to_string()),
                    parent_path: entry.path().parent().map(|p| p.to_string_lossy().to_string()),
                };
                folder_items.push(item);
            }
        } else if metadata.is_dir() {
            folder_count += 1;
        }
    }

    logger::log_info(&format!("扫描完成，收集到 {} 个文件项，{} 个文件夹，总大小：{} 字节", folder_items.len(), folder_count, total_size));

    logger::log_info("开始使用事务批量插入数据...");
    
    let file_type_stats: Vec<FileTypeStat> = file_type_map
        .into_iter()
        .map(|(file_type, count)| FileTypeStat {
            id: None,
            scan_id: 0,
            file_type,
            count,
            total_size: 0,
        })
        .collect();

    let scan_duration_ms = start_time.elapsed().as_millis() as u64;
    let scan_timestamp = start_time.elapsed().as_millis() as i64;
    

    let scan_id = repo.create_scan_with_items(
        &path,
        scan_timestamp,
        &folder_items,
        &file_type_stats,
        total_size,
        file_count,
        folder_count,
        scan_duration_ms,
    )
    .map_err(|e| {
        logger::log_error(&format!("事务批量插入失败：{}", e));
        AppError::database(e.to_string())
    })?;
    
    logger::log_info(&format!("事务批量插入完成，扫描 ID: {}", scan_id));

    let result = FolderScan {
        id: Some(scan_id),
        path,
        scan_timestamp,
        total_size,
        file_count,
        folder_count,
        scan_duration_ms: Some(scan_duration_ms),
    };

    logger::log_info(&format!("scan_folder 返回结果：{:?}", result));
    Ok(result)
}

#[tauri::command]
pub fn get_folder_scans<R: Runtime>(_app: tauri::AppHandle<R>, path: String, limit: i64, db_path: String) -> Result<Vec<FolderScan>, AppError> {
    let repo = DatabaseRepository::new(&db_path)
        .map_err(|e| AppError::database(e.to_string()))?;
    repo.get_folder_scans(&path, limit)
        .map_err(|e| AppError::database(e.to_string()))
}

#[tauri::command]
pub fn get_folder_items<R: Runtime>(_app: tauri::AppHandle<R>, scan_id: i64, db_path: String) -> Result<Vec<FolderItem>, AppError> {
    let repo = DatabaseRepository::new(&db_path)
        .map_err(|e| AppError::database(e.to_string()))?;
    repo.get_folder_items(scan_id)
        .map_err(|e| AppError::database(e.to_string()))
}

#[tauri::command]
pub fn get_file_type_stats<R: Runtime>(_app: tauri::AppHandle<R>, scan_id: i64, db_path: String) -> Result<Vec<FileTypeStat>, AppError> {
    let repo = DatabaseRepository::new(&db_path)
        .map_err(|e| AppError::database(e.to_string()))?;
    repo.get_file_type_stats(scan_id)
        .map_err(|e| AppError::database(e.to_string()))
}

#[tauri::command]
pub fn delete_folder_scan<R: Runtime>(_app: tauri::AppHandle<R>, scan_id: i64, db_path: String) -> Result<(), AppError> {
    let repo = DatabaseRepository::new(&db_path)
        .map_err(|e| AppError::database(e.to_string()))?;
    repo.delete_folder_scan(scan_id)
        .map_err(|e| AppError::database(e.to_string()))?;
    Ok(())
}

#[tauri::command]
pub async fn select_folder<R: Runtime>(app: tauri::AppHandle<R>) -> Result<String, String> {
    let path = app.dialog().file().blocking_pick_folder();
    match path {
        Some(p) => Ok(p.to_string()),
        None => Err("No folder selected".to_string()),
    }
}

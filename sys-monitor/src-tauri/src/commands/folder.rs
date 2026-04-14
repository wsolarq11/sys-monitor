use crate::db::repository::DatabaseRepository;
use crate::models::folder::{FileTypeStat, FolderItem, FolderScan};
use crate::utils::file_types::classify_file;
use crate::error::AppError;
use crate::logger;
use std::path::Path;
use std::time::Instant;
use tauri::{Manager, Runtime};
use tokio::fs;
use tauri_plugin_dialog::DialogExt;

#[tauri::command]
pub async fn scan_folder<R: Runtime>(_app: tauri::AppHandle<R>, path: String, db_path: String) -> Result<FolderScan, AppError> {
    logger::log_info(&format!("scan_folder 命令被调用 - 路径: {}, 数据库路径: {}", path, db_path));
    
    let path_clean = path.trim().to_string();
    
    if path_clean.is_empty() {
        logger::log_error("扫描路径为空");
        return Err(AppError::System("Path cannot be empty".to_string()));
    }
    
    if !Path::new(&path_clean).exists() {
        logger::log_error(&format!("路径不存在: {}", path_clean));
        return Err(AppError::System(format!("Path does not exist: {}", path_clean)));
    }

    if !Path::new(&path_clean).is_dir() {
        logger::log_error(&format!("路径不是目录: {}", path_clean));
        return Err(AppError::System(format!("Path is not a directory: {}", path_clean)));
    }

    logger::log_info(&format!("开始创建数据库连接: {}", db_path));
    let repo = DatabaseRepository::new(&db_path)
        .map_err(|e| {
            logger::log_error(&format!("数据库连接失败: {}", e));
            AppError::System(format!("Database connection failed: {}", e))
        })?;
    logger::log_info("数据库连接创建成功");

    let start_time = Instant::now();

    let mut total_size: u64 = 0;
    let mut file_count: u64 = 0;
    let mut folder_count: u64 = 0;

    let mut file_type_stats: std::collections::HashMap<String, u64> = std::collections::HashMap::new();

    logger::log_info("开始创建文件夹扫描记录...");
    let scan_id = repo.create_folder_scan(&path, start_time.elapsed().as_millis() as i64)
        .map_err(|e| {
            logger::log_error(&format!("创建文件夹扫描记录失败: {}", e));
            AppError::System(e.to_string())
        })?;
    logger::log_info(&format!("文件夹扫描记录创建成功，ID: {}", scan_id));

    logger::log_info(&format!("开始扫描文件夹: {}", path));

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
                continue; // 跳过无法访问的文件
            }
        };

        if metadata.is_file() {
            file_count += 1;
            total_size += metadata.len();

            let file_type = classify_file(entry.path().to_string_lossy().as_ref());
            *file_type_stats.entry(file_type.clone()).or_insert(0) += 1;

            if let Some(ext) = entry.path().extension().and_then(|e| e.to_str()) {
                let item = FolderItem {
                    id: None,
                    scan_id,
                    path: entry.path().to_string_lossy().to_string(),
                    name: entry.file_name().to_string_lossy().to_string(),
                    size: metadata.len(),
                    item_type: "file".to_string(),
                    extension: Some(ext.to_string()),
                    parent_path: entry.path().parent().map(|p| p.to_string_lossy().to_string()),
                };
                if let Err(e) = repo.insert_folder_item(&item) {
                    logger::log_warn(&format!("插入文件夹项目失败 {}: {}", entry.path().display(), e));
                    // 继续处理其他文件
                }
            }
        } else if metadata.is_dir() {
            folder_count += 1;
        }
    }

    logger::log_info(&format!("扫描完成: {} 个文件, {} 个文件夹, 总大小: {} 字节", file_count, folder_count, total_size));

    logger::log_info("开始保存文件类型统计...");
    for (file_type, count) in file_type_stats {
        let stat = FileTypeStat {
            id: None,
            scan_id,
            file_type: file_type.clone(),
            count,
            total_size: 0,
        };
        if let Err(e) = repo.insert_file_type_stat(&stat) {
            logger::log_warn(&format!("插入文件类型统计失败 {}: {}", file_type, e));
        }
    }

    logger::log_info("开始更新文件夹扫描结果...");
    repo.update_folder_scan(scan_id, total_size, file_count, folder_count, start_time.elapsed().as_millis() as u64)
        .map_err(|e| {
            logger::log_error(&format!("更新文件夹扫描失败: {}", e));
            AppError::System(e.to_string())
        })?;
    logger::log_info("文件夹扫描更新成功");

    let result = FolderScan {
        id: Some(scan_id),
        path,
        scan_timestamp: start_time.elapsed().as_millis() as i64,
        total_size,
        file_count,
        folder_count,
        scan_duration_ms: Some(start_time.elapsed().as_millis() as u64),
    };

    logger::log_info(&format!("scan_folder 返回结果: {:?}", result));
    Ok(result)
}

#[tauri::command]
pub fn get_folder_scans<R: Runtime>(_app: tauri::AppHandle<R>, path: String, limit: i64, db_path: String) -> Result<Vec<FolderScan>, AppError> {
    println!("get_folder_scans called with path: {}, limit: {}, db_path: {}", path, limit, db_path);
    let repo = DatabaseRepository::new(&db_path)
        .map_err(|e| AppError::System(e.to_string()))?;
    let result = repo.get_folder_scans(&path, limit)
        .map_err(|e| AppError::System(e.to_string()));
    println!("get_folder_scans returning: {:?}", result);
    result
}

#[tauri::command]
pub fn get_folder_items<R: Runtime>(_app: tauri::AppHandle<R>, scan_id: i64, db_path: String) -> Result<Vec<FolderItem>, AppError> {
    let repo = DatabaseRepository::new(&db_path)
        .map_err(|e| AppError::System(e.to_string()))?;
    repo.get_folder_items(scan_id)
        .map_err(|e| AppError::System(e.to_string()))
}

#[tauri::command]
pub fn get_file_type_stats<R: Runtime>(_app: tauri::AppHandle<R>, scan_id: i64, db_path: String) -> Result<Vec<FileTypeStat>, AppError> {
    let repo = DatabaseRepository::new(&db_path)
        .map_err(|e| AppError::System(e.to_string()))?;
    repo.get_file_type_stats(scan_id)
        .map_err(|e| AppError::System(e.to_string()))
}

#[tauri::command]
pub fn delete_folder_scan<R: Runtime>(_app: tauri::AppHandle<R>, scan_id: i64, db_path: String) -> Result<(), AppError> {
    let repo = DatabaseRepository::new(&db_path)
        .map_err(|e| AppError::System(e.to_string()))?;
    repo.delete_folder_scan(scan_id)
        .map_err(|e| AppError::System(e.to_string()))?;
    Ok(())
}

#[tauri::command]
pub async fn select_folder<R: Runtime>(app: tauri::AppHandle<R>) -> Result<String, String> {
    // 使用阻塞版本，确保对话框能正常工作
    let path = app.dialog().file().blocking_pick_folder();
    match path {
        Some(p) => Ok(p.to_string()),
        None => Err("No folder selected".to_string()),
    }
}

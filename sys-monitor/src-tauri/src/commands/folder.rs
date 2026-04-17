use crate::db::repository::DatabaseRepository;
use crate::error::AppError;
use crate::logger;
use crate::models::folder::{FileTypeStat, FolderItem, FolderScan, WatchedFolder};
use crate::services::file_watcher_service::FileWatcherService;
use crate::utils::file_types::classify_file;
use std::path::Path;
use std::sync::Arc;
use std::time::Instant;
use tauri::{Manager, Runtime, State};
use tauri_plugin_dialog::DialogExt;

#[tauri::command]
pub async fn scan_folder<R: Runtime>(
    _app: tauri::AppHandle<R>,
    path: String,
    db_path: String,
) -> Result<FolderScan, AppError> {
    logger::log_info(&format!(
        "scan_folder 命令被调用 - 路径：{}, 数据库路径：{}",
        path, db_path
    ));

    let path_clean = path.trim().to_string();

    if path_clean.is_empty() {
        logger::log_error("扫描路径为空");
        return Err(AppError::invalid_parameter("Path cannot be empty"));
    }

    if !Path::new(&path_clean).exists() {
        logger::log_error(&format!("路径不存在：{}", path_clean));
        return Err(AppError::file_system(format!(
            "Path does not exist: {}",
            path_clean
        )));
    }

    if !Path::new(&path_clean).is_dir() {
        logger::log_error(&format!("路径不是目录：{}", path_clean));
        return Err(AppError::file_system(format!(
            "Path is not a directory: {}",
            path_clean
        )));
    }

    logger::log_info(&format!("开始创建数据库连接：{}", db_path));
    let mut repo = DatabaseRepository::new(&db_path).map_err(|e| {
        logger::log_error(&format!("数据库连接失败：{}", e));
        AppError::database(format!("Database connection failed: {}", e))
    })?;
    logger::log_info("数据库连接创建成功");

    let start_time = Instant::now();

    let mut total_size: u64 = 0;
    let mut file_count: u64 = 0;
    let mut folder_count: u64 = 0;

    let mut file_type_map: std::collections::HashMap<String, u64> =
        std::collections::HashMap::new();
    let mut folder_items: Vec<FolderItem> = Vec::new();

    logger::log_info(&format!("开始扫描文件夹：{}", path));

    let mut processed_count = 0;
    for entry in walkdir::WalkDir::new(&path)
        .into_iter()
        .filter_map(|e| e.ok())
    {
        processed_count += 1;
        if processed_count % 1000 == 0 {
            logger::log_debug(&format!("已处理 {} 个项目...", processed_count));
        }

        let metadata = match entry.metadata() {
            Ok(m) => m,
            Err(e) => {
                logger::log_warn(&format!(
                    "无法获取文件元数据 {}: {}",
                    entry.path().display(),
                    e
                ));
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
                    parent_path: entry
                        .path()
                        .parent()
                        .map(|p| p.to_string_lossy().to_string()),
                };
                folder_items.push(item);
            }
        } else if metadata.is_dir() {
            folder_count += 1;
        }
    }

    logger::log_info(&format!(
        "扫描完成，收集到 {} 个文件项，{} 个文件夹，总大小：{} 字节",
        folder_items.len(),
        folder_count,
        total_size
    ));

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

    let scan_id = repo
        .create_scan_with_items(
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
pub fn get_folder_scans<R: Runtime>(
    _app: tauri::AppHandle<R>,
    path: String,
    limit: i64,
    db_path: String,
) -> Result<Vec<FolderScan>, AppError> {
    let repo = DatabaseRepository::new(&db_path).map_err(|e| AppError::database(e.to_string()))?;
    repo.get_folder_scans(&path, limit)
        .map_err(|e| AppError::database(e.to_string()))
}

#[tauri::command]
pub fn get_folder_items<R: Runtime>(
    _app: tauri::AppHandle<R>,
    scan_id: i64,
    db_path: String,
) -> Result<Vec<FolderItem>, AppError> {
    let repo = DatabaseRepository::new(&db_path).map_err(|e| AppError::database(e.to_string()))?;
    repo.get_folder_items(scan_id)
        .map_err(|e| AppError::database(e.to_string()))
}

#[tauri::command]
pub fn get_file_type_stats<R: Runtime>(
    _app: tauri::AppHandle<R>,
    scan_id: i64,
    db_path: String,
) -> Result<Vec<FileTypeStat>, AppError> {
    let repo = DatabaseRepository::new(&db_path).map_err(|e| AppError::database(e.to_string()))?;
    repo.get_file_type_stats(scan_id)
        .map_err(|e| AppError::database(e.to_string()))
}

#[tauri::command]
pub fn delete_folder_scan<R: Runtime>(
    _app: tauri::AppHandle<R>,
    scan_id: i64,
    db_path: String,
) -> Result<(), AppError> {
    let repo = DatabaseRepository::new(&db_path).map_err(|e| AppError::database(e.to_string()))?;
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

// ========== Watched Folders Commands ==========

#[tauri::command]
pub async fn add_watched_folder<R: Runtime>(
    app: tauri::AppHandle<R>,
    path: String,
    alias: Option<String>,
    db_path: String,
) -> Result<i64, AppError> {
    logger::log_info(&format!(
        "add_watched_folder - 路径: {}, 别名: {:?}",
        path, alias
    ));

    let repo = DatabaseRepository::new(&db_path).map_err(|e| {
        logger::log_error(&format!("数据库连接失败: {}", e));
        AppError::database(e.to_string())
    })?;

    let folder_id = repo
        .insert_watched_folder(&path, alias.as_deref())
        .map_err(|e| {
            logger::log_error(&format!("添加监控文件夹失败: {}", e));
            AppError::database(e.to_string())
        })?;

    // 获取文件夹信息并启动监听
    if let Ok(folders) = repo.get_all_watched_folders() {
        if let Some(folder_info) = folders.iter().find(|f| f.id == folder_id) {
            let watcher_service: State<Arc<FileWatcherService>> = app.state();
            if let Err(e) = watcher_service.add_watch(folder_info).await {
                logger::log_warn(&format!("启动文件监听失败: {}", e));
            }
        }
    }

    logger::log_info(&format!("成功添加监控文件夹, ID: {}", folder_id));
    Ok(folder_id)
}

#[tauri::command]
pub async fn remove_watched_folder<R: Runtime>(
    app: tauri::AppHandle<R>,
    folder_id: i64,
    db_path: String,
) -> Result<(), AppError> {
    logger::log_info(&format!("remove_watched_folder - ID: {}", folder_id));

    // 先停止文件监听
    let watcher_service: State<Arc<FileWatcherService>> = app.state();
    if let Err(e) = watcher_service.remove_watch(folder_id).await {
        logger::log_warn(&format!("停止文件监听失败: {}", e));
    }

    let repo = DatabaseRepository::new(&db_path).map_err(|e| AppError::database(e.to_string()))?;

    repo.delete_watched_folder(folder_id)
        .map_err(|e| AppError::database(e.to_string()))?;

    logger::log_info(&format!("成功移除监控文件夹, ID: {}", folder_id));
    Ok(())
}

#[tauri::command]
pub async fn list_watched_folders<R: Runtime>(
    _app: tauri::AppHandle<R>,
    db_path: String,
) -> Result<Vec<WatchedFolder>, AppError> {
    let repo = DatabaseRepository::new(&db_path).map_err(|e| AppError::database(e.to_string()))?;

    let folders = repo
        .get_all_watched_folders()
        .map_err(|e| AppError::database(e.to_string()))?;

    Ok(folders)
}

#[tauri::command]
pub async fn toggle_watched_folder_active<R: Runtime>(
    app: tauri::AppHandle<R>,
    folder_id: i64,
    is_active: bool,
    db_path: String,
) -> Result<bool, AppError> {
    logger::log_info(&format!(
        "toggle_watched_folder_active - ID: {}, 新状态: {}",
        folder_id, is_active
    ));

    // 获取文件夹信息
    let repo = DatabaseRepository::new(&db_path).map_err(|e| {
        logger::log_error(&format!("数据库连接失败: {}", e));
        AppError::database(e.to_string())
    })?;

    let folders = repo.get_all_watched_folders().map_err(|e| {
        logger::log_error(&format!("获取监控文件夹列表失败: {}", e));
        AppError::database(e.to_string())
    })?;

    let folder_info = folders.iter().find(|f| f.id == folder_id).ok_or_else(|| {
        logger::log_error(&format!("未找到文件夹 ID: {}", folder_id));
        AppError::invalid_parameter(format!("Folder with id {} not found", folder_id))
    })?;

    // 更新数据库状态
    repo.update_watched_folder_status(folder_id, is_active)
        .map_err(|e| {
            logger::log_error(&format!("更新文件夹状态失败: {}", e));
            AppError::database(e.to_string())
        })?;

    // 根据新状态启动或停止文件监听
    let watcher_service: State<Arc<FileWatcherService>> = app.state();

    if is_active {
        // 设为 active，启动监听
        if let Err(e) = watcher_service.add_watch(folder_info).await {
            logger::log_warn(&format!("启动文件监听失败: {}", e));
            return Err(AppError::file_system(format!(
                "Failed to start file watcher: {}",
                e
            )));
        }
        logger::log_info(&format!("成功启动文件夹监听, ID: {}", folder_id));
    } else {
        // 设为 inactive，停止监听
        if let Err(e) = watcher_service.remove_watch(folder_id).await {
            logger::log_warn(&format!("停止文件监听失败: {}", e));
        }
        logger::log_info(&format!("成功停止文件夹监听, ID: {}", folder_id));
    }

    logger::log_info(&format!(
        "成功切换文件夹状态, ID: {}, 新状态: {}",
        folder_id, is_active
    ));
    Ok(true)
}

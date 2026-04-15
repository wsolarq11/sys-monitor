#[allow(unused_imports)]
pub mod commands;
#[allow(unused_imports)]
pub mod db;
#[allow(unused_imports)]
pub mod error;
#[allow(unused_imports)]
pub mod error_handling;
#[allow(unused_imports)]
pub mod logger;
#[allow(unused_imports)]
pub mod models;
#[allow(unused_imports)]
pub mod utils;
#[allow(unused_imports)]
pub mod services {
    pub mod file_watcher_service;
}

use std::env;
use std::sync::Arc;

use commands::database::get_db_path;
use commands::folder::{
    add_watched_folder, delete_folder_scan, get_file_type_stats, get_folder_items,
    get_folder_scans, list_watched_folders, remove_watched_folder, scan_folder, select_folder,
    toggle_watched_folder_active,
};
use commands::system::{
    get_cpu_info, get_disk_info, get_memory_info, get_network_info, get_system_metrics,
};
use error::ErrorMonitor;
use error_handling::ErrorHandler;
use services::file_watcher_service::FileWatcherService;
use tauri::Manager;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    // 初始化Sentry错误追踪
    let _sentry_guard = sentry::init((
        env::var("SENTRY_DSN").unwrap_or_else(|_| "".to_string()),
        sentry::ClientOptions {
            release: sentry::release_name!(),
            environment: Some(
                env::var("SENTRY_ENVIRONMENT")
                    .unwrap_or_else(|_| "development".to_string())
                    .into(),
            ),
            debug: env::var("SENTRY_DEBUG")
                .map(|v| v == "true")
                .unwrap_or(false),
            ..Default::default()
        },
    ));

    // 设置自定义panic处理器
    std::panic::set_hook(Box::new(|info| {
        ErrorHandler::handle_panic(info);
    }));

    // 初始化错误监控器
    let _error_monitor = ErrorMonitor::new();

    // 初始化日志系统
    if let Err(e) = logger::init_logger() {
        ErrorHandler::handle_error(&e, "初始化日志系统");
    }

    logger::log_info("SysMonitor 应用程序启动");
    sentry::capture_message("SysMonitor 应用程序启动", sentry::Level::Info);

    // 记录启动统计
    ErrorHandler::track_error_metrics("app_start", "info");

    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_notification::init())
        .setup(|app| {
            // 初始化文件监听服务
            let (watcher_service, event_rx) = FileWatcherService::new(app.handle().clone());
            let watcher_arc = Arc::new(watcher_service);

            // 管理状态
            app.manage(watcher_arc.clone());

            // 启动事件处理循环(5秒防抖聚合)
            let watcher_for_spawn = watcher_arc.clone();
            tokio::spawn(async move {
                watcher_for_spawn.start_event_processor(event_rx, 5).await;
            });

            // 异步初始化: 从数据库加载所有活跃的监控文件夹并启动监听
            let watcher_for_init = watcher_arc.clone();
            let app_handle = app.handle().clone();
            tokio::spawn(async move {
                initialize_watched_folders(watcher_for_init, app_handle).await;
            });

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            get_system_metrics,
            get_cpu_info,
            get_memory_info,
            get_disk_info,
            get_network_info,
            get_db_path,
            scan_folder,
            get_folder_scans,
            get_folder_items,
            get_file_type_stats,
            delete_folder_scan,
            select_folder,
            add_watched_folder,
            remove_watched_folder,
            list_watched_folders,
            toggle_watched_folder_active,
        ])
        .run(tauri::generate_context!())
        .unwrap_or_else(|e| {
            logger::log_error(&format!("Failed to run Tauri application: {}", e));
            // 使用更优雅的错误处理，而不是直接panic
            eprintln!("Failed to run Tauri application: {}", e);
            std::process::exit(1);
        });
}

/// 初始化所有活跃的监控文件夹监听
async fn initialize_watched_folders(
    watcher_service: Arc<FileWatcherService>,
    _app_handle: tauri::AppHandle,
) {
    use db::repository::DatabaseRepository;
    use std::env;

    let db_path = env::var("DB_PATH").unwrap_or_else(|_| "data.db".to_string());

    // 创建数据库仓库实例
    let repo = match DatabaseRepository::new(&db_path) {
        Ok(repo) => repo,
        Err(e) => {
            logger::log_error(&format!(
                "初始化文件监听: 无法打开数据库 ({}): {}",
                db_path, e
            ));
            return;
        }
    };

    // 查询所有 is_active=true 的监控文件夹
    let watched_folders = match repo.get_all_watched_folders() {
        Ok(folders) => folders,
        Err(e) => {
            logger::log_error(&format!("初始化文件监听: 查询监控文件夹失败: {}", e));
            return;
        }
    };

    let active_folders: Vec<_> = watched_folders.iter().filter(|f| f.is_active).collect();

    if active_folders.is_empty() {
        logger::log_info("初始化文件监听: 没有活跃的监控文件夹");
        return;
    }

    logger::log_info(&format!(
        "初始化文件监听: 找到 {} 个活跃监控文件夹",
        active_folders.len()
    ));

    // 对每个活跃文件夹启动监听,单个失败不影响其他
    let mut success_count = 0;
    let mut failure_count = 0;

    for folder in &active_folders {
        match watcher_service.add_watch(folder).await {
            Ok(()) => {
                success_count += 1;
                logger::log_info(&format!(
                    "初始化文件监听: 成功启动监听 [id={}] {}",
                    folder.id, folder.path
                ));
            }
            Err(e) => {
                failure_count += 1;
                logger::log_error(&format!(
                    "初始化文件监听: 启动监听失败 [id={}] {}: {}",
                    folder.id, folder.path, e
                ));
            }
        }
    }

    logger::log_info(&format!(
        "初始化文件监听完成: 成功 {}, 失败 {}",
        success_count, failure_count
    ));
}

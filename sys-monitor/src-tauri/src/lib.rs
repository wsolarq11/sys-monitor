#[allow(unused_imports)]
pub mod commands;
#[allow(unused_imports)]
pub mod db;
#[allow(unused_imports)]
pub mod models;
#[allow(unused_imports)]
pub mod error;
#[allow(unused_imports)]
pub mod utils;
#[allow(unused_imports)]
pub mod logger;
#[allow(unused_imports)]
pub mod error_handling;
#[allow(unused_imports)]
pub mod services;

use std::env;

use commands::system::{get_system_metrics, get_cpu_info, get_memory_info, get_disk_info, get_network_info};
use commands::database::get_db_path;
use commands::folder::{scan_folder, get_folder_scans, get_folder_items, get_file_type_stats, delete_folder_scan, select_folder};
use error_handling::ErrorHandler;
use error::ErrorMonitor;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    // 初始化Sentry错误追踪
    let _sentry_guard = sentry::init((
        env::var("SENTRY_DSN").unwrap_or_else(|_| "".to_string()),
        sentry::ClientOptions {
            release: sentry::release_name!(),
            environment: Some(env::var("SENTRY_ENVIRONMENT").unwrap_or_else(|_| "development".to_string()).into()),
            debug: env::var("SENTRY_DEBUG").map(|v| v == "true").unwrap_or(false),
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
            select_folder
        ])
        .run(tauri::generate_context!())
        .unwrap_or_else(|e| {
            logger::log_error(&format!("Failed to run Tauri application: {}", e));
            // 使用更优雅的错误处理，而不是直接panic
            eprintln!("Failed to run Tauri application: {}", e);
            std::process::exit(1);
        });
}

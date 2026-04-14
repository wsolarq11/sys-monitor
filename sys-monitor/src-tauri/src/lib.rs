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

use commands::system::{get_system_metrics, get_cpu_info, get_memory_info, get_disk_info, get_network_info};
use commands::database::get_db_path;
use commands::folder::{scan_folder, get_folder_scans, get_folder_items, get_file_type_stats, delete_folder_scan, select_folder};

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    // 初始化日志系统
    if let Err(e) = logger::init_logger() {
        eprintln!("Failed to initialize logger: {}", e);
    }
    
    logger::log_info("SysMonitor 应用程序启动");
    
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
            panic!("Failed to run Tauri application: {}", e);
        });
}

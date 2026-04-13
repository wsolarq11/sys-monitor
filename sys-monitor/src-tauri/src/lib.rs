#[allow(unused_imports)]
mod commands;
#[allow(unused_imports)]
mod db;
#[allow(unused_imports)]
mod models;
#[allow(unused_imports)]
mod error;

use commands::system::{get_system_metrics, get_cpu_info, get_memory_info};
use commands::database::{save_system_metric, get_recent_metrics};

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![
            get_system_metrics,
            get_cpu_info,
            get_memory_info,
            save_system_metric,
            get_recent_metrics
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

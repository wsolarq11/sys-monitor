use std::fs::{File, OpenOptions};
use std::io::{self, Write};
use std::path::Path;
use std::sync::Mutex;
use chrono::Local;

static LOG_FILE: Mutex<Option<File>> = Mutex::new(None);

pub fn init_logger() -> io::Result<()> {
    let log_path = "sysmonitor.log";
    
    let file = OpenOptions::new()
        .create(true)
        .append(true)
        .open(log_path)?;
    
    *LOG_FILE.lock().unwrap() = Some(file);
    
    // 直接写入初始化日志，避免递归调用
    let timestamp = Local::now().format("%Y-%m-%d %H:%M:%S%.3f");
    let init_message = format!("[{}] [INFO] === SysMonitor 日志系统初始化 ===\n", timestamp);
    let file_message = format!("[{}] [INFO] 日志文件: {}\n", timestamp, log_path);
    
    // 输出到控制台
    println!("{}", init_message.trim());
    println!("{}", file_message.trim());
    
    // 写入文件
    if let Some(ref mut file) = *LOG_FILE.lock().unwrap() {
        let _ = file.write_all(init_message.as_bytes());
        let _ = file.write_all(file_message.as_bytes());
        let _ = file.flush();
    }
    
    Ok(())
}

fn write_log(level: &str, message: &str) {
    let timestamp = Local::now().format("%Y-%m-%d %H:%M:%S%.3f");
    let log_message = format!("[{}] [{}] {}\n", timestamp, level, message);
    
    // 输出到控制台
    println!("{}", log_message.trim());
    
    // 写入文件
    if let Some(ref mut file) = *LOG_FILE.lock().unwrap() {
        let _ = file.write_all(log_message.as_bytes());
        let _ = file.flush();
    }
}

pub fn log_info(message: &str) {
    write_log("INFO", message);
}

pub fn log_error(message: &str) {
    write_log("ERROR", message);
}

pub fn log_debug(message: &str) {
    write_log("DEBUG", message);
}

pub fn log_warn(message: &str) {
    write_log("WARN", message);
}
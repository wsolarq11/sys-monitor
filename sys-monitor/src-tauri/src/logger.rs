use chrono::{Local, Utc};
use serde_json::json;
use std::fs::{File, OpenOptions};
use std::io::{self, Write};
use std::path::Path;
use std::sync::Mutex;

static LOG_FILE: Mutex<Option<File>> = Mutex::new(None);

pub fn init_logger() -> io::Result<()> {
    let log_path = "sysmonitor.log";

    let file = OpenOptions::new()
        .create(true)
        .append(true)
        .open(log_path)?;

    *LOG_FILE.lock().unwrap() = Some(file);

    // 结构化日志初始化
    let structured_log = json!({
        "timestamp": Utc::now().to_rfc3339(),
        "level": "INFO",
        "message": "SysMonitor 日志系统初始化",
        "app": "sys-monitor",
        "version": env!("CARGO_PKG_VERSION"),
        "log_file": log_path,
        "environment": std::env::var("SENTRY_ENVIRONMENT").unwrap_or_else(|_| "development".to_string())
    });

    // 输出结构化日志到控制台 (Loki兼容格式)
    println!("{}", structured_log);

    // 写入文件
    if let Some(ref mut file) = *LOG_FILE.lock().unwrap() {
        let _ = file.write_all(structured_log.to_string().as_bytes());
        let _ = file.write_all(b"\n");
        let _ = file.flush();
    }

    Ok(())
}

fn write_log(level: &str, message: &str) {
    let timestamp = Utc::now().to_rfc3339();

    // 创建结构化日志
    let structured_log = json!({
        "timestamp": timestamp,
        "level": level,
        "message": message,
        "app": "sys-monitor",
        "version": env!("CARGO_PKG_VERSION"),
        "environment": std::env::var("SENTRY_ENVIRONMENT").unwrap_or_else(|_| "development".to_string()),
        "thread_id": format!("{:?}", std::thread::current().id())
    });

    // 输出结构化日志到控制台 (Loki兼容格式)
    println!("{}", structured_log);

    // 写入文件
    if let Some(ref mut file) = *LOG_FILE.lock().unwrap() {
        let _ = file.write_all(structured_log.to_string().as_bytes());
        let _ = file.write_all(b"\n");
        let _ = file.flush();
    }

    // 根据日志级别发送到Sentry
    match level {
        "ERROR" => {
            sentry::capture_message(&format!("{}: {}", level, message), sentry::Level::Error);
        }
        "WARN" => {
            sentry::capture_message(&format!("{}: {}", level, message), sentry::Level::Warning);
        }
        _ => {}
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

use crate::error::AppError;
use serde::{Deserialize, Serialize};
use std::error::Error;
use std::fmt;

/// 错误处理工具
pub struct ErrorHandler;

impl ErrorHandler {
    /// 处理错误并记录到 Sentry
    pub fn handle_error(error: &dyn Error, context: &str) {
        let error_message = format!("{}: {}", context, error);

        // 记录到日志
        crate::logger::log_error(&error_message);

        // 发送到 Sentry
        sentry::capture_message(&error_message, sentry::Level::Error);

        // 设置错误上下文
        sentry::configure_scope(|scope| {
            scope.set_tag("error_type", "backend_error");
            scope.set_extra("error_context", context.into());
            scope.set_extra("error_message", error.to_string().into());
        });
    }

    /// 处理 panic 并记录到 Sentry
    pub fn handle_panic(info: &std::panic::PanicHookInfo) {
        let panic_message = format!("Panic occurred: {}", info);

        // 记录到日志
        crate::logger::log_error(&panic_message);

        // 发送到 Sentry
        sentry::capture_message(&panic_message, sentry::Level::Fatal);

        // 设置 panic 上下文
        sentry::configure_scope(|scope| {
            scope.set_tag("error_type", "panic");
            scope.set_extra("panic_info", info.to_string().into());
        });
    }

    /// 优雅的错误恢复
    pub fn graceful_recovery(error: &(dyn Error + 'static)) -> Result<(), AppError> {
        // 尝试转换为 AppError
        if let Some(app_error) = error.downcast_ref::<AppError>() {
            match app_error {
                AppError::ResourceLimit(_) => {
                    // 资源不足错误，尝试释放资源
                    Self::release_resources();
                    Err(AppError::resource_limit("资源不足，已尝试释放"))
                }
                AppError::Permission(_) => {
                    // 权限错误，提示用户
                    Err(AppError::permission("权限不足，请检查应用权限"))
                }
                _ => Err(AppError::unknown(error.to_string())),
            }
        } else {
            // 其他错误，转换为 Unknown
            Err(AppError::unknown(error.to_string()))
        }
    }

    /// 释放资源
    fn release_resources() {
        // 清理临时文件
        if let Ok(temp_dir) = std::env::temp_dir().read_dir() {
            for entry in temp_dir.flatten() {
                if let Ok(file_name) = entry.file_name().into_string() {
                    if file_name.starts_with("sysmonitor-") {
                        let _ = std::fs::remove_file(entry.path());
                    }
                }
            }
        }
    }

    /// 错误统计
    pub fn track_error_metrics(error_type: &str, severity: &str) {
        sentry::configure_scope(|scope| {
            scope.set_tag("error_type", error_type);
            scope.set_tag("severity", severity);
        });

        // 记录错误指标
        sentry::capture_message(
            &format!("Error metric: {} - {}", error_type, severity),
            sentry::Level::Info,
        );
    }
}

/// 错误恢复策略（已迁移到 error::RecoveryStrategy）
/// 此类型保留用于向后兼容，建议直接使用 error::RecoveryStrategy
#[deprecated(note = "请使用 crate::error::RecoveryStrategy")]
pub type RecoveryStrategy = crate::error::RecoveryStrategy;

/// 错误监控器（已迁移到 error::ErrorMonitor）
/// 此类型保留用于向后兼容，建议直接使用 error::ErrorMonitor
#[deprecated(note = "请使用 crate::error::ErrorMonitor")]
pub type ErrorMonitor = crate::error::ErrorMonitor;

/// 错误统计（已迁移到 error::ErrorStats）
/// 此类型保留用于向后兼容，建议直接使用 error::ErrorStats
#[deprecated(note = "请使用 crate::error::ErrorStats")]
pub type ErrorStats = crate::error::ErrorStats;

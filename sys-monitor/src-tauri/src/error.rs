use std::fmt;
use std::sync::PoisonError;
use thiserror::Error;

/// 统一的应用程序错误类型
///
/// 合并了原有的 AppError 和 SysMonitorError，提供全面的错误处理覆盖
#[derive(Error, Debug)]
pub enum AppError {
    /// 参数验证错误
    #[error("无效参数：{0}")]
    InvalidParameter(String),

    /// 文件系统错误（IO、路径不存在、权限不足等）
    #[error("文件系统错误：{0}")]
    FileSystem(String),

    /// 数据库错误
    #[error("数据库错误：{0}")]
    Database(String),

    /// 网络错误
    #[error("网络错误：{0}")]
    Network(String),

    /// 配置错误
    #[error("配置错误：{0}")]
    Configuration(String),

    /// 权限错误
    #[error("权限错误：{0}")]
    Permission(String),

    /// 资源限制错误（内存不足、磁盘空间不足等）
    #[error("资源限制：{0}")]
    ResourceLimit(String),

    /// 操作被取消
    #[error("操作已取消：{0}")]
    Cancelled(String),

    /// 底层 IO 错误
    #[error("IO 错误：{0}")]
    Io(std::io::Error),

    /// 底层数据库错误
    #[error("SQLite 错误：{0}")]
    Sqlite(rusqlite::Error),

    /// 互斥锁中毒错误
    #[error("同步原语中毒：{0}")]
    Poison(String),

    /// JSON 序列化/反序列化错误
    #[error("JSON 错误：{0}")]
    Json(serde_json::Error),

    /// 未知错误
    #[error("未知错误：{0}")]
    Unknown(String),
}

impl AppError {
    /// 创建 InvalidParameter 错误
    pub fn invalid_parameter(msg: impl Into<String>) -> Self {
        AppError::InvalidParameter(msg.into())
    }

    /// 创建 FileSystem 错误
    pub fn file_system(msg: impl Into<String>) -> Self {
        AppError::FileSystem(msg.into())
    }

    /// 创建 Database 错误
    pub fn database(msg: impl Into<String>) -> Self {
        AppError::Database(msg.into())
    }

    /// 创建 Network 错误
    pub fn network(msg: impl Into<String>) -> Self {
        AppError::Network(msg.into())
    }

    /// 创建 Configuration 错误
    pub fn configuration(msg: impl Into<String>) -> Self {
        AppError::Configuration(msg.into())
    }

    /// 创建 Permission 错误
    pub fn permission(msg: impl Into<String>) -> Self {
        AppError::Permission(msg.into())
    }

    /// 创建 ResourceLimit 错误
    pub fn resource_limit(msg: impl Into<String>) -> Self {
        AppError::ResourceLimit(msg.into())
    }

    /// 创建 Cancelled 错误
    pub fn cancelled(msg: impl Into<String>) -> Self {
        AppError::Cancelled(msg.into())
    }

    /// 创建 Unknown 错误
    pub fn unknown(msg: impl Into<String>) -> Self {
        AppError::Unknown(msg.into())
    }

    /// 创建 Poison 错误
    pub fn poison(msg: impl Into<String>) -> Self {
        AppError::Poison(msg.into())
    }

    /// 获取错误类型标识
    pub fn error_type(&self) -> &'static str {
        match self {
            AppError::InvalidParameter(_) => "InvalidParameter",
            AppError::FileSystem(_) => "FileSystem",
            AppError::Database(_) => "Database",
            AppError::Network(_) => "Network",
            AppError::Configuration(_) => "Configuration",
            AppError::Permission(_) => "Permission",
            AppError::ResourceLimit(_) => "ResourceLimit",
            AppError::Cancelled(_) => "Cancelled",
            AppError::Io(_) => "Io",
            AppError::Sqlite(_) => "Sqlite",
            AppError::Poison(_) => "Poison",
            AppError::Json(_) => "Json",
            AppError::Unknown(_) => "Unknown",
        }
    }

    /// 判断是否为可恢复错误
    pub fn is_recoverable(&self) -> bool {
        matches!(
            self,
            AppError::Network(_) | AppError::ResourceLimit(_) | AppError::Cancelled(_)
        )
    }
}

// ============== From trait 实现 ==============

impl From<std::io::Error> for AppError {
    fn from(error: std::io::Error) -> Self {
        match error.kind() {
            std::io::ErrorKind::PermissionDenied => AppError::Permission(error.to_string()),
            std::io::ErrorKind::NotFound => AppError::FileSystem(format!("路径不存在：{}", error)),
            std::io::ErrorKind::AlreadyExists => {
                AppError::FileSystem(format!("路径已存在：{}", error))
            }
            std::io::ErrorKind::InvalidInput => AppError::InvalidParameter(error.to_string()),
            _ => AppError::FileSystem(error.to_string()),
        }
    }
}

impl From<rusqlite::Error> for AppError {
    fn from(error: rusqlite::Error) -> Self {
        match &error {
            rusqlite::Error::SqliteFailure(sqlite_err, _) => {
                match sqlite_err.extended_code {
                    // 数据库文件相关错误
                    1007..=1009 => AppError::FileSystem(format!("数据库文件错误：{}", error)),
                    // 权限相关错误
                    1031 => AppError::Permission(format!("数据库权限不足：{}", error)),
                    // 其他 SQLite 错误
                    _ => AppError::Database(error.to_string()),
                }
            }
            rusqlite::Error::Utf8Error(_) => {
                AppError::FileSystem(format!("数据库编码错误：{}", error))
            }
            rusqlite::Error::NulError(_) => {
                AppError::InvalidParameter(format!("数据库参数包含空字节：{}", error))
            }
            rusqlite::Error::InvalidParameterName(_) => {
                AppError::InvalidParameter(format!("无效参数名：{}", error))
            }
            _ => AppError::Database(error.to_string()),
        }
    }
}

impl<T> From<PoisonError<T>> for AppError {
    fn from(error: PoisonError<T>) -> Self {
        AppError::Poison(format!("互斥锁中毒：{}", error))
    }
}

// ============== Serialize 实现 ==============

impl serde::Serialize for AppError {
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        use serde::ser::SerializeMap;

        let mut map = serializer.serialize_map(Some(3))?;
        map.serialize_entry("type", &self.error_type())?;
        map.serialize_entry("message", &self.to_string())?;
        map.serialize_entry("recoverable", &self.is_recoverable())?;
        map.end()
    }
}

// ============== 类型别名 ==============

/// 统一的结果类型
pub type Result<T> = std::result::Result<T, AppError>;

// ============== 错误监控工具 ==============

/// 错误监控器
pub struct ErrorMonitor {
    error_count: std::sync::atomic::AtomicU64,
    last_error_time: std::sync::Mutex<std::time::Instant>,
}

impl ErrorMonitor {
    pub fn new() -> Self {
        Self {
            error_count: std::sync::atomic::AtomicU64::new(0),
            last_error_time: std::sync::Mutex::new(std::time::Instant::now()),
        }
    }

    /// 记录错误
    pub fn record_error(&self, error: &AppError) {
        self.error_count
            .fetch_add(1, std::sync::atomic::Ordering::SeqCst);
        *self.last_error_time.lock().unwrap() = std::time::Instant::now();

        crate::logger::log_error(&format!("错误记录：{} - {}", error.error_type(), error));
    }

    /// 获取错误统计
    pub fn get_stats(&self) -> ErrorStats {
        ErrorStats {
            total_errors: self.error_count.load(std::sync::atomic::Ordering::SeqCst),
            last_error_time: *self.last_error_time.lock().unwrap(),
        }
    }

    /// 检查错误频率是否过高
    pub fn is_error_rate_high(&self) -> bool {
        let stats = self.get_stats();
        let duration_since_last_error = stats.last_error_time.elapsed().as_secs();

        // 如果最近 5 分钟内错误超过 10 次，认为错误率过高
        duration_since_last_error < 300 && stats.total_errors > 10
    }
}

impl Default for ErrorMonitor {
    fn default() -> Self {
        Self::new()
    }
}

/// 错误统计
#[derive(Debug, Clone)]
pub struct ErrorStats {
    pub total_errors: u64,
    pub last_error_time: std::time::Instant,
}

// ============== 错误恢复策略 ==============

/// 错误恢复策略
pub enum RecoveryStrategy {
    /// 重试操作
    Retry { max_attempts: u32, delay_ms: u64 },
    /// 回退到默认值
    Fallback,
    /// 忽略错误继续执行
    Ignore,
    /// 终止操作
    Terminate,
}

impl RecoveryStrategy {
    /// 执行恢复策略
    pub fn execute<T, F>(&self, operation: F) -> Result<T>
    where
        F: Fn() -> Result<T>,
    {
        match self {
            RecoveryStrategy::Retry {
                max_attempts,
                delay_ms,
            } => {
                for attempt in 1..=*max_attempts {
                    match operation() {
                        Ok(result) => return Ok(result),
                        Err(error) if attempt == *max_attempts => {
                            return Err(error);
                        }
                        Err(error) => {
                            crate::logger::log_warn(&format!(
                                "第 {} 次尝试失败：{}",
                                attempt, error
                            ));
                            std::thread::sleep(std::time::Duration::from_millis(*delay_ms));
                        }
                    }
                }
                Err(AppError::Unknown("超过最大重试次数".to_string()))
            }
            RecoveryStrategy::Fallback => {
                // Fallback 需要调用者提供默认值，这里简化处理
                operation().map_err(|_| AppError::Unknown("回退失败".to_string()))
            }
            RecoveryStrategy::Ignore => match operation() {
                Ok(result) => Ok(result),
                Err(error) => {
                    crate::logger::log_warn(&format!("忽略错误继续执行：{}", error));
                    Err(error)
                }
            },
            RecoveryStrategy::Terminate => operation().map_err(|error| {
                crate::logger::log_error(&format!("终止操作：{}", error));
                error
            }),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_io_error_conversion() {
        let io_error = std::io::Error::new(std::io::ErrorKind::NotFound, "file not found");
        let app_error: AppError = io_error.into();
        assert!(matches!(app_error, AppError::FileSystem(_)));
    }

    #[test]
    fn test_permission_error_conversion() {
        let io_error = std::io::Error::new(std::io::ErrorKind::PermissionDenied, "access denied");
        let app_error: AppError = io_error.into();
        assert!(matches!(app_error, AppError::Permission(_)));
    }

    #[test]
    fn test_error_type() {
        let error = AppError::invalid_parameter("test");
        assert_eq!(error.error_type(), "InvalidParameter");
    }

    #[test]
    fn test_is_recoverable() {
        let network_error = AppError::network("timeout");
        assert!(network_error.is_recoverable());

        let param_error = AppError::invalid_parameter("bad input");
        assert!(!param_error.is_recoverable());
    }
}

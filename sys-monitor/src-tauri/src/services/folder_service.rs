use crate::db::repository::DatabaseRepository;
use crate::models::folder::{FileTypeStat, FolderItem, FolderScan};
use crate::utils::file_types::classify_file;
use crate::logger;
use std::path::Path;
use std::sync::Arc;
use std::time::Instant;
use tokio::sync::{watch, Mutex};
use tokio_util::sync::CancellationToken;

/// 扫描进度信息
#[derive(Debug, Clone)]
pub struct ScanProgress {
    /// 已处理的文件数量
    pub processed_count: u64,
    /// 当前扫描路径
    pub current_path: String,
    /// 总文件数（估算）
    pub estimated_total: u64,
    /// 进度百分比 (0.0 - 1.0)
    pub progress: f64,
}

/// 文件夹扫描服务
pub struct FolderService {
    db_path: String,
}

impl FolderService {
    pub fn new(db_path: String) -> Self {
        Self { db_path }
    }

    /// 带进度反馈和取消支持的文件夹扫描
    /// 
    /// 参数:
    /// - path: 要扫描的文件夹路径
    /// - cancel_token: 用于取消扫描的 token
    /// - progress_tx: 用于发送进度更新的 watch channel sender
    /// 
    /// 返回:
    /// - Ok(FolderScan): 扫描结果
    /// - Err(String): 错误信息
    pub async fn scan_folder_with_progress(
        &self,
        path: String,
        cancel_token: CancellationToken,
        progress_tx: watch::Sender<ScanProgress>,
    ) -> Result<FolderScan, String> {
        logger::log_info(&format!(
            "scan_folder_with_progress 开始 - 路径：{}, 数据库路径：{}",
            path, self.db_path
        ));

        let path_clean = path.trim().to_string();

        if path_clean.is_empty() {
            logger::log_error("扫描路径为空");
            return Err("Path cannot be empty".to_string());
        }

        if !Path::new(&path_clean).exists() {
            logger::log_error(&format!("路径不存在：{}", path_clean));
            return Err(format!("Path does not exist: {}", path_clean));
        }

        if !Path::new(&path_clean).is_dir() {
            logger::log_error(&format!("路径不是目录：{}", path_clean));
            return Err(format!("Path is not a directory: {}", path_clean));
        }

        logger::log_info(&format!("开始创建数据库连接：{}", self.db_path));
        let repo = DatabaseRepository::new(&self.db_path)
            .map_err(|e| {
                logger::log_error(&format!("数据库连接失败：{}", e));
                format!("Database connection failed: {}", e)
            })?;
        logger::log_info("数据库连接创建成功");

        let start_time = Instant::now();

        let mut total_size: u64 = 0;
        let mut file_count: u64 = 0;
        let mut folder_count: u64 = 0;

        let mut file_type_map: std::collections::HashMap<String, u64> = std::collections::HashMap::new();
        let mut folder_items: Vec<FolderItem> = Vec::new();

        logger::log_info(&format!("开始扫描文件夹：{}", path));

        // 发送初始进度
        let _ = progress_tx.send(ScanProgress {
            processed_count: 0,
            current_path: path_clean.clone(),
            estimated_total: 0,
            progress: 0.0,
        });

        let mut processed_count: u64 = 0;
        let entries: Vec<_> = walkdir::WalkDir::new(&path)
            .into_iter()
            .filter_map(|e| e.ok())
            .collect();
        
        let estimated_total = entries.len() as u64;
        logger::log_info(&format!("估算总项目数：{}", estimated_total));

        for entry in entries {
            // 检查取消信号
            if cancel_token.is_cancelled() {
                logger::log_warn("扫描被用户取消");
                return Err("Scan cancelled by user".to_string());
            }

            processed_count += 1;

            // 每 100 个文件发送一次进度更新
            if processed_count % 100 == 0 {
                let progress = if estimated_total > 0 {
                    processed_count as f64 / estimated_total as f64
                } else {
                    0.0
                };

                let _ = progress_tx.send(ScanProgress {
                    processed_count,
                    current_path: entry.path().to_string_lossy().to_string(),
                    estimated_total,
                    progress,
                });

                if processed_count % 1000 == 0 {
                    logger::log_debug(&format!("已处理 {} 个项目...", processed_count));
                }
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
                        scan_id: 0, // 会在批量插入时设置
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

        // 发送最终进度（100%）
        let _ = progress_tx.send(ScanProgress {
            processed_count,
            current_path: path_clean.clone(),
            estimated_total,
            progress: 1.0,
        });

        logger::log_info(&format!(
            "扫描完成，收集到 {} 个文件项，{} 个文件夹，总大小：{} 字节",
            folder_items.len(), folder_count, total_size
        ));

        // 使用事务批量插入所有数据
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
        
        // 使用原子性事务方法一次性完成所有插入
        let mut repo = repo;
        let scan_id = repo.create_scan_with_items(
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
            e.to_string()
        })?;
        
        logger::log_info(&format!("事务批量插入完成，扫描 ID: {}", scan_id));

        let result = FolderScan {
            id: Some(scan_id),
            path,
            scan_timestamp: start_time.elapsed().as_millis() as i64,
            total_size,
            file_count,
            folder_count,
            scan_duration_ms: Some(start_time.elapsed().as_millis() as u64),
        };

        logger::log_info(&format!("scan_folder_with_progress 返回结果：{:?}", result));
        Ok(result)
    }
}

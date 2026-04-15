use notify::{Config, Event, RecommendedWatcher, RecursiveMode, Watcher};
use std::collections::HashMap;
use std::path::PathBuf;
use std::sync::Arc;
use tokio::sync::{mpsc, RwLock};
use tauri::{AppHandle, Emitter};
use crate::db::repository::DatabaseRepository;
use crate::models::folder::WatchedFolder;

/// 文件变更事件类型
#[derive(Debug, Clone, serde::Serialize)]
pub enum FileEventType {
    Created,
    Modified,
    Deleted,
}

impl ToString for FileEventType {
    fn to_string(&self) -> String {
        match self {
            FileEventType::Created => "Created".to_string(),
            FileEventType::Modified => "Modified".to_string(),
            FileEventType::Deleted => "Deleted".to_string(),
        }
    }
}

/// 文件变更事件
#[derive(Debug, Clone, serde::Serialize)]
pub struct FileChangeEvent {
    pub folder_id: i64,
    pub folder_path: String,
    pub event_type: String,
    pub file_path: String,
    pub file_size: Option<u64>,
    pub timestamp: i64,
}

/// 防抖聚合的事件
#[derive(Debug, Clone)]
struct DebouncedEvent {
    folder_id: i64,
    folder_path: String,
    events: Vec<FileChangeEvent>,
    last_update: std::time::Instant,
}

/// 文件监听服务
pub struct FileWatcherService {
    app_handle: AppHandle,
    watchers: Arc<RwLock<HashMap<i64, RecommendedWatcher>>>,
    event_tx: mpsc::Sender<FileChangeEvent>,
    debounce_map: Arc<RwLock<HashMap<i64, DebouncedEvent>>>,
}

impl FileWatcherService {
    pub fn new(app_handle: AppHandle) -> (Self, mpsc::Receiver<FileChangeEvent>) {
        let (event_tx, event_rx) = mpsc::channel::<FileChangeEvent>(1000);

        let service = Self {
            app_handle,
            watchers: Arc::new(RwLock::new(HashMap::new())),
            event_tx,
            debounce_map: Arc::new(RwLock::new(HashMap::new())),
        };

        (service, event_rx)
    }
    
    /// 添加文件夹监听
    pub async fn add_watch(&self, folder: &WatchedFolder) -> Result<(), String> {
        let mut watchers = self.watchers.write().await;
        
        if watchers.contains_key(&folder.id) {
            return Err(format!("Folder {} is already being watched", folder.id));
        }
        
        let event_tx = self.event_tx.clone();
        let folder_id = folder.id;
        let folder_path_for_closure = PathBuf::from(&folder.path);
        let recursive = folder.recursive;
        
        let mut watcher = RecommendedWatcher::new(
            move |result: Result<Event, notify::Error>| {
                if let Ok(event) = result {
                    let tx = event_tx.clone();
                    let fid = folder_id;
                    let fpath = folder_path_for_closure.clone();
                    
                    tokio::spawn(async move {
                        Self::handle_notify_event(event, tx, fid, fpath).await;
                    });
                }
            },
            Config::default()
        ).map_err(|e| format!("Failed to create watcher: {}", e))?;
        
        let mode = if recursive {
            RecursiveMode::Recursive
        } else {
            RecursiveMode::NonRecursive
        };
        
        watcher.watch(&PathBuf::from(&folder.path), mode)
            .map_err(|e| format!("Failed to watch path: {}", e))?;
        
        watchers.insert(folder.id, watcher);
        
        // 发送状态更新到前端
        let _ = self.app_handle.emit("watcher-status-changed", serde_json::json!({
            "folder_id": folder.id,
            "status": "started",
            "path": folder.path
        }));
        
        Ok(())
    }
    
    /// 移除文件夹监听
    pub async fn remove_watch(&self, folder_id: i64) -> Result<(), String> {
        let mut watchers = self.watchers.write().await;
        
        if watchers.remove(&folder_id).is_some() {
            // 清理防抖缓存
            let mut debounce = self.debounce_map.write().await;
            debounce.remove(&folder_id);
            
            let _ = self.app_handle.emit("watcher-status-changed", serde_json::json!({
                "folder_id": folder_id,
                "status": "stopped"
            }));
            
            Ok(())
        } else {
            Err(format!("Folder {} is not being watched", folder_id))
        }
    }
    
    /// 处理notify事件
    async fn handle_notify_event(
        event: Event,
        event_tx: mpsc::Sender<FileChangeEvent>,
        folder_id: i64,
        folder_path: PathBuf,
    ) {
        use notify::EventKind;
        
        for path in event.paths {
            let event_type = match event.kind {
                EventKind::Create(_) => FileEventType::Created,
                EventKind::Modify(_) => FileEventType::Modified,
                EventKind::Remove(_) => FileEventType::Deleted,
                _ => continue,
            };
            
            let file_size = std::fs::metadata(&path).ok().map(|m| m.len());
            
            let change_event = FileChangeEvent {
                folder_id,
                folder_path: folder_path.to_string_lossy().to_string(),
                event_type: event_type.to_string(),
                file_path: path.to_string_lossy().to_string(),
                file_size,
                timestamp: chrono::Utc::now().timestamp(),
            };
            
            let _ = event_tx.send(change_event).await;
        }
    }
    
    /// 启动事件处理循环(带智能聚合和数据库记录)
    pub async fn start_event_processor(
        &self,
        mut event_rx: mpsc::Receiver<FileChangeEvent>,
        debounce_seconds: u64,
    ) {
        let app_handle = self.app_handle.clone();

        tokio::spawn(async move {
            let mut buffer: HashMap<i64, DebouncedEvent> = HashMap::new();
            let debounce_duration = std::time::Duration::from_secs(debounce_seconds);
            
            while let Some(event) = event_rx.recv().await {
                let folder_id = event.folder_id;
                
                // 添加到缓冲区
                let entry = buffer.entry(folder_id).or_insert_with(|| DebouncedEvent {
                    folder_id,
                    folder_path: event.folder_path.clone(),
                    events: Vec::new(),
                    last_update: std::time::Instant::now(),
                });
                
                entry.events.push(event);
                entry.last_update = std::time::Instant::now();
                
                // 检查是否需要刷新缓冲区
                let mut to_flush = Vec::new();
                for (fid, debounced) in buffer.iter() {
                    if debounced.last_update.elapsed() >= debounce_duration {
                        to_flush.push(*fid);
                    }
                }
                
                // 刷新过期的缓冲
                for fid in to_flush {
                    if let Some(debounced) = buffer.remove(&fid) {
                        Self::flush_events(&app_handle, debounced).await;
                    }
                }
            }

            // 清空剩余缓冲
            for (_, debounced) in buffer.drain() {
                Self::flush_events(&app_handle, debounced).await;
            }
        });
    }
    
    /// 刷新事件到前端和数据库，并检查阈值触发警报
    async fn flush_events(
        app_handle: &AppHandle,
        debounced: DebouncedEvent,
    ) {
        if debounced.events.is_empty() {
            return;
        }
        
        let folder_id = debounced.folder_id;
        let folder_path = debounced.folder_path.clone();
        
        // 智能聚合: 统计各类型事件数量
        let mut create_count = 0;
        let mut delete_count = 0;
        let mut modify_count = 0;
        let mut sample_files = Vec::new();
        
        for event in &debounced.events {
            match event.event_type.as_str() {
                "Created" => create_count += 1,
                "Deleted" => delete_count += 1,
                "Modified" => modify_count += 1,
                _ => {}
            }
            
            if sample_files.len() < 3 {
                sample_files.push(event.file_path.clone());
            }
        }
        
        // 构建聚合通知消息
        let mut messages = Vec::new();
        if create_count > 0 {
            messages.push(format!("新建 {} 个文件", create_count));
        }
        if delete_count > 0 {
            messages.push(format!("删除 {} 个文件", delete_count));
        }
        if modify_count > 0 {
            messages.push(format!("修改 {} 个文件", modify_count));
        }
        
        let summary = messages.join(", ");
        let detail = if !sample_files.is_empty() {
            format!("\n示例: {}", sample_files.join("\n"))
        } else {
            String::new()
        };
        
        // 发送到前端
        let _ = app_handle.emit("folder-change-aggregated", serde_json::json!({
            "folder_id": folder_id,
            "folder_path": folder_path,
            "create_count": create_count,
            "delete_count": delete_count,
            "modify_count": modify_count,
            "total_count": debounced.events.len(),
            "summary": summary,
            "detail": detail,
            "sample_files": sample_files,
            "timestamp": chrono::Utc::now().timestamp()
        }));
        
        // 记录到数据库并进行阈值检查
        let db_path = std::env::var("DB_PATH").unwrap_or_else(|_| "data.db".to_string());
        if let Ok(mut repo) = DatabaseRepository::new(&db_path) {
            // 记录文件夹事件
            for event in &debounced.events {
                let _ = repo.insert_folder_event(
                    folder_id,
                    &event.event_type,
                    &event.file_path,
                    event.file_size,
                );
            }
            
            // 清理7天前的旧事件
            let _ = repo.cleanup_old_events(7);
            
            // 阈值检查：查询该folder的配置和最新扫描结果
            Self::check_thresholds_and_alert(app_handle, &mut repo, folder_id, &folder_path).await;
        }
    }

    /// 检查阈值并触发警报
    async fn check_thresholds_and_alert(
        app_handle: &AppHandle,
        repo: &mut DatabaseRepository,
        folder_id: i64,
        folder_path: &str,
    ) {
        // 获取监控文件夹配置
        let watched_folder = match repo.get_watched_folder_by_id(folder_id) {
            Ok(Some(folder)) => folder,
            Ok(None) => {
                // 文件夹不存在于数据库中，跳过阈值检查
                return;
            }
            Err(e) => {
                eprintln!("Failed to get watched folder {}: {}", folder_id, e);
                return;
            }
        };

        // 如果没有设置任何阈值，直接返回
        if watched_folder.size_threshold_bytes.is_none() && watched_folder.file_count_threshold.is_none() {
            return;
        }

        // 获取最新的扫描结果
        let latest_scan = match repo.get_folder_scans(folder_path, 1) {
            Ok(mut scans) => scans.pop(),
            Err(e) => {
                eprintln!("Failed to get folder scans for {}: {}", folder_path, e);
                return;
            }
        };

        // 如果没有扫描记录，无法进行阈值检查
        let scan = match latest_scan {
            Some(scan) => scan,
            None => {
                return;
            }
        };

        let current_time = chrono::Utc::now().timestamp();
        let mut alerts_triggered = Vec::new();

        // 检查大小阈值
        if let Some(size_threshold) = watched_folder.size_threshold_bytes {
            if scan.total_size > size_threshold {
                let size_mb = scan.total_size as f64 / (1024.0 * 1024.0);
                let threshold_mb = size_threshold as f64 / (1024.0 * 1024.0);
                
                alerts_triggered.push((
                    "size_exceeded".to_string(),
                    format!("文件夹 {} 大小超标", folder_path),
                    Some(threshold_mb),
                    Some(size_mb),
                    format!(
                        "当前大小: {:.2} MB, 阈值: {:.2} MB",
                        size_mb, threshold_mb
                    ),
                ));

                // 写入alerts表
                let _ = repo.insert_alert(
                    "folder_size",
                    &format!("folder_{}_size", folder_id),
                    Some(threshold_mb),
                    Some(size_mb),
                );
            }
        }

        // 检查文件数量阈值
        if let Some(file_count_threshold) = watched_folder.file_count_threshold {
            if scan.file_count > file_count_threshold {
                alerts_triggered.push((
                    "file_count_exceeded".to_string(),
                    format!("文件夹 {} 文件数量超标", folder_path),
                    Some(file_count_threshold as f64),
                    Some(scan.file_count as f64),
                    format!(
                        "当前文件数: {}, 阈值: {}",
                        scan.file_count, file_count_threshold
                    ),
                ));

                // 写入alerts表
                let _ = repo.insert_alert(
                    "folder_file_count",
                    &format!("folder_{}_file_count", folder_id),
                    Some(file_count_threshold as f64),
                    Some(scan.file_count as f64),
                );
            }
        }

        // 如果有警报触发，发送事件到前端
        for (alert_type, title, threshold, actual, description) in &alerts_triggered {
            let _ = app_handle.emit("folder-threshold-alert", serde_json::json!({
                "folder_id": folder_id,
                "folder_path": folder_path,
                "alert_type": alert_type,
                "title": title,
                "description": description,
                "threshold_value": threshold,
                "actual_value": actual,
                "timestamp": current_time
            }));
        }
    }
    
    /// 获取所有正在监听的文件夹ID
    pub async fn get_watching_folders(&self) -> Vec<i64> {
        let watchers = self.watchers.read().await;
        watchers.keys().cloned().collect()
    }
    
    /// 停止所有监听
    pub async fn stop_all(&self) {
        let mut watchers = self.watchers.write().await;
        watchers.clear();
    }
}

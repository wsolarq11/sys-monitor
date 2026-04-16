use crate::models::folder::{FileTypeStat, FolderItem, FolderScan};
use crate::models::metrics::{CpuCoreMetric, DiskMetric, NetworkMetric, SystemMetric};
use rusqlite::{Connection, OptionalExtension, Result};

use std::time::{SystemTime, UNIX_EPOCH};

/// SQLite 数据库性能优化配置
const CACHE_SIZE_KB: i64 = -64000; // 64MB 缓存（负值表示 KB）
const MMAP_SIZE: i64 = 268435456; // 256MB 内存映射
const BATCH_SIZE: usize = 1000; // 批量插入大小

pub struct DatabaseRepository {
    conn: Connection,
}

impl DatabaseRepository {
    pub fn new(path: &str) -> Result<Self> {
        let conn = Connection::open(path)?;
        let repo = Self { conn };
        repo.init()?;
        repo.optimize_pragmas()?; // 应用性能优化设置
        Ok(repo)
    }

    pub fn init(&self) -> Result<()> {
        use crate::db::schema::INIT_SQL;
        self.conn.execute_batch(INIT_SQL)?;
        
        // 应用性能优化迁移
        self.apply_performance_migration()?;
        
        Ok(())
    }
    /// 应用性能优化迁移（添加索引等）
    fn apply_performance_migration(&self) -> Result<()> {
        const MIGRATION_SQL: &str = r#"
            CREATE INDEX IF NOT EXISTS idx_folder_scans_path_timestamp 
                ON folder_scans(path, scan_timestamp DESC);
            
            CREATE INDEX IF NOT EXISTS idx_folder_items_path ON folder_items(path);
            CREATE INDEX IF NOT EXISTS idx_folder_items_parent ON folder_items(parent_path);
            CREATE INDEX IF NOT EXISTS idx_folder_items_type ON folder_items(type);
            CREATE INDEX IF NOT EXISTS idx_folder_items_extension ON folder_items(extension);
            
            DROP INDEX IF EXISTS idx_folder_events_folder_time;
            CREATE INDEX IF NOT EXISTS idx_folder_events_folder_time 
                ON folder_events(watched_folder_id, timestamp DESC);
            
            CREATE INDEX IF NOT EXISTS idx_folder_events_file_path ON folder_events(file_path);
            CREATE INDEX IF NOT EXISTS idx_alerts_metric_type ON alerts(metric_type);
            CREATE INDEX IF NOT EXISTS idx_alerts_acknowledged ON alerts(acknowledged);
            CREATE INDEX IF NOT EXISTS idx_watched_folders_created ON watched_folders(created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_system_metrics_created ON system_metrics(created_at);
            CREATE INDEX IF NOT EXISTS idx_network_metrics_created ON network_metrics(created_at);
            
            ANALYZE;
        "#;
        
        self.conn.execute_batch(MIGRATION_SQL)?;
        Ok(())
    }

    /// 优化 SQLite PRAGMA 设置以提升性能
    fn optimize_pragmas(&self) -> Result<()> {
        self.conn.execute_batch(&format!(
            "PRAGMA journal_mode = WAL;
             PRAGMA synchronous = NORMAL;
             PRAGMA cache_size = {};",
            CACHE_SIZE_KB
        ))?;
        
        // 这些 PRAGMA 可能在某些环境下不支持
        let _ = self.conn.execute_batch(&format!(
            "PRAGMA temp_store = MEMORY;
             PRAGMA mmap_size = {};",
            MMAP_SIZE
        ));
        
        Ok(())
    }

    /// 获取底层连接用于高级操作
    pub fn get_connection(&self) -> &Connection {
        &self.conn
    }


    pub fn insert_system_metric(&self, metric: &SystemMetric) -> Result<i64> {
        self.conn.execute(
            "INSERT INTO system_metrics (timestamp, cpu_usage, memory_usage, memory_total, disk_usage, disk_total)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6)",
            rusqlite::params![
                metric.timestamp,
                metric.cpu_usage,
                metric.memory_usage,
                metric.memory_total.unwrap_or(0.0),
                metric.disk_usage.unwrap_or(0.0),
                metric.disk_total.unwrap_or(0.0),
            ],
        )?;
        Ok(self.conn.last_insert_rowid())
    }

    pub fn insert_cpu_core(&self, core: &CpuCoreMetric) -> Result<()> {
        self.conn.execute(
            "INSERT INTO cpu_cores (metric_id, core_name, usage_percent)
             VALUES (?1, ?2, ?3)",
            rusqlite::params![core.metric_id, core.core_name, core.usage_percent,],
        )?;
        Ok(())
    }

    pub fn get_system_metrics(&self, limit: u32) -> Result<Vec<SystemMetric>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, timestamp, cpu_usage, memory_usage, memory_total, disk_usage, disk_total
             FROM system_metrics
             ORDER BY timestamp DESC
             LIMIT ?1",
        )?;

        let metrics = stmt.query_map(rusqlite::params![limit], |row| {
            Ok(SystemMetric {
                id: Some(row.get(0)?),
                timestamp: row.get(1)?,
                cpu_usage: row.get(2)?,
                memory_usage: row.get(3)?,
                memory_total: Some(row.get(4)?),
                disk_usage: Some(row.get(5)?),
                disk_total: Some(row.get(6)?),
            })
        })?;

        let mut result = Vec::new();
        for metric in metrics {
            result.push(metric?);
        }
        Ok(result)
    }

    pub fn get_cpu_cores(&self, metric_id: i64) -> Result<Vec<CpuCoreMetric>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, metric_id, core_name, usage_percent
             FROM cpu_cores
             WHERE metric_id = ?1",
        )?;

        let cores = stmt.query_map(rusqlite::params![metric_id], |row| {
            Ok(CpuCoreMetric {
                id: Some(row.get(0)?),
                metric_id: row.get(1)?,
                core_name: row.get(2)?,
                usage_percent: row.get(3)?,
            })
        })?;

        let mut result = Vec::new();
        for core in cores {
            result.push(core?);
        }
        Ok(result)
    }

    pub fn insert_disk_metric(&self, metric: &DiskMetric) -> Result<i64> {
        self.conn.execute(
            "INSERT INTO disk_metrics (metric_id, mount_point, total_bytes, available_bytes, disk_type)
             VALUES (?1, ?2, ?3, ?4, ?5)",
            rusqlite::params![
                metric.metric_id,
                metric.mount_point,
                metric.total_bytes,
                metric.available_bytes,
                metric.disk_type,
            ],
        )?;
        Ok(self.conn.last_insert_rowid())
    }

    pub fn get_disk_metrics(&self, metric_id: i64) -> Result<Vec<DiskMetric>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, metric_id, mount_point, total_bytes, available_bytes, disk_type
             FROM disk_metrics
             WHERE metric_id = ?1",
        )?;

        let metrics = stmt.query_map(rusqlite::params![metric_id], |row| {
            Ok(DiskMetric {
                id: Some(row.get(0)?),
                metric_id: row.get(1)?,
                mount_point: row.get(2)?,
                total_bytes: row.get(3)?,
                available_bytes: row.get(4)?,
                disk_type: row.get(5)?,
            })
        })?;

        let mut result = Vec::new();
        for metric in metrics {
            result.push(metric?);
        }
        Ok(result)
    }

    pub fn insert_network_metric(&self, metric: &NetworkMetric) -> Result<i64> {
        self.conn.execute(
            "INSERT INTO network_metrics (timestamp, interface_name, bytes_sent, bytes_received)
             VALUES (?1, ?2, ?3, ?4)",
            rusqlite::params![
                metric.timestamp,
                metric.interface_name,
                metric.bytes_sent,
                metric.bytes_received,
            ],
        )?;
        Ok(self.conn.last_insert_rowid())
    }

    pub fn get_network_metrics(&self, limit: u32) -> Result<Vec<NetworkMetric>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, timestamp, interface_name, bytes_sent, bytes_received
             FROM network_metrics
             ORDER BY timestamp DESC
             LIMIT ?1",
        )?;

        let metrics = stmt.query_map(rusqlite::params![limit], |row| {
            Ok(NetworkMetric {
                id: Some(row.get(0)?),
                timestamp: row.get(1)?,
                interface_name: row.get(2)?,
                bytes_sent: row.get(3)?,
                bytes_received: row.get(4)?,
            })
        })?;

        let mut result = Vec::new();
        for metric in metrics {
            result.push(metric?);
        }
        Ok(result)
    }

    // Folder scan methods
    pub fn create_folder_scan(&self, path: &str, scan_timestamp: i64) -> Result<i64> {
        self.conn.execute(
            "INSERT INTO folder_scans (path, scan_timestamp, total_size, file_count, folder_count, scan_duration_ms)
             VALUES (?1, ?2, 0, 0, 0, 0)",
            rusqlite::params![
                path,
                scan_timestamp,
            ],
        )?;
        Ok(self.conn.last_insert_rowid())
    }

    pub fn update_folder_scan(
        &self,
        scan_id: i64,
        total_size: u64,
        file_count: u64,
        folder_count: u64,
        scan_duration_ms: u64,
    ) -> Result<()> {
        self.conn.execute(
            "UPDATE folder_scans SET total_size = ?1, file_count = ?2, folder_count = ?3, scan_duration_ms = ?4 WHERE id = ?5",
            rusqlite::params![
                total_size,
                file_count,
                folder_count,
                scan_duration_ms,
                scan_id,
            ],
        )?;
        Ok(())
    }

    pub fn get_folder_scans(&self, path: &str, limit: i64) -> Result<Vec<FolderScan>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, path, scan_timestamp, total_size, file_count, folder_count, scan_duration_ms
             FROM folder_scans 
             WHERE path = ?1
             ORDER BY scan_timestamp DESC 
             LIMIT ?2"
        )?;

        let scans = stmt.query_map(rusqlite::params![path, limit], |row| {
            Ok(FolderScan {
                id: Some(row.get(0)?),
                path: row.get(1)?,
                scan_timestamp: row.get(2)?,
                total_size: row.get(3)?,
                file_count: row.get(4)?,
                folder_count: row.get(5)?,
                scan_duration_ms: row.get(6)?,
            })
        })?;

        let mut result = Vec::new();
        for scan in scans {
            result.push(scan?);
        }
        Ok(result)
    }

    pub fn insert_folder_item(&self, item: &FolderItem) -> Result<i64> {
        self.conn.execute(
            "INSERT INTO folder_items (scan_id, path, name, size, type, extension, parent_path)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7)",
            rusqlite::params![
                item.scan_id,
                item.path,
                item.name,
                item.size,
                item.item_type,
                item.extension,
                item.parent_path,
            ],
        )?;
        Ok(self.conn.last_insert_rowid())
    }

    pub fn get_folder_items(&self, scan_id: i64) -> Result<Vec<FolderItem>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, scan_id, path, name, size, type, extension, parent_path
             FROM folder_items
             WHERE scan_id = ?1",
        )?;

        let items = stmt.query_map(rusqlite::params![scan_id], |row| {
            Ok(FolderItem {
                id: Some(row.get(0)?),
                scan_id: row.get(1)?,
                path: row.get(2)?,
                name: row.get(3)?,
                size: row.get(4)?,
                item_type: row.get(5)?,
                extension: row.get(6)?,
                parent_path: row.get(7)?,
            })
        })?;

        let mut result = Vec::new();
        for item in items {
            result.push(item?);
        }
        Ok(result)
    }

    pub fn insert_file_type_stat(&self, stat: &FileTypeStat) -> Result<i64> {
        self.conn.execute(
            "INSERT INTO file_type_stats (scan_id, file_type, count, total_size)
             VALUES (?1, ?2, ?3, ?4)",
            rusqlite::params![stat.scan_id, stat.file_type, stat.count, stat.total_size,],
        )?;
        Ok(self.conn.last_insert_rowid())
    }

    pub fn get_file_type_stats(&self, scan_id: i64) -> Result<Vec<FileTypeStat>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, scan_id, file_type, count, total_size
             FROM file_type_stats
             WHERE scan_id = ?1",
        )?;

        let stats = stmt.query_map(rusqlite::params![scan_id], |row| {
            Ok(FileTypeStat {
                id: Some(row.get(0)?),
                scan_id: row.get(1)?,
                file_type: row.get(2)?,
                count: row.get(3)?,
                total_size: row.get(4)?,
            })
        })?;

        let mut result = Vec::new();
        for stat in stats {
            result.push(stat?);
        }
        Ok(result)
    }

    pub fn delete_folder_scan(&self, scan_id: i64) -> Result<bool> {
        self.conn.execute(
            "DELETE FROM folder_items WHERE scan_id = ?1",
            rusqlite::params![scan_id],
        )?;
        self.conn.execute(
            "DELETE FROM file_type_stats WHERE scan_id = ?1",
            rusqlite::params![scan_id],
        )?;
        let affected = self.conn.execute(
            "DELETE FROM folder_scans WHERE id = ?1",
            rusqlite::params![scan_id],
        )?;
        Ok(affected > 0)
    }

    /// 批量插入 folder items，使用事务每 500 条提交一次
    pub fn insert_folder_items_batch(&mut self, items: &[FolderItem]) -> Result<usize> {
        let tx = self.conn.transaction()?;
        let mut inserted = 0;

        // 使用预编译语句提升性能
        let mut stmt = tx.prepare_cached(
            "INSERT INTO folder_items (scan_id, path, name, size, type, extension, parent_path)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7)"
        )?;
        
        for item in items {
            stmt.execute(rusqlite::params![
                item.scan_id,
                item.path,
                item.name,
                item.size,
                item.item_type,
                item.extension,
                item.parent_path,
            ])?;
            inserted += 1;
        }
        
        // 显式 drop statement 以释放 borrow
        drop(stmt);

        tx.commit()?;
        Ok(inserted)
    }

    /// 批量插入 file type stats，使用事务
    pub fn insert_file_type_stats_batch(&mut self, stats: &[FileTypeStat]) -> Result<usize> {
        let tx = self.conn.transaction()?;
        let mut inserted = 0;

        // 使用预编译语句提升性能
        let mut stmt = tx.prepare_cached(
            "INSERT INTO file_type_stats (scan_id, file_type, count, total_size)
             VALUES (?1, ?2, ?3, ?4)"
        )?;
        
        for stat in stats {
            stmt.execute(rusqlite::params![
                stat.scan_id, 
                stat.file_type, 
                stat.count, 
                stat.total_size
            ])?;
            inserted += 1;
        }
        
        // 显式 drop statement 以释放 borrow
        drop(stmt);

        tx.commit()?;
        Ok(inserted)
    }

    /// 原子性事务方法：创建扫描、插入 items、插入统计、更新结果
    pub fn create_scan_with_items(
        &mut self,
        path: &str,
        scan_timestamp: i64,
        items: &[FolderItem],
        stats: &[FileTypeStat],
        total_size: u64,
        file_count: u64,
        folder_count: u64,
        scan_duration_ms: u64,
    ) -> Result<i64> {
        let tx = self.conn.transaction()?;

        // 1. 创建扫描记录
        tx.execute(
            "INSERT INTO folder_scans (path, scan_timestamp, total_size, file_count, folder_count, scan_duration_ms)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6)",
            rusqlite::params![
                path,
                scan_timestamp,
                total_size,
                file_count,
                folder_count,
                scan_duration_ms,
            ],
        )?;
        let scan_id = tx.last_insert_rowid();

        // 2. 批量插入 folder items
        // 使用预编译语句提升性能
        let mut item_stmt = tx.prepare_cached(
            "INSERT INTO folder_items (scan_id, path, name, size, type, extension, parent_path)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7)"
        )?;
        
        for (i, item) in items.iter().enumerate() {
            item_stmt.execute(rusqlite::params![
                scan_id,
                item.path,
                item.name,
                item.size,
                item.item_type,
                item.extension,
                item.parent_path,
            ])?;
            
            // 每 BATCH_SIZE 条记录输出进度
            if (i + 1) % BATCH_SIZE == 0 {
                // log::debug!("已插入 {} 条文件夹项", i + 1);
            }
        }

        // 3. 批量插入 file type stats
        // 使用预编译语句提升性能
        let mut stat_stmt = tx.prepare_cached(
            "INSERT INTO file_type_stats (scan_id, file_type, count, total_size)
             VALUES (?1, ?2, ?3, ?4)"
        )?;
        
        for stat in stats {
            stat_stmt.execute(rusqlite::params![
                scan_id, 
                stat.file_type, 
                stat.count, 
                stat.total_size
            ])?;
        }
        
        // 显式 drop statements 以释放 borrow
        drop(item_stmt);
        drop(stat_stmt);

        // 4. 提交事务
        tx.commit()?;

        Ok(scan_id)
    }

    /// 插入监控文件夹配置
    pub fn insert_watched_folder(&self, path: &str, alias: Option<&str>) -> Result<i64> {
        self.conn.execute(
            "INSERT INTO watched_folders (path, alias, is_active)
             VALUES (?1, ?2, 1)",
            rusqlite::params![path, alias],
        )?;
        Ok(self.conn.last_insert_rowid())
    }

    /// 获取所有监控文件夹
    pub fn get_all_watched_folders(&self) -> Result<Vec<crate::models::folder::WatchedFolder>> {
        use crate::models::folder::WatchedFolder;
        let mut stmt = self.conn.prepare(
            "SELECT id, path, alias, is_active, recursive, debounce_ms,
                    size_threshold_bytes, file_count_threshold,
                    notify_on_create, notify_on_delete, notify_on_modify,
                    last_scan_timestamp, last_event_timestamp, total_events_count
             FROM watched_folders
             ORDER BY created_at DESC",
        )?;

        let folders = stmt.query_map([], |row| {
            Ok(WatchedFolder {
                id: row.get(0)?,
                path: row.get(1)?,
                alias: row.get(2)?,
                is_active: row.get::<_, i64>(3)? != 0,
                recursive: row.get::<_, i64>(4)? != 0,
                debounce_ms: row.get(5)?,
                size_threshold_bytes: row.get(6)?,
                file_count_threshold: row.get(7)?,
                notify_on_create: row.get::<_, i64>(8)? != 0,
                notify_on_delete: row.get::<_, i64>(9)? != 0,
                notify_on_modify: row.get::<_, i64>(10)? != 0,
                last_scan_timestamp: row.get(11)?,
                last_event_timestamp: row.get(12)?,
                total_events_count: row.get(13)?,
            })
        })?;

        let mut result = Vec::new();
        for folder in folders {
            result.push(folder?);
        }
        Ok(result)
    }

    /// 删除监控文件夹
    pub fn delete_watched_folder(&self, folder_id: i64) -> Result<bool> {
        let affected = self.conn.execute(
            "DELETE FROM watched_folders WHERE id = ?1",
            rusqlite::params![folder_id],
        )?;
        Ok(affected > 0)
    }

    /// 更新监控文件夹状态
    pub fn update_watched_folder_status(&self, folder_id: i64, is_active: bool) -> Result<()> {
        self.conn.execute(
            "UPDATE watched_folders SET is_active = ?1, updated_at = strftime('%s', 'now') WHERE id = ?2",
            rusqlite::params![if is_active { 1 } else { 0 }, folder_id],
        )?;
        Ok(())
    }

    /// 插入文件夹事件
    pub fn insert_folder_event(
        &self,
        watched_folder_id: i64,
        event_type: &str,
        file_path: &str,
        file_size: Option<u64>,
    ) -> Result<i64> {
        self.conn.execute(
            "INSERT INTO folder_events (watched_folder_id, event_type, file_path, file_size)
             VALUES (?1, ?2, ?3, ?4)",
            rusqlite::params![watched_folder_id, event_type, file_path, file_size],
        )?;
        Ok(self.conn.last_insert_rowid())
    }

    /// 获取文件夹事件
    pub fn get_folder_events(
        &self,
        watched_folder_id: i64,
        limit: i64,
    ) -> Result<Vec<crate::models::folder::FolderEvent>> {
        use crate::models::folder::FolderEvent;
        let mut stmt = self.conn.prepare(
            "SELECT id, watched_folder_id, event_type, file_path, file_size, timestamp
             FROM folder_events
             WHERE watched_folder_id = ?1
             ORDER BY timestamp DESC
             LIMIT ?2",
        )?;

        let events = stmt.query_map(rusqlite::params![watched_folder_id, limit], |row| {
            Ok(FolderEvent {
                id: row.get(0)?,
                watched_folder_id: row.get(1)?,
                event_type: row.get(2)?,
                file_path: row.get(3)?,
                file_size: row.get(4)?,
                timestamp: row.get(5)?,
            })
        })?;

        let mut result = Vec::new();
        for event in events {
            result.push(event?);
        }
        Ok(result)
    }

    /// 插入告警
    pub fn insert_alert(
        &self,
        metric_type: &str,
        metric_name: &str,
        threshold_value: Option<f64>,
        actual_value: Option<f64>,
    ) -> Result<i64> {
        use std::time::{SystemTime, UNIX_EPOCH};
        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs() as i64;

        self.conn.execute(
            "INSERT INTO alerts (timestamp, metric_type, metric_name, threshold_value, actual_value)
             VALUES (?1, ?2, ?3, ?4, ?5)",
            rusqlite::params![timestamp, metric_type, metric_name, threshold_value, actual_value],
        )?;
        Ok(self.conn.last_insert_rowid())
    }

    /// 插入文件夹扫描记录（带完整参数）
    pub fn insert_folder_scan(
        &self,
        path: &str,
        scan_timestamp: i64,
        file_count: u64,
        folder_count: u64,
        scan_duration_ms: u64,
    ) -> Result<i64> {
        self.conn.execute(
            "INSERT INTO folder_scans (path, scan_timestamp, total_size, file_count, folder_count, scan_duration_ms)
             VALUES (?1, ?2, 0, ?3, ?4, ?5)",
            rusqlite::params![path, scan_timestamp, file_count, folder_count, scan_duration_ms],
        )?;
        Ok(self.conn.last_insert_rowid())
    }

    /// 根据 ID 获取监控文件夹
    pub fn get_watched_folder_by_id(
        &self,
        folder_id: i64,
    ) -> Result<Option<crate::models::folder::WatchedFolder>> {
        use crate::models::folder::WatchedFolder;
        let mut stmt = self.conn.prepare(
            "SELECT id, path, alias, is_active, recursive, debounce_ms,
                    size_threshold_bytes, file_count_threshold,
                    notify_on_create, notify_on_delete, notify_on_modify,
                    last_scan_timestamp, last_event_timestamp, total_events_count
             FROM watched_folders
             WHERE id = ?1",
        )?;

        let folder = stmt.query_map(rusqlite::params![folder_id], |row| {
            Ok(WatchedFolder {
                id: row.get(0)?,
                path: row.get(1)?,
                alias: row.get(2)?,
                is_active: row.get::<_, i64>(3)? != 0,
                recursive: row.get::<_, i64>(4)? != 0,
                debounce_ms: row.get(5)?,
                size_threshold_bytes: row.get(6)?,
                file_count_threshold: row.get(7)?,
                notify_on_create: row.get::<_, i64>(8)? != 0,
                notify_on_delete: row.get::<_, i64>(9)? != 0,
                notify_on_modify: row.get::<_, i64>(10)? != 0,
                last_scan_timestamp: row.get(11)?,
                last_event_timestamp: row.get(12)?,
                total_events_count: row.get(13)?,
            })
        })?;

        let result = folder.into_iter().next().transpose()?;
        Ok(result)
    }

    /// 清理旧的事件记录
    pub fn cleanup_old_events(&self, days_to_keep: i64) -> Result<usize> {
        let affected = self.conn.execute(
            "DELETE FROM folder_events WHERE timestamp < strftime('%s', 'now', ?1 || ' days')",
            rusqlite::params![-days_to_keep],
        )?;
        Ok(affected)
    }

    /// 综合数据清理：清理旧事件、指标并整理数据库
    pub fn cleanup_database(&self, events_days: i64, metrics_days: i64) -> Result<CleanupStats> {
        let mut stats = CleanupStats::default();
        
        // 1. 清理旧的文件夹事件
        let event_cutoff = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs() as i64
            - (events_days * 86400);
        
        stats.events_deleted = self.conn.execute(
            "DELETE FROM folder_events WHERE timestamp < ?1",
            rusqlite::params![event_cutoff],
        )?;
        
        // 2. 清理旧的系统指标
        let metric_cutoff = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs() as i64
            - (metrics_days * 86400);
        
        // 先删除关联的 CPU cores
        let cpu_cores_deleted = self.conn.execute(
            "DELETE FROM cpu_cores WHERE metric_id IN (SELECT id FROM system_metrics WHERE timestamp < ?1)",
            rusqlite::params![metric_cutoff],
        )?;
        stats.cpu_cores_deleted = cpu_cores_deleted;
        
        // 再删除关联的 disk metrics
        let disk_metrics_deleted = self.conn.execute(
            "DELETE FROM disk_metrics WHERE metric_id IN (SELECT id FROM system_metrics WHERE timestamp < ?1)",
            rusqlite::params![metric_cutoff],
        )?;
        stats.disk_metrics_deleted = disk_metrics_deleted;
        
        // 最后删除系统指标
        let system_metrics_deleted = self.conn.execute(
            "DELETE FROM system_metrics WHERE timestamp < ?1",
            rusqlite::params![metric_cutoff],
        )?;
        stats.system_metrics_deleted = system_metrics_deleted;
        
        // 3. 清理旧的网络指标
        stats.network_metrics_deleted = self.conn.execute(
            "DELETE FROM network_metrics WHERE timestamp < ?1",
            rusqlite::params![metric_cutoff],
        )?;
        
        // 4. 清理旧的告警（保留 30 天）
        let alert_cutoff = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs() as i64
            - (30 * 86400);
        
        stats.alerts_deleted = self.conn.execute(
            "DELETE FROM alerts WHERE timestamp < ?1 AND acknowledged = 1",
            rusqlite::params![alert_cutoff],
        )?;
        
        // 5. VACUUM 整理数据库碎片
        self.conn.execute("VACUUM", [])?;
        
        // 6. 重新分析以更新查询计划器统计
        self.conn.execute("ANALYZE", [])?;
        
        Ok(stats)
    }

    /// 获取数据库统计信息
    pub fn get_database_stats(&self) -> Result<DatabaseStats> {
        let mut stmt = self.conn.prepare(
            "SELECT 
                (SELECT COUNT(*) FROM folder_scans),
                (SELECT COUNT(*) FROM folder_items),
                (SELECT COUNT(*) FROM file_type_stats),
                (SELECT COUNT(*) FROM folder_events),
                (SELECT COUNT(*) FROM system_metrics),
                (SELECT COUNT(*) FROM cpu_cores),
                (SELECT COUNT(*) FROM disk_metrics),
                (SELECT COUNT(*) FROM network_metrics),
                (SELECT COUNT(*) FROM alerts),
                (SELECT COUNT(*) FROM watched_folders)
            "
        )?;
        
        let stats = stmt.query_row([], |row| {
            Ok(DatabaseStats {
                folder_scans: row.get(0)?,
                folder_items: row.get(1)?,
                file_type_stats: row.get(2)?,
                folder_events: row.get(3)?,
                system_metrics: row.get(4)?,
                cpu_cores: row.get(5)?,
                disk_metrics: row.get(6)?,
                network_metrics: row.get(7)?,
                alerts: row.get(8)?,
                watched_folders: row.get(9)?,
            })
        })?;
        
        Ok(stats)
    }

    /// 运行 EXPLAIN QUERY PLAN 分析查询
    pub fn explain_query(&self, query: &str) -> Result<Vec<String>> {
        let mut stmt = self.conn.prepare(&format!("EXPLAIN QUERY PLAN {}", query))?;
        
        let rows = stmt.query_map([], |row| {
            Ok(row.get::<_, String>(3)?) // detail 列在第 4 列（索引 3）
        })?;
        
        let mut plans = Vec::new();
        for row in rows {
            plans.push(row?);
        }
        
        Ok(plans)
    }
}

/// 清理统计数据
#[derive(Debug, Default)]
pub struct CleanupStats {
    pub events_deleted: usize,
    pub system_metrics_deleted: usize,
    pub cpu_cores_deleted: usize,
    pub disk_metrics_deleted: usize,
    pub network_metrics_deleted: usize,
    pub alerts_deleted: usize,
}

/// 数据库统计信息
#[derive(Debug)]
pub struct DatabaseStats {
    pub folder_scans: i64,
    pub folder_items: i64,
    pub file_type_stats: i64,
    pub folder_events: i64,
    pub system_metrics: i64,
    pub cpu_cores: i64,
    pub disk_metrics: i64,
    pub network_metrics: i64,
    pub alerts: i64,
    pub watched_folders: i64,
}


#[cfg(test)]
mod tests {
    use super::*;
    use crate::models::folder::{FileTypeStat, FolderItem};
    use crate::models::metrics::{CpuCoreMetric, DiskMetric, NetworkMetric, SystemMetric};
    use tempfile::tempdir;

    fn create_test_repo() -> DatabaseRepository {
        let dir = tempdir().expect("Failed to create temp dir");
        let db_path = dir.path().join("test.db");
        DatabaseRepository::new(db_path.to_str().unwrap()).expect("Failed to create repo")
    }

    #[test]
    fn test_repository_initialization() {
        let _repo = create_test_repo();
        assert!(true);
    }

    #[test]
    fn test_insert_and_get_system_metrics() {
        let repo = create_test_repo();
        let metric = SystemMetric {
            id: None,
            timestamp: 1234567890,
            cpu_usage: 45.5,
            memory_usage: 60.2,
            memory_total: Some(16.0),
            disk_usage: Some(50.0),
            disk_total: Some(500.0),
        };
        let id = repo
            .insert_system_metric(&metric)
            .expect("Failed to insert");
        assert!(id > 0);
        let metrics = repo.get_system_metrics(10).expect("Failed to get metrics");
        assert_eq!(metrics.len(), 1);
        assert_eq!(metrics[0].cpu_usage, 45.5);
    }

    #[test]
    fn test_insert_cpu_core() {
        let repo = create_test_repo();
        let core = CpuCoreMetric {
            id: None,
            metric_id: 1,
            core_name: "Core 0".to_string(),
            usage_percent: 75.0,
        };
        repo.insert_cpu_core(&core)
            .expect("Failed to insert CPU core");
        let cores = repo.get_cpu_cores(1).expect("Failed to get cores");
        assert_eq!(cores.len(), 1);
    }

    #[test]
    fn test_insert_and_get_disk_metrics() {
        let repo = create_test_repo();
        let metric = DiskMetric {
            id: None,
            metric_id: 1,
            mount_point: "/".to_string(),
            total_bytes: 500_000_000_000,
            available_bytes: 250_000_000_000,
            disk_type: Some("SSD".to_string()),
        };
        let id = repo.insert_disk_metric(&metric).expect("Failed to insert");
        assert!(id > 0);
        let metrics = repo.get_disk_metrics(1).expect("Failed to get");
        assert_eq!(metrics.len(), 1);
    }

    #[test]
    fn test_insert_and_get_network_metrics() {
        let repo = create_test_repo();
        let metric = NetworkMetric {
            id: None,
            timestamp: 1234567890,
            interface_name: "eth0".to_string(),
            bytes_sent: 1000000,
            bytes_received: 2000000,
        };
        let id = repo
            .insert_network_metric(&metric)
            .expect("Failed to insert");
        assert!(id > 0);
        let metrics = repo.get_network_metrics(10).expect("Failed to get");
        assert_eq!(metrics.len(), 1);
    }

    #[test]
    fn test_folder_scan_lifecycle() {
        let repo = create_test_repo();
        let scan_id = repo
            .insert_folder_scan("/test/path", 1000000, 100, 10, 500)
            .expect("Failed to insert");
        assert!(scan_id > 0);
        repo.update_folder_scan(scan_id, 2000000, 200, 20, 1000)
            .expect("Failed to update");
        let scans = repo
            .get_folder_scans("/test/path", 10)
            .expect("Failed to get");
        assert_eq!(scans.len(), 1);
        assert_eq!(scans[0].total_size, 2000000);
        let deleted = repo.delete_folder_scan(scan_id).expect("Failed to delete");
        assert!(deleted);
    }

    #[test]
    fn test_insert_folder_item() {
        let repo = create_test_repo();
        let item = FolderItem {
            id: None,
            scan_id: 1,
            path: "/test/file.txt".to_string(),
            name: "file.txt".to_string(),
            size: 1024,
            item_type: "file".to_string(),
            extension: Some(".txt".to_string()),
            parent_path: Some("/test".to_string()),
        };
        let id = repo.insert_folder_item(&item).expect("Failed to insert");
        assert!(id > 0);
        let items = repo.get_folder_items(1).expect("Failed to get");
        assert_eq!(items.len(), 1);
    }

    #[test]
    fn test_insert_file_type_stat() {
        let repo = create_test_repo();
        let stat = FileTypeStat {
            id: None,
            scan_id: 1,
            file_type: ".txt".to_string(),
            count: 50,
            total_size: 51200,
        };
        let id = repo.insert_file_type_stat(&stat).expect("Failed to insert");
        assert!(id > 0);
        let stats = repo.get_file_type_stats(1).expect("Failed to get");
        assert_eq!(stats.len(), 1);
    }

    #[test]
    fn test_batch_insert_folder_items() {
        let mut repo = create_test_repo();
        let items = vec![
            FolderItem {
                id: None,
                scan_id: 1,
                path: "/a.txt".to_string(),
                name: "a.txt".to_string(),
                size: 100,
                item_type: "file".to_string(),
                extension: Some(".txt".to_string()),
                parent_path: Some("/".to_string()),
            },
            FolderItem {
                id: None,
                scan_id: 1,
                path: "/b.txt".to_string(),
                name: "b.txt".to_string(),
                size: 200,
                item_type: "file".to_string(),
                extension: Some(".txt".to_string()),
                parent_path: Some("/".to_string()),
            },
        ];
        let count = repo
            .insert_folder_items_batch(&items)
            .expect("Failed to batch insert");
        assert_eq!(count, 2);
    }

    #[test]
    fn test_batch_insert_file_type_stats() {
        let mut repo = create_test_repo();
        let stats = vec![
            FileTypeStat {
                id: None,
                scan_id: 1,
                file_type: ".txt".to_string(),
                count: 10,
                total_size: 1000,
            },
            FileTypeStat {
                id: None,
                scan_id: 1,
                file_type: ".jpg".to_string(),
                count: 5,
                total_size: 5000,
            },
        ];
        let count = repo
            .insert_file_type_stats_batch(&stats)
            .expect("Failed to batch insert");
        assert_eq!(count, 2);
    }

    #[test]
    fn test_watched_folder_crud() {
        let mut repo = create_test_repo();
        let id = repo
            .insert_watched_folder("/watch/path", Some("Test"))
            .expect("Failed to insert");
        assert!(id > 0);
        let folders = repo.get_all_watched_folders().expect("Failed to get");
        assert_eq!(folders.len(), 1);
        assert!(folders[0].is_active);
        repo.update_watched_folder_status(id, false)
            .expect("Failed to update");
        let folders = repo.get_all_watched_folders().expect("Failed to get");
        assert!(!folders[0].is_active);
        let deleted = repo.delete_watched_folder(id).expect("Failed to delete");
        assert!(deleted);
    }

    #[test]
    fn test_insert_and_get_folder_events() {
        let repo = create_test_repo();
        let event_id = repo
            .insert_folder_event(1, "Created", "/test/new_file.txt", Some(1024))
            .expect("Failed to insert");
        assert!(event_id > 0);
        let events = repo.get_folder_events(1, 10).expect("Failed to get");
        assert_eq!(events.len(), 1);
        assert_eq!(events[0].event_type, "Created");
    }

    #[test]
    fn test_insert_alert() {
        let repo = create_test_repo();
        let alert_id = repo
            .insert_alert(
                "folder_size",
                "/test/path",
                Some(1000000.0),
                Some(2000000.0),
            )
            .expect("Failed to insert");
        assert!(alert_id > 0);
    }
}

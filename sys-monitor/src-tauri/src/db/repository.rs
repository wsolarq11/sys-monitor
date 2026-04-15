use crate::models::folder::{FileTypeStat, FolderItem, FolderScan};
use crate::models::metrics::{CpuCoreMetric, DiskMetric, NetworkMetric, SystemMetric};
use rusqlite::{Connection, Result};

pub struct DatabaseRepository {
    conn: Connection,
}

impl DatabaseRepository {
    pub fn new(path: &str) -> Result<Self> {
        let conn = Connection::open(path)?;
        let repo = Self { conn };
        repo.init()?;
        Ok(repo)
    }

    pub fn init(&self) -> Result<()> {
        use crate::db::schema::INIT_SQL;
        self.conn.execute_batch(INIT_SQL)?;
        Ok(())
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
        let batch_size = 500;

        for chunk in items.chunks(batch_size) {
            for item in chunk {
                tx.execute(
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
                inserted += 1;
            }
        }

        tx.commit()?;
        Ok(inserted)
    }

    /// 批量插入 file type stats，使用事务
    pub fn insert_file_type_stats_batch(&mut self, stats: &[FileTypeStat]) -> Result<usize> {
        let tx = self.conn.transaction()?;
        let mut inserted = 0;

        for stat in stats {
            tx.execute(
                "INSERT INTO file_type_stats (scan_id, file_type, count, total_size)
                 VALUES (?1, ?2, ?3, ?4)",
                rusqlite::params![stat.scan_id, stat.file_type, stat.count, stat.total_size,],
            )?;
            inserted += 1;
        }

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
        for item in items {
            tx.execute(
                "INSERT INTO folder_items (scan_id, path, name, size, type, extension, parent_path)
                 VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7)",
                rusqlite::params![
                    scan_id,
                    item.path,
                    item.name,
                    item.size,
                    item.item_type,
                    item.extension,
                    item.parent_path,
                ],
            )?;
        }

        // 3. 批量插入 file type stats
        for stat in stats {
            tx.execute(
                "INSERT INTO file_type_stats (scan_id, file_type, count, total_size)
                 VALUES (?1, ?2, ?3, ?4)",
                rusqlite::params![scan_id, stat.file_type, stat.count, stat.total_size,],
            )?;
        }

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
            used_bytes: 250_000_000_000,
            usage_percent: 50.0,
            file_system: Some("ext4".to_string()),
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
            bytes_recv: 2000000,
            packets_sent: 1000,
            packets_recv: 2000,
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
        let mut repo = create_test_repo();
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
        let mut repo = create_test_repo();
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

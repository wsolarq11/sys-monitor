use rusqlite::{Connection, Result};
use crate::models::metrics::{SystemMetric, CpuCoreMetric, DiskMetric, NetworkMetric};
use crate::models::folder::{FolderScan, FolderItem, FileTypeStat};

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
            rusqlite::params![
                core.metric_id,
                core.core_name,
                core.usage_percent,
            ],
        )?;
        Ok(())
    }

    pub fn get_system_metrics(&self, limit: u32) -> Result<Vec<SystemMetric>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, timestamp, cpu_usage, memory_usage, memory_total, disk_usage, disk_total
             FROM system_metrics
             ORDER BY timestamp DESC
             LIMIT ?1"
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
             WHERE metric_id = ?1"
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
             WHERE metric_id = ?1"
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
             LIMIT ?1"
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

    pub fn update_folder_scan(&self, scan_id: i64, total_size: u64, file_count: u64, folder_count: u64, scan_duration_ms: u64) -> Result<()> {
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
             WHERE scan_id = ?1"
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
            rusqlite::params![
                stat.scan_id,
                stat.file_type,
                stat.count,
                stat.total_size,
            ],
        )?;
        Ok(self.conn.last_insert_rowid())
    }

    pub fn get_file_type_stats(&self, scan_id: i64) -> Result<Vec<FileTypeStat>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, scan_id, file_type, count, total_size
             FROM file_type_stats
             WHERE scan_id = ?1"
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
                rusqlite::params![
                    stat.scan_id,
                    stat.file_type,
                    stat.count,
                    stat.total_size,
                ],
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
                rusqlite::params![
                    scan_id,
                    stat.file_type,
                    stat.count,
                    stat.total_size,
                ],
            )?;
        }
        
        // 4. 提交事务
        tx.commit()?;
        
        Ok(scan_id)
    }
}

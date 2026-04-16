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
            -- Composite index for folder_scans path + timestamp
            CREATE INDEX IF NOT EXISTS idx_folder_scans_path_timestamp 
                ON folder_scans(path, scan_timestamp DESC);
            
            -- Index for folder_items by path
            CREATE INDEX IF NOT EXISTS idx_folder_items_path ON folder_items(path);
            
            -- Index for folder_items by parent_path
            CREATE INDEX IF NOT EXISTS idx_folder_items_parent ON folder_items(parent_path);
            
            -- Index for folder_items by type
            CREATE INDEX IF NOT EXISTS idx_folder_items_type ON folder_items(type);
            
            -- Index for folder_items by extension
            CREATE INDEX IF NOT EXISTS idx_folder_items_extension ON folder_items(extension);
            
            -- Optimize folder_events composite index
            DROP INDEX IF EXISTS idx_folder_events_folder_time;
            CREATE INDEX IF NOT EXISTS idx_folder_events_folder_time 
                ON folder_events(watched_folder_id, timestamp DESC);
            
            -- Index for folder_events by file_path
            CREATE INDEX IF NOT EXISTS idx_folder_events_file_path ON folder_events(file_path);
            
            -- Index for alerts
            CREATE INDEX IF NOT EXISTS idx_alerts_metric_type ON alerts(metric_type);
            CREATE INDEX IF NOT EXISTS idx_alerts_acknowledged ON alerts(acknowledged);
            
            -- Index for watched_folders
            CREATE INDEX IF NOT EXISTS idx_watched_folders_created ON watched_folders(created_at DESC);
            
            -- Indexes for cleanup queries
            CREATE INDEX IF NOT EXISTS idx_system_metrics_created ON system_metrics(created_at);
            CREATE INDEX IF NOT EXISTS idx_network_metrics_created ON network_metrics(created_at);
            
            -- Update query planner statistics
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
        
        // 这些 PRAGMA 可能在某些环境下不支持，使用 ignore_errors
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

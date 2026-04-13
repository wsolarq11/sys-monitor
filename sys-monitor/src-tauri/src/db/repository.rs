use rusqlite::{Connection, Result};
use crate::models::metrics::{SystemMetric, CpuCoreMetric, DiskMetric, NetworkMetric};

pub struct DatabaseRepository {
    conn: Connection,
}

impl DatabaseRepository {
    pub fn new(path: &str) -> Result<Self> {
        let conn = Connection::open(path)?;
        Ok(Self { conn })
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

    pub fn insert_disk_metric(&self, disk: &DiskMetric) -> Result<()> {
        self.conn.execute(
            "INSERT INTO disk_metrics (metric_id, mount_point, total_bytes, available_bytes, disk_type)
             VALUES (?1, ?2, ?3, ?4, ?5)",
            rusqlite::params![
                disk.metric_id,
                disk.mount_point,
                disk.total_bytes,
                disk.available_bytes,
                disk.disk_type,
            ],
        )?;
        Ok(())
    }

    pub fn insert_network_metric(&self, metric: &NetworkMetric) -> Result<()> {
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
        Ok(())
    }

    pub fn get_recent_metrics(&self, limit: u32) -> Result<Vec<SystemMetric>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, timestamp, cpu_usage, memory_usage, memory_total, disk_usage, disk_total
             FROM system_metrics 
             ORDER BY timestamp DESC 
             LIMIT ?1"
        )?;
        
        let metrics = stmt.query_map([limit], |row| {
            Ok(SystemMetric {
                id: Some(row.get(0)?),
                timestamp: row.get(1)?,
                cpu_usage: row.get(2)?,
                memory_usage: row.get(3)?,
                memory_total: row.get(4)?,
                disk_usage: row.get(5)?,
                disk_total: row.get(6)?,
            })
        })?;
        
        metrics.collect::<Result<Vec<_>, _>>()
    }

    pub fn get_cpu_cores(&self, metric_id: i64) -> Result<Vec<CpuCoreMetric>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, metric_id, core_name, usage_percent
             FROM cpu_cores
             WHERE metric_id = ?1"
        )?;
        
        let cores = stmt.query_map([metric_id], |row| {
            Ok(CpuCoreMetric {
                id: Some(row.get(0)?),
                metric_id: row.get(1)?,
                core_name: row.get(2)?,
                usage_percent: row.get(3)?,
            })
        })?;
        
        cores.collect::<Result<Vec<_>, _>>()
    }

    pub fn get_disk_metrics(&self, metric_id: i64) -> Result<Vec<DiskMetric>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, metric_id, mount_point, total_bytes, available_bytes, disk_type
             FROM disk_metrics
             WHERE metric_id = ?1"
        )?;
        
        let disks = stmt.query_map([metric_id], |row| {
            Ok(DiskMetric {
                id: Some(row.get(0)?),
                metric_id: row.get(1)?,
                mount_point: row.get(2)?,
                total_bytes: row.get(3)?,
                available_bytes: row.get(4)?,
                disk_type: row.get(5)?,
            })
        })?;
        
        disks.collect::<Result<Vec<_>, _>>()
    }
}

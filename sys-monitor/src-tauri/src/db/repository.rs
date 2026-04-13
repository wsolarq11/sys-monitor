use rusqlite::{Connection, Result};
use crate::models::metrics::SystemMetric;

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

    pub fn insert_system_metric(&self, metric: &SystemMetric) -> Result<()> {
        self.conn.execute(
            "INSERT INTO system_metrics (timestamp, cpu_usage, memory_usage, disk_usage)
             VALUES (?1, ?2, ?3, ?4)",
            rusqlite::params![
                metric.timestamp,
                metric.cpu_usage,
                metric.memory_usage,
                metric.disk_usage.unwrap_or(0.0),
            ],
        )?;
        Ok(())
    }

    pub fn get_recent_metrics(&self, limit: u32) -> Result<Vec<SystemMetric>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, timestamp, cpu_usage, memory_usage, disk_usage 
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
                disk_usage: row.get(4)?,
            })
        })?;
        
        metrics.collect::<Result<Vec<_>, _>>()
    }
}

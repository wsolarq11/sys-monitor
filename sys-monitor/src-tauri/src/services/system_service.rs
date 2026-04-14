use sysinfo::{System, Disks, Networks, CpuRefreshKind, RefreshKind};
use crate::models::metrics::SystemMetric;
use crate::error::AppError;
use crate::logger;
use std::sync::{Arc, Mutex};

/// 系统信息服务层
/// 负责处理系统指标采集相关的业务逻辑
/// 使用 Arc<Mutex<System>> 确保线程安全，避免竞态条件
pub struct SystemService {
    system: Arc<Mutex<System>>,
}

impl SystemService {
    /// 创建新的 SystemService 实例
    pub fn new() -> Self {
        let system = System::new_with_specifics(
            RefreshKind::new()
                .with_cpu(CpuRefreshKind::everything())
                .with_memory(sysinfo::MemoryRefreshKind::everything())
        );
        
        Self {
            system: Arc::new(Mutex::new(system)),
        }
    }

    /// 刷新系统信息并获取指标
    /// 
    /// # 返回
    /// 返回 SystemMetric 指标数据
    pub fn refresh_and_get_metrics(&self) -> Result<SystemMetric, AppError> {
        logger::log_info("SystemService::refresh_and_get_metrics - 刷新系统指标");
        
        // 获取锁并刷新系统信息
        let mut sys = self.system.lock().map_err(|e| {
            logger::log_error(&format!("获取系统锁失败：{}", e));
            AppError::poison(format!("Failed to acquire system lock: {}", e))
        })?;
        
        // 确保 CPU 信息已初始化
        if sys.cpus().is_empty() {
            logger::log_debug("CPU 信息为空，初始化 CPU...");
            sys.refresh_cpu();
            std::thread::sleep(std::time::Duration::from_millis(200));
            sys.refresh_cpu();
        }
        
        // 刷新所有系统信息
        sys.refresh_all();
        
        // 获取磁盘信息
        let disks = Disks::new_with_refreshed_list();
        
        // 构建系统指标
        let metric = SystemMetric {
            id: None,
            timestamp: chrono::Utc::now().timestamp(),
            cpu_usage: self.get_global_cpu_usage(&sys) as f64,
            memory_usage: self.get_global_memory_usage(&sys),
            memory_total: Some(self.get_global_memory_total(&sys)),
            disk_usage: Some(self.get_global_disk_usage(&disks)),
            disk_total: Some(self.get_global_disk_total(&disks)),
        };
        
        logger::log_info(&format!(
            "系统指标采集完成 - CPU: {:.1}%, 内存：{:.0}MB / {:.0}MB, 磁盘：{:.1}%",
            metric.cpu_usage,
            metric.memory_usage / 1024.0 / 1024.0,
            metric.memory_total.unwrap_or(1.0) / 1024.0 / 1024.0,
            metric.disk_usage.unwrap_or(0.0)
        ));
        
        Ok(metric)
    }

    /// 获取全局 CPU 使用率
    fn get_global_cpu_usage(&self, sys: &System) -> f32 {
        if sys.cpus().is_empty() {
            return 0.0;
        }
        sys.global_cpu_info().cpu_usage()
    }

    /// 获取全局内存使用量
    fn get_global_memory_usage(&self, sys: &System) -> f64 {
        sys.used_memory() as f64
    }

    /// 获取全局内存总量
    fn get_global_memory_total(&self, sys: &System) -> f64 {
        sys.total_memory() as f64
    }

    /// 获取全局磁盘使用率
    fn get_global_disk_usage(&self, disks: &Disks) -> f64 {
        let mut total = 0;
        let mut available = 0;
        for disk in disks.iter() {
            total += disk.total_space();
            available += disk.available_space();
        }
        if total == 0 {
            return 0.0;
        }
        ((total - available) as f64 / total as f64) * 100.0
    }

    /// 获取全局磁盘总容量
    fn get_global_disk_total(&self, disks: &Disks) -> f64 {
        disks.iter().map(|d| d.total_space() as f64).sum()
    }
}

impl Default for SystemService {
    fn default() -> Self {
        Self::new()
    }
}

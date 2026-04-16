/// 系统监控命令单元测试
/// 
/// 测试范围：
/// - get_system_metrics: 验证系统指标获取
/// - get_cpu_info: 验证CPU信息获取
/// - get_memory_info: 验证内存信息获取
/// - get_disk_info: 验证磁盘信息获取
/// - get_network_info: 验证网络信息获取

#[cfg(test)]
mod tests {
    use super::*;
    use crate::models::metrics::SystemMetric;

    #[test]
    fn test_get_system_metrics_returns_valid_data() {
        let result = get_system_metrics();
        assert!(result.is_ok());
        
        let metric = result.unwrap();
        
        // 验证CPU使用率在合理范围内 (0-100%)
        assert!(metric.cpu_usage >= 0.0);
        assert!(metric.cpu_usage <= 100.0);
        
        // 验证内存使用率为正数
        assert!(metric.memory_usage > 0.0);
        
        // 验证时间戳有效
        assert!(metric.timestamp > 0);
    }

    #[test]
    fn test_get_system_metrics_structure() {
        let metric = get_system_metrics().unwrap();
        
        // 验证所有必需字段都存在
        assert!(metric.cpu_usage.is_finite());
        assert!(metric.memory_usage.is_finite());
        
        // 可选字段应该存在（可能为None或有效值）
        if let Some(total) = metric.memory_total {
            assert!(total > 0.0);
        }
        
        if let Some(disk_usage) = metric.disk_usage {
            assert!(disk_usage >= 0.0);
            assert!(disk_usage <= 100.0);
        }
        
        if let Some(disk_total) = metric.disk_total {
            assert!(disk_total > 0.0);
        }
    }

    #[test]
    fn test_get_cpu_info_returns_valid_json() {
        let result = get_cpu_info();
        assert!(result.is_ok());
        
        let cpu_info = result.unwrap();
        
        // 验证JSON结构
        assert!(cpu_info.get("cpu_count").is_some());
        assert!(cpu_info.get("cpus").is_some());
        
        let cpu_count = cpu_info["cpu_count"].as_u64().unwrap();
        let cpus = cpu_info["cpus"].as_array().unwrap();
        
        // CPU数量应该与数组长度一致
        assert_eq!(cpu_count as usize, cpus.len());
        
        // 至少有一个CPU
        assert!(cpu_count > 0);
    }

    #[test]
    fn test_get_cpu_info_cpu_details() {
        let cpu_info = get_cpu_info().unwrap();
        let cpus = cpu_info["cpus"].as_array().unwrap();
        
        for cpu in cpus {
            // 每个CPU应该有name、usage和frequency字段
            assert!(cpu.get("name").is_some());
            assert!(cpu.get("usage").is_some());
            assert!(cpu.get("frequency").is_some());
            
            let usage = cpu["usage"].as_f64().unwrap();
            assert!(usage >= 0.0);
            assert!(usage <= 100.0);
            
            let frequency = cpu["frequency"].as_u64().unwrap();
            assert!(frequency > 0);
        }
    }

    #[test]
    fn test_get_memory_info_returns_valid_json() {
        let result = get_memory_info();
        assert!(result.is_ok());
        
        let mem_info = result.unwrap();
        
        // 验证必需的字段
        assert!(mem_info.get("total").is_some());
        assert!(mem_info.get("available").is_some());
        assert!(mem_info.get("used").is_some());
        assert!(mem_info.get("usage_percent").is_some());
        
        let total = mem_info["total"].as_u64().unwrap();
        let available = mem_info["available"].as_u64().unwrap();
        let used = mem_info["used"].as_u64().unwrap();
        let usage_percent = mem_info["usage_percent"].as_f64().unwrap();
        
        // 验证数据一致性
        assert!(total > 0);
        assert!(used > 0);
        assert!(available <= total);
        assert_eq!(used + available, total);
        
        // 验证使用率计算正确
        let expected_percent = (used as f64 / total as f64) * 100.0;
        assert!((usage_percent - expected_percent).abs() < 0.1);
    }

    #[test]
    fn test_get_disk_info_returns_valid_json() {
        let result = get_disk_info();
        assert!(result.is_ok());
        
        let disk_info = result.unwrap();
        
        // 验证结构
        assert!(disk_info.get("disk_count").is_some());
        assert!(disk_info.get("disks").is_some());
        
        let disk_count = disk_info["disk_count"].as_u64().unwrap();
        let disks = disk_info["disks"].as_array().unwrap();
        
        assert_eq!(disk_count as usize, disks.len());
    }

    #[test]
    fn test_get_disk_info_disk_details() {
        let disk_info = get_disk_info().unwrap();
        let disks = disk_info["disks"].as_array().unwrap();
        
        for disk in disks {
            // 验证每个磁盘的必需字段
            assert!(disk.get("name").is_some());
            assert!(disk.get("mount_point").is_some());
            assert!(disk.get("total_space").is_some());
            assert!(disk.get("available_space").is_some());
            assert!(disk.get("used_space").is_some());
            assert!(disk.get("usage_percent").is_some());
            assert!(disk.get("file_system").is_some());
            
            let total_space = disk["total_space"].as_u64().unwrap();
            let available_space = disk["available_space"].as_u64().unwrap();
            let used_space = disk["used_space"].as_u64().unwrap();
            let usage_percent = disk["usage_percent"].as_f64().unwrap();
            
            // 验证数据一致性
            assert!(total_space > 0);
            assert!(available_space <= total_space);
            assert_eq!(used_space, total_space - available_space);
            
            // 验证使用率计算
            let expected_percent = ((total_space - available_space) as f64 / total_space as f64) * 100.0;
            assert!((usage_percent - expected_percent).abs() < 0.1);
        }
    }

    #[test]
    fn test_get_network_info_returns_valid_json() {
        let result = get_network_info();
        assert!(result.is_ok());
        
        let net_info = result.unwrap();
        
        // 验证结构
        assert!(net_info.get("interface_count").is_some());
        assert!(net_info.get("interfaces").is_some());
        
        let interface_count = net_info["interface_count"].as_u64().unwrap();
        let interfaces = net_info["interfaces"].as_array().unwrap();
        
        assert_eq!(interface_count as usize, interfaces.len());
    }

    #[test]
    fn test_get_network_info_interface_details() {
        let net_info = get_network_info().unwrap();
        let interfaces = net_info["interfaces"].as_array().unwrap();
        
        for interface in interfaces {
            // 验证每个网络接口的必需字段
            assert!(interface.get("name").is_some());
            assert!(interface.get("bytes_received").is_some());
            assert!(interface.get("bytes_sent").is_some());
            
            let bytes_received = interface["bytes_received"].as_u64().unwrap();
            let bytes_sent = interface["bytes_sent"].as_u64().unwrap();
            
            // 字节数应该是非负数
            assert!(bytes_received >= 0);
            assert!(bytes_sent >= 0);
        }
    }

    #[test]
    fn test_system_metrics_timestamp_is_current() {
        let before = chrono::Utc::now().timestamp();
        let metric = get_system_metrics().unwrap();
        let after = chrono::Utc::now().timestamp();
        
        // 验证时间戳在调用前后之间
        assert!(metric.timestamp >= before);
        assert!(metric.timestamp <= after);
    }

    #[test]
    fn test_multiple_calls_consistency() {
        // 多次调用应该返回相似的结果（不会有巨大差异）
        let metric1 = get_system_metrics().unwrap();
        std::thread::sleep(std::time::Duration::from_millis(100));
        let metric2 = get_system_metrics().unwrap();
        
        // CPU使用率变化应该在合理范围内（不超过50%）
        let cpu_diff = (metric1.cpu_usage - metric2.cpu_usage).abs();
        assert!(cpu_diff < 50.0);
        
        // 内存使用量变化也应该在合理范围内
        let mem_diff = (metric1.memory_usage - metric2.memory_usage).abs();
        let mem_total = metric1.memory_total.unwrap_or(metric1.memory_usage * 2);
        let mem_diff_percent = (mem_diff / mem_total) * 100.0;
        assert!(mem_diff_percent < 10.0);
    }
}

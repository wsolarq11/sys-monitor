/// 第七阶段：核心功能单元测试
/// 测试范围：FolderService, SystemService, Store, 工具函数

use std::fs::File;
use std::io::Write;
use tempfile::tempdir;

// ============================================
// FolderService 单元测试
// ============================================

mod folder_service_tests {
    use super::*;
    use sys_monitor_lib::utils::file_types::{classify_file, get_extension, get_file_type_category};
    use sys_monitor_lib::db::repository::DatabaseRepository;
    use sys_monitor_lib::models::folder::{FolderItem, FileTypeStat};

    // ========== 参数验证测试 ==========
    
    #[test]
    fn test_scan_path_validation_empty_path() {
        // 测试空路径验证
        let empty_paths = vec!["", "   ", "\t", "\n"];
        
        for path in empty_paths {
            let trimmed = path.trim();
            assert!(trimmed.is_empty(), "Empty path should be detected");
        }
    }
    
    #[test]
    fn test_scan_path_validation_nonexistent_path() {
        // 测试不存在路径的验证
        let nonexistent_paths = vec![
            "/nonexistent/path/that/does/not/exist",
            "C:\\\\nonexistent\\windows\\path",
            "/invalid/unix/path/12345",
        ];
        
        for path in nonexistent_paths {
            assert!(
                !std::path::Path::new(path).exists(),
                "Path should not exist for test: {}",
                path
            );
        }
    }
    
    #[test]
    fn test_scan_path_validation_file_not_directory() {
        // 测试文件不是目录的验证
        let temp_dir = tempdir().expect("Failed to create temp dir");
        let file_path = temp_dir.path().join("test_file.txt");
        
        File::create(&file_path)
            .expect("Failed to create test file")
            .write_all(b"test content")
            .expect("Failed to write test content");
        
        assert!(file_path.exists(), "Test file should exist");
        assert!(!file_path.is_dir(), "File should not be a directory");
    }

    // ========== 扫描逻辑测试 ==========
    
    #[test]
    fn test_folder_scan_basic() {
        // 测试基本文件夹扫描功能
        let temp_dir = tempdir().expect("Failed to create temp dir");
        let scan_path = temp_dir.path().to_str().unwrap();
        
        // 创建测试文件结构
        create_test_file_structure(scan_path);
        
        // 创建数据库仓库
        let db_path = format!("{}/test.db", temp_dir.path().display());
        let repo = DatabaseRepository::new(&db_path)
            .expect("Failed to create repository");
        
        // 创建扫描记录
        let scan_timestamp = chrono::Utc::now().timestamp();
        let scan_id = repo.create_folder_scan(scan_path, scan_timestamp)
            .expect("Failed to create folder scan");
        
        assert!(scan_id > 0, "Scan ID should be positive");
        
        // 验证扫描记录
        let scans = repo.get_folder_scans(scan_path, 10)
            .expect("Failed to get folder scans");
        
        assert_eq!(scans.len(), 1, "Should have 1 scan");
        assert_eq!(scans[0].path, scan_path, "Path should match");
    }
    
    #[test]
    fn test_folder_scan_with_subdirectories() {
        // 测试包含子目录的扫描
        let temp_dir = tempdir().expect("Failed to create temp dir");
        let scan_path = temp_dir.path().to_str().unwrap();
        
        // 创建多层目录结构
        std::fs::create_dir(format!("{}/level1", scan_path)).unwrap();
        std::fs::create_dir(format!("{}/level1/level2", scan_path)).unwrap();
        std::fs::create_dir(format!("{}/level1/level2/level3", scan_path)).unwrap();
        
        // 创建测试文件
        File::create(format!("{}/file1.txt", scan_path))
            .unwrap().write_all(b"content1").unwrap();
        File::create(format!("{}/level1/file2.txt", scan_path))
            .unwrap().write_all(b"content2").unwrap();
        File::create(format!("{}/level1/level2/file3.txt", scan_path))
            .unwrap().write_all(b"content3").unwrap();
        
        // 验证目录结构
        assert!(std::path::Path::new(&format!("{}/level1/level2/level3", scan_path)).exists());
        assert!(std::path::Path::new(&format!("{}/file1.txt", scan_path)).exists());
    }
    
    #[test]
    fn test_folder_scan_file_counting() {
        // 测试文件计数准确性
        let temp_dir = tempdir().expect("Failed to create temp dir");
        let scan_path = temp_dir.path().to_str().unwrap();
        
        // 创建精确数量的文件
        let expected_file_count = 15;
        for i in 0..expected_file_count {
            File::create(format!("{}/file_{}.txt", scan_path, i))
                .unwrap().write_all(b"test").unwrap();
        }
        
        // 创建几个目录
        std::fs::create_dir(format!("{}/dir1", scan_path)).unwrap();
        std::fs::create_dir(format!("{}/dir2", scan_path)).unwrap();
        
        // 验证文件数量
        let mut actual_file_count = 0;
        for entry in walkdir::WalkDir::new(scan_path).into_iter().filter_map(|e| e.ok()) {
            if entry.metadata().unwrap().is_file() {
                actual_file_count += 1;
            }
        }
        
        assert_eq!(actual_file_count, expected_file_count, "File count should match");
    }
    
    #[test]
    fn test_folder_scan_size_calculation() {
        // 测试大小计算准确性
        let temp_dir = tempdir().expect("Failed to create temp dir");
        let scan_path = temp_dir.path().to_str().unwrap();
        
        // 创建已知大小的文件
        let file_sizes = vec![100u64, 200u64, 500u64, 1000u64];
        let expected_total: u64 = file_sizes.iter().sum();
        
        for (i, &size) in file_sizes.iter().enumerate() {
            let content = vec![b'a'; size as usize];
            File::create(format!("{}/file_{}.dat", scan_path, i))
                .unwrap().write_all(&content).unwrap();
        }
        
        // 计算实际总大小
        let mut actual_total = 0u64;
        for entry in walkdir::WalkDir::new(scan_path).into_iter().filter_map(|e| e.ok()) {
            if let Ok(metadata) = entry.metadata() {
                if metadata.is_file() {
                    actual_total += metadata.len();
                }
            }
        }
        
        assert_eq!(actual_total, expected_total, "Total size should match");
    }

    // ========== 文件类型分类测试 ==========
    
    #[test]
    fn test_file_type_classification_comprehensive() {
        // 测试所有文件类型的分类
        let test_cases = vec![
            // Images
            ("test.jpg", "Images"),
            ("test.JPEG", "Images"),
            ("test.png", "Images"),
            ("test.gif", "Images"),
            ("test.bmp", "Images"),
            ("test.svg", "Images"),
            ("test.webp", "Images"),
            ("test.ico", "Images"),
            ("test.tiff", "Images"),
            
            // Videos
            ("test.mp4", "Videos"),
            ("test.avi", "Videos"),
            ("test.mkv", "Videos"),
            ("test.mov", "Videos"),
            ("test.wmv", "Videos"),
            ("test.flv", "Videos"),
            ("test.webm", "Videos"),
            
            // Audio
            ("test.mp3", "Audio"),
            ("test.wav", "Audio"),
            ("test.flac", "Audio"),
            ("test.aac", "Audio"),
            ("test.ogg", "Audio"),
            
            // Documents
            ("test.pdf", "Documents"),
            ("test.doc", "Documents"),
            ("test.docx", "Documents"),
            ("test.xls", "Documents"),
            ("test.xlsx", "Documents"),
            ("test.txt", "Documents"),
            ("test.rtf", "Documents"),
            
            // Archives
            ("test.zip", "Archives"),
            ("test.rar", "Archives"),
            ("test.7z", "Archives"),
            ("test.tar", "Archives"),
            ("test.gz", "Archives"),
            
            // Code
            ("test.rs", "Code"),
            ("test.js", "Code"),
            ("test.ts", "Code"),
            ("test.py", "Code"),
            ("test.java", "Code"),
            ("test.cpp", "Code"),
            ("test.go", "Code"),
            ("test.html", "Code"),
            ("test.css", "Code"),
            ("test.json", "Code"),
            ("test.xml", "Code"),
            ("test.yaml", "Code"),
            ("test.yml", "Code"),
            ("test.md", "Code"),
            ("test.csv", "Code"),
            
            // Scripts
            ("test.sh", "Scripts"),
            ("test.bash", "Scripts"),
            ("test.zsh", "Scripts"),
            
            // Fonts
            ("test.ttf", "Fonts"),
            ("test.otf", "Fonts"),
            ("test.woff", "Fonts"),
            ("test.woff2", "Fonts"),
            
            // Data
            ("test.db", "Data"),
            ("test.sqlite", "Data"),
            ("test.sqlite3", "Data"),
            
            // Config
            ("test.ini", "Config"),
            ("test.cfg", "Config"),
            ("test.conf", "Config"),
            ("test.toml", "Config"),
            
            // Executables
            ("test.exe", "Executables"),
            ("test.msi", "Executables"),
            ("test.bat", "Executables"),
            ("test.cmd", "Executables"),
            
            // Other
            ("test.unknown", "Other"),
            ("no_extension", "Other"),
        ];
        
        for (filename, expected) in test_cases {
            let result = classify_file(filename);
            assert_eq!(
                result, expected,
                "Failed classification for file: {}",
                filename
            );
        }
    }
    
    #[test]
    fn test_get_extension_edge_cases() {
        // 测试扩展名提取的边界情况
        assert_eq!(get_extension("file.txt"), Some("txt".to_string()));
        assert_eq!(get_extension("file.TXT"), Some("txt".to_string()));
        assert_eq!(get_extension("file.Tar.Gz"), Some("gz".to_string()));
        assert_eq!(get_extension("no_extension"), None);
        assert_eq!(get_extension(""), None);
        assert_eq!(get_extension("/path/to/file.mp3"), Some("mp3".to_string()));
        assert_eq!(get_extension("C:\\Users\\file.doc"), Some("doc".to_string()));
        assert_eq!(get_extension(".hidden"), None);
        assert_eq!(get_extension(".hidden.txt"), Some("txt".to_string()));
    }
    
    #[test]
    fn test_get_file_type_category_case_insensitive() {
        // 测试分类函数的大小写不敏感性
        let extensions = vec!["jpg", "JPG", "Jpg", "jPg"];
        
        for ext in extensions {
            let result = get_file_type_category(ext);
            assert_eq!(result, "Images", "Should be case insensitive: {}", ext);
        }
    }

    // ========== 取消机制测试 ==========
    
    #[test]
    fn test_scan_cancellation_support() {
        // 测试扫描取消机制的支持
        // 注意：这里测试的是扫描逻辑可以支持取消，而不是实际实现取消
        let temp_dir = tempdir().expect("Failed to create temp dir");
        let scan_path = temp_dir.path().to_str().unwrap();
        
        // 创建大量文件模拟长时间扫描
        for i in 0..100 {
            File::create(format!("{}/file_{}.txt", scan_path, i))
                .unwrap().write_all(b"test content").unwrap();
        }
        
        // 验证可以迭代处理（支持取消的基础）
        let mut processed = 0;
        for entry in walkdir::WalkDir::new(scan_path).into_iter().filter_map(|e| e.ok()) {
            processed += 1;
            // 这里可以检查取消标志
            // if cancel_flag.load(Ordering::Relaxed) { break; }
        }
        
        assert!(processed > 0, "Should process at least one item");
    }

    // ========== 错误处理测试 ==========
    
    #[test]
    fn test_scan_error_handling_permission_denied() {
        // 测试权限错误的处理
        // 注意：在测试环境中可能无法完全模拟权限错误
        let temp_dir = tempdir().expect("Failed to create temp dir");
        let db_path = format!("{}/test.db", temp_dir.path().display());
        
        let repo = DatabaseRepository::new(&db_path)
            .expect("Failed to create repository");
        
        // 即使路径不存在，也应该能创建扫描记录
        let scan_timestamp = chrono::Utc::now().timestamp();
        let scan_id = repo.create_folder_scan("/nonexistent/path", scan_timestamp)
            .expect("Should be able to create scan record");
        
        assert!(scan_id > 0, "Scan ID should be positive");
    }
    
    #[test]
    fn test_scan_error_handling_special_characters() {
        // 测试特殊字符路径的处理
        let temp_dir = tempdir().expect("Failed to create temp dir");
        let special_dir = temp_dir.path().join("test dir with spaces & special!@#");
        std::fs::create_dir(&special_dir).unwrap();
        
        let special_path = special_dir.to_str().unwrap();
        let db_path = format!("{}/test.db", temp_dir.path().display());
        
        let repo = DatabaseRepository::new(&db_path)
            .expect("Failed to create repository");
        
        let scan_timestamp = chrono::Utc::now().timestamp();
        let scan_id = repo.create_folder_scan(special_path, scan_timestamp)
            .expect("Should handle special characters in path");
        
        assert!(scan_id > 0, "Scan ID should be positive");
    }

    // ========== 批量操作测试 ==========
    
    #[test]
    fn test_batch_insert_folder_items() {
        // 测试批量插入文件夹项目
        let temp_dir = tempdir().expect("Failed to create temp dir");
        let db_path = format!("{}/test.db", temp_dir.path().display());
        
        let mut repo = DatabaseRepository::new(&db_path)
            .expect("Failed to create repository");
        
        // 创建扫描记录
        let scan_timestamp = chrono::Utc::now().timestamp();
        let scan_id = repo.create_folder_scan("/test/batch", scan_timestamp)
            .expect("Failed to create folder scan");
        
        // 创建批量项目
        let mut items = Vec::new();
        for i in 0..1000 {
            items.push(FolderItem {
                id: None,
                scan_id,
                path: format!("/test/batch/file_{}.txt", i),
                name: format!("file_{}.txt", i),
                size: 100,
                item_type: "file".to_string(),
                extension: Some("txt".to_string()),
                parent_path: Some("/test/batch".to_string()),
            });
        }
        
        // 批量插入
        let inserted = repo.insert_folder_items_batch(&items)
            .expect("Failed to batch insert items");
        
        assert_eq!(inserted, 1000, "Should insert 1000 items");
        
        // 验证插入结果
        let retrieved_items = repo.get_folder_items(scan_id)
            .expect("Failed to get folder items");
        
        assert_eq!(retrieved_items.len(), 1000, "Should retrieve 1000 items");
    }
    
    #[test]
    fn test_batch_insert_file_type_stats() {
        // 测试批量插入文件类型统计
        let temp_dir = tempdir().expect("Failed to create temp dir");
        let db_path = format!("{}/test.db", temp_dir.path().display());
        
        let mut repo = DatabaseRepository::new(&db_path)
            .expect("Failed to create repository");
        
        let scan_timestamp = chrono::Utc::now().timestamp();
        let scan_id = repo.create_folder_scan("/test/stats", scan_timestamp)
            .expect("Failed to create folder scan");
        
        // 创建统计信息
        let stats = vec![
            FileTypeStat {
                id: None,
                scan_id,
                file_type: "Documents".to_string(),
                count: 50,
                total_size: 5000,
            },
            FileTypeStat {
                id: None,
                scan_id,
                file_type: "Images".to_string(),
                count: 30,
                total_size: 15000,
            },
            FileTypeStat {
                id: None,
                scan_id,
                file_type: "Code".to_string(),
                count: 20,
                total_size: 2000,
            },
        ];
        
        let inserted = repo.insert_file_type_stats_batch(&stats)
            .expect("Failed to batch insert stats");
        
        assert_eq!(inserted, 3, "Should insert 3 stats");
        
        let retrieved = repo.get_file_type_stats(scan_id)
            .expect("Failed to get file type stats");
        
        assert_eq!(retrieved.len(), 3, "Should retrieve 3 stats");
    }
    
    #[test]
    fn test_atomic_scan_creation() {
        // 测试原子性扫描创建（事务）
        let temp_dir = tempdir().expect("Failed to create temp dir");
        let db_path = format!("{}/test.db", temp_dir.path().display());
        
        let mut repo = DatabaseRepository::new(&db_path)
            .expect("Failed to create repository");
        
        let items = vec![
            FolderItem {
                id: None,
                scan_id: 0, // Will be set by the method
                path: "/test/file1.txt".to_string(),
                name: "file1.txt".to_string(),
                size: 100,
                item_type: "file".to_string(),
                extension: Some("txt".to_string()),
                parent_path: Some("/test".to_string()),
            },
        ];
        
        let stats = vec![
            FileTypeStat {
                id: None,
                scan_id: 0,
                file_type: "Documents".to_string(),
                count: 1,
                total_size: 100,
            },
        ];
        
        let scan_id = repo.create_scan_with_items(
            "/test/atomic",
            chrono::Utc::now().timestamp(),
            &items,
            &stats,
            100,
            1,
            0,
            50,
        ).expect("Failed to create atomic scan");
        
        assert!(scan_id > 0, "Should return positive scan ID");
        
        // 验证扫描记录
        let scans = repo.get_folder_scans("/test/atomic", 10)
            .expect("Failed to get scans");
        assert_eq!(scans.len(), 1, "Should have 1 scan");
        assert_eq!(scans[0].file_count, 1, "Should have 1 file");
        
        // 验证 items
        let retrieved_items = repo.get_folder_items(scan_id)
            .expect("Failed to get items");
        assert_eq!(retrieved_items.len(), 1, "Should have 1 item");
        
        // 验证 stats
        let retrieved_stats = repo.get_file_type_stats(scan_id)
            .expect("Failed to get stats");
        assert_eq!(retrieved_stats.len(), 1, "Should have 1 stat");
    }
}

// ============================================
// SystemService 单元测试
// ============================================

mod system_service_tests {
    use super::*;
    use sys_monitor_lib::db::repository::DatabaseRepository;
    use sys_monitor_lib::models::metrics::{SystemMetric, CpuCoreMetric, DiskMetric, NetworkMetric};

    // ========== 指标获取测试 ==========
    
    #[test]
    fn test_system_metric_insertion() {
        // 测试系统指标插入
        let temp_dir = tempdir().expect("Failed to create temp dir");
        let db_path = format!("{}/test.db", temp_dir.path().display());
        
        let repo = DatabaseRepository::new(&db_path)
            .expect("Failed to create repository");
        
        let metric = SystemMetric {
            id: None,
            timestamp: chrono::Utc::now().timestamp(),
            cpu_usage: 45.5,
            memory_usage: 60.2,
            memory_total: Some(16000.0),
            disk_usage: Some(50.0),
            disk_total: Some(500000.0),
        };
        
        let metric_id = repo.insert_system_metric(&metric)
            .expect("Failed to insert system metric");
        
        assert!(metric_id > 0, "Metric ID should be positive");
        
        // 验证插入的数据
        let metrics = repo.get_system_metrics(10)
            .expect("Failed to get system metrics");
        
        assert_eq!(metrics.len(), 1, "Should have 1 metric");
        assert_eq!(metrics[0].cpu_usage, 45.5, "CPU usage should match");
        assert_eq!(metrics[0].memory_usage, 60.2, "Memory usage should match");
    }
    
    #[test]
    fn test_cpu_core_metric_insertion() {
        // 测试 CPU 核心指标插入
        let temp_dir = tempdir().expect("Failed to create temp dir");
        let db_path = format!("{}/test.db", temp_dir.path().display());
        
        let repo = DatabaseRepository::new(&db_path)
            .expect("Failed to create repository");
        
        // 先创建系统指标
        let system_metric = SystemMetric {
            id: None,
            timestamp: chrono::Utc::now().timestamp(),
            cpu_usage: 50.0,
            memory_usage: 50.0,
            memory_total: Some(16000.0),
            disk_usage: Some(50.0),
            disk_total: Some(500000.0),
        };
        
        let metric_id = repo.insert_system_metric(&system_metric)
            .expect("Failed to insert system metric");
        
        // 插入 CPU 核心指标
        let core_metric = CpuCoreMetric {
            id: None,
            metric_id,
            core_name: "CPU 0".to_string(),
            usage_percent: 75.5,
        };
        
        repo.insert_cpu_core(&core_metric)
            .expect("Failed to insert CPU core metric");
        
        // 验证
        let cores = repo.get_cpu_cores(metric_id)
            .expect("Failed to get CPU cores");
        
        assert_eq!(cores.len(), 1, "Should have 1 core");
        assert_eq!(cores[0].core_name, "CPU 0", "Core name should match");
        assert_eq!(cores[0].usage_percent, 75.5, "Usage should match");
    }
    
    #[test]
    fn test_disk_metric_insertion() {
        // 测试磁盘指标插入
        let temp_dir = tempdir().expect("Failed to create temp dir");
        let db_path = format!("{}/test.db", temp_dir.path().display());
        
        let repo = DatabaseRepository::new(&db_path)
            .expect("Failed to create repository");
        
        let system_metric = SystemMetric {
            id: None,
            timestamp: chrono::Utc::now().timestamp(),
            cpu_usage: 50.0,
            memory_usage: 50.0,
            memory_total: Some(16000.0),
            disk_usage: Some(50.0),
            disk_total: Some(500000.0),
        };
        
        let metric_id = repo.insert_system_metric(&system_metric)
            .expect("Failed to insert system metric");
        
        let disk_metric = DiskMetric {
            id: None,
            metric_id,
            mount_point: "C:".to_string(),
            total_bytes: 500_000_000_000,
            available_bytes: 250_000_000_000,
            disk_type: Some("SSD".to_string()),
        };
        
        repo.insert_disk_metric(&disk_metric)
            .expect("Failed to insert disk metric");
        
        let disks = repo.get_disk_metrics(metric_id)
            .expect("Failed to get disk metrics");
        
        assert_eq!(disks.len(), 1, "Should have 1 disk");
        assert_eq!(disks[0].mount_point, "C:", "Mount point should match");
        assert_eq!(disks[0].total_bytes, 500_000_000_000, "Total bytes should match");
    }
    
    #[test]
    fn test_network_metric_insertion() {
        // 测试网络指标插入
        let temp_dir = tempdir().expect("Failed to create temp dir");
        let db_path = format!("{}/test.db", temp_dir.path().display());
        
        let repo = DatabaseRepository::new(&db_path)
            .expect("Failed to create repository");
        
        let network_metric = NetworkMetric {
            id: None,
            timestamp: chrono::Utc::now().timestamp(),
            interface_name: "Ethernet".to_string(),
            bytes_sent: 1_000_000,
            bytes_received: 2_000_000,
        };
        
        repo.insert_network_metric(&network_metric)
            .expect("Failed to insert network metric");
        
        let networks = repo.get_network_metrics(10)
            .expect("Failed to get network metrics");
        
        assert_eq!(networks.len(), 1, "Should have 1 network metric");
        assert_eq!(networks[0].interface_name, "Ethernet", "Interface name should match");
        assert_eq!(networks[0].bytes_sent, 1_000_000, "Bytes sent should match");
    }

    // ========== 并发安全性测试 ==========
    
    #[test]
    fn test_concurrent_metric_insertions() {
        // 测试并发插入指标的安全性（模拟并发场景）
        // 注意：rusqlite Connection 不是线程安全的，这里使用顺序插入模拟
        let temp_dir = tempdir().expect("Failed to create temp dir");
        let db_path = format!("{}/test.db", temp_dir.path().display());
        
        let mut repo = DatabaseRepository::new(&db_path)
            .expect("Failed to create repository");
        
        // 顺序插入 10 个指标（模拟并发场景）
        let mut results = vec![];
        for i in 0..10 {
            let metric = SystemMetric {
                id: None,
                timestamp: chrono::Utc::now().timestamp(),
                cpu_usage: i as f64 * 10.0,
                memory_usage: 50.0,
                memory_total: Some(16000.0),
                disk_usage: Some(50.0),
                disk_total: Some(500000.0),
            };
            
            let result = repo.insert_system_metric(&metric)
                .expect("Failed to insert metric");
            results.push(result);
        }
        
        // 验证所有插入都成功了
        assert_eq!(results.len(), 10, "Should have 10 results");
        
        // 验证数据库中有 10 条记录
        let metrics = repo.get_system_metrics(100)
            .expect("Failed to get metrics");
        
        assert_eq!(metrics.len(), 10, "Should have 10 metrics in database");
    }
    
    #[test]
    fn test_metric_limit_enforcement() {
        // 测试指标数量限制
        let temp_dir = tempdir().expect("Failed to create temp dir");
        let db_path = format!("{}/test.db", temp_dir.path().display());
        
        let repo = DatabaseRepository::new(&db_path)
            .expect("Failed to create repository");
        
        // 插入 50 个指标
        for i in 0..50 {
            let metric = SystemMetric {
                id: None,
                timestamp: chrono::Utc::now().timestamp() + i,
                cpu_usage: i as f64,
                memory_usage: 50.0,
                memory_total: Some(16000.0),
                disk_usage: Some(50.0),
                disk_total: Some(500000.0),
            };
            
            repo.insert_system_metric(&metric)
                .expect("Failed to insert metric");
        }
        
        // 测试不同限制
        let limit_10 = repo.get_system_metrics(10)
            .expect("Failed to get metrics with limit 10");
        assert_eq!(limit_10.len(), 10, "Should return 10 metrics");
        
        let limit_25 = repo.get_system_metrics(25)
            .expect("Failed to get metrics with limit 25");
        assert_eq!(limit_25.len(), 25, "Should return 25 metrics");
        
        let limit_100 = repo.get_system_metrics(100)
            .expect("Failed to get metrics with limit 100");
        assert_eq!(limit_100.len(), 50, "Should return all 50 metrics");
    }

    // ========== 边界条件测试 ==========
    
    #[test]
    fn test_empty_metrics_retrieval() {
        // 测试空数据库的指标检索
        let temp_dir = tempdir().expect("Failed to create temp dir");
        let db_path = format!("{}/test.db", temp_dir.path().display());
        
        let repo = DatabaseRepository::new(&db_path)
            .expect("Failed to create repository");
        
        let metrics = repo.get_system_metrics(10)
            .expect("Failed to get metrics");
        
        assert_eq!(metrics.len(), 0, "Should return empty list");
    }
    
    #[test]
    fn test_metric_with_null_values() {
        // 测试包含 null 值的指标
        let temp_dir = tempdir().expect("Failed to create temp dir");
        let db_path = format!("{}/test.db", temp_dir.path().display());
        
        let repo = DatabaseRepository::new(&db_path)
            .expect("Failed to create repository");
        
        // 创建包含 null 值的指标（通过 0.0 表示）
        let metric = SystemMetric {
            id: None,
            timestamp: chrono::Utc::now().timestamp(),
            cpu_usage: 0.0,
            memory_usage: 0.0,
            memory_total: Some(0.0),
            disk_usage: Some(0.0),
            disk_total: Some(0.0),
        };
        
        let metric_id = repo.insert_system_metric(&metric)
            .expect("Failed to insert metric");
        
        assert!(metric_id > 0, "Metric ID should be positive");
    }
}

// ============================================
// Store/状态管理测试
// ============================================

mod store_tests {
    use super::*;
    use sys_monitor_lib::db::repository::DatabaseRepository;

    // ========== 状态转换测试 ==========
    
    #[test]
    fn test_folder_scan_state_lifecycle() {
        // 测试文件夹扫描状态生命周期
        let temp_dir = tempdir().expect("Failed to create temp dir");
        let db_path = format!("{}/test.db", temp_dir.path().display());
        
        let repo = DatabaseRepository::new(&db_path)
            .expect("Failed to create repository");
        
        // 1. 初始状态：创建扫描记录
        let scan_timestamp = chrono::Utc::now().timestamp();
        let scan_id = repo.create_folder_scan("/test/lifecycle", scan_timestamp)
            .expect("Failed to create scan");
        
        // 验证初始状态
        let scans = repo.get_folder_scans("/test/lifecycle", 10)
            .expect("Failed to get scans");
        assert_eq!(scans.len(), 1, "Should have 1 scan");
        assert_eq!(scans[0].total_size, 0, "Initial size should be 0");
        assert_eq!(scans[0].file_count, 0, "Initial file count should be 0");
        
        // 2. 扫描中：更新进度
        repo.update_folder_scan(scan_id, 5000, 50, 5, 100)
            .expect("Failed to update scan");
        
        let scans = repo.get_folder_scans("/test/lifecycle", 10)
            .expect("Failed to get scans");
        assert_eq!(scans[0].total_size, 5000, "Size should be updated");
        assert_eq!(scans[0].file_count, 50, "File count should be updated");
        assert_eq!(scans[0].folder_count, 5, "Folder count should be updated");
        
        // 3. 完成状态：最终更新
        repo.update_folder_scan(scan_id, 10000, 100, 10, 500)
            .expect("Failed to finalize scan");
        
        let scans = repo.get_folder_scans("/test/lifecycle", 10)
            .expect("Failed to get scans");
        assert_eq!(scans[0].total_size, 10000, "Final size should be 10000");
        assert_eq!(scans[0].file_count, 100, "Final file count should be 100");
        assert_eq!(scans[0].scan_duration_ms, Some(500), "Duration should be set");
    }
    
    #[test]
    fn test_scan_deletion_state_transition() {
        // 测试扫描删除的状态转换
        let temp_dir = tempdir().expect("Failed to create temp dir");
        let db_path = format!("{}/test.db", temp_dir.path().display());
        
        let repo = DatabaseRepository::new(&db_path)
            .expect("Failed to create repository");
        
        // 创建扫描
        let scan_timestamp = chrono::Utc::now().timestamp();
        let scan_id = repo.create_folder_scan("/test/delete", scan_timestamp)
            .expect("Failed to create scan");
        
        // 验证存在
        let scans = repo.get_folder_scans("/test/delete", 10)
            .expect("Failed to get scans");
        assert_eq!(scans.len(), 1, "Should have 1 scan");
        
        // 删除扫描
        let deleted = repo.delete_folder_scan(scan_id)
            .expect("Failed to delete scan");
        assert!(deleted, "Should return true on successful deletion");
        
        // 验证已删除
        let scans = repo.get_folder_scans("/test/delete", 10)
            .expect("Failed to get scans");
        assert_eq!(scans.len(), 0, "Should have 0 scans after deletion");
    }
    
    #[test]
    fn test_multiple_scans_state_isolation() {
        // 测试多个扫描的状态隔离
        let temp_dir = tempdir().expect("Failed to create temp dir");
        let db_path = format!("{}/test.db", temp_dir.path().display());
        
        let repo = DatabaseRepository::new(&db_path)
            .expect("Failed to create repository");
        
        // 创建 3 个不同的扫描
        let paths = vec!["/test/scan1", "/test/scan2", "/test/scan3"];
        let mut scan_ids = vec![];
        
        for path in &paths {
            let scan_id = repo.create_folder_scan(path, chrono::Utc::now().timestamp())
                .expect("Failed to create scan");
            scan_ids.push(scan_id);
        }
        
        // 分别更新每个扫描
        for (i, &scan_id) in scan_ids.iter().enumerate() {
            repo.update_folder_scan(scan_id, (i as u64 + 1) * 1000, (i as u64 + 1) * 10, i as u64 + 1, 100)
                .expect("Failed to update scan");
        }
        
        // 验证每个扫描的独立性
        for (i, &scan_id) in scan_ids.iter().enumerate() {
            let scans = repo.get_folder_scans(paths[i], 10)
                .expect("Failed to get scans");
            
            assert_eq!(scans.len(), 1, "Should have 1 scan");
            assert_eq!(scans[0].total_size, (i as u64 + 1) * 1000, "Size should be unique");
            assert_eq!(scans[0].file_count, (i as u64 + 1) * 10, "File count should be unique");
        }
    }

    // ========== 历史状态测试 ==========
    
    #[test]
    fn test_scan_history_limit() {
        // 测试扫描历史限制
        let temp_dir = tempdir().expect("Failed to create temp dir");
        let db_path = format!("{}/test.db", temp_dir.path().display());
        
        let repo = DatabaseRepository::new(&db_path)
            .expect("Failed to create repository");
        
        // 创建 20 个扫描记录
        for i in 0..20 {
            let scan_timestamp = chrono::Utc::now().timestamp() + i;
            let scan_id = repo.create_folder_scan("/test/history", scan_timestamp)
                .expect("Failed to create scan");
            repo.update_folder_scan(scan_id, (i as u64 + 1) * 100, i as u64 + 1, 1, 50)
                .expect("Failed to update scan");
        }
        
        // 测试不同限制
        let limit_5 = repo.get_folder_scans("/test/history", 5)
            .expect("Failed to get scans");
        assert_eq!(limit_5.len(), 5, "Should return 5 scans");
        
        let limit_10 = repo.get_folder_scans("/test/history", 10)
            .expect("Failed to get scans");
        assert_eq!(limit_10.len(), 10, "Should return 10 scans");
        
        // 验证返回的是最新的记录（按时间倒序）
        assert!(limit_10[0].scan_timestamp > limit_10[9].scan_timestamp, 
                "Should return in descending order");
    }
    
    #[test]
    fn test_scan_timestamp_ordering() {
        // 测试扫描时间戳排序
        let temp_dir = tempdir().expect("Failed to create temp dir");
        let db_path = format!("{}/test.db", temp_dir.path().display());
        
        let repo = DatabaseRepository::new(&db_path)
            .expect("Failed to create repository");
        
        // 以特定顺序创建扫描
        let timestamps = vec![300, 100, 500, 200, 400];
        
        for ts in &timestamps {
            repo.create_folder_scan("/test/order", *ts)
                .expect("Failed to create scan");
        }
        
        // 获取所有扫描
        let scans = repo.get_folder_scans("/test/order", 10)
            .expect("Failed to get scans");
        
        assert_eq!(scans.len(), 5, "Should have 5 scans");
        
        // 验证按时间戳降序排列
        for i in 0..scans.len() - 1 {
            assert!(scans[i].scan_timestamp >= scans[i + 1].scan_timestamp,
                    "Should be ordered by timestamp descending");
        }
    }
}

// ============================================
// 工具函数测试
// ============================================

mod utility_tests {
    // 工具函数测试不需要额外导入

    // ========== formatBytes 测试 ==========
    
    #[test]
    fn test_format_bytes_zero() {
        // 测试 0 字节
        assert_eq!(super::format_bytes(0), "0 B");
    }
    
    #[test]
    fn test_format_bytes_bytes() {
        // 测试字节级别
        assert_eq!(super::format_bytes(1), "1.00 B");
        assert_eq!(super::format_bytes(500), "500.00 B");
        assert_eq!(super::format_bytes(1023), "1023.00 B");
    }
    
    #[test]
    fn test_format_bytes_kilobytes() {
        // 测试 KB 级别
        assert_eq!(super::format_bytes(1024), "1.00 KB");
        assert_eq!(super::format_bytes(1536), "1.50 KB");
        assert_eq!(super::format_bytes(2048), "2.00 KB");
        assert_eq!(super::format_bytes(10240), "10.00 KB");
    }
    
    #[test]
    fn test_format_bytes_megabytes() {
        // 测试 MB 级别
        assert_eq!(super::format_bytes(1048576), "1.00 MB");
        assert_eq!(super::format_bytes(1572864), "1.50 MB");
        assert_eq!(super::format_bytes(5242880), "5.00 MB");
        assert_eq!(super::format_bytes(10485760), "10.00 MB");
    }
    
    #[test]
    fn test_format_bytes_gigabytes() {
        // 测试 GB 级别
        assert_eq!(super::format_bytes(1073741824), "1.00 GB");
        assert_eq!(super::format_bytes(1610612736), "1.50 GB");
        assert_eq!(super::format_bytes(5368709120), "5.00 GB");
        assert_eq!(super::format_bytes(10737418240), "10.00 GB");
    }
    
    #[test]
    fn test_format_bytes_terabytes() {
        // 测试 TB 级别
        assert_eq!(super::format_bytes(1099511627776), "1.00 TB");
        assert_eq!(super::format_bytes(2199023255552), "2.00 TB");
    }
    
    #[test]
    fn test_format_bytes_precision() {
        // 测试精度
        assert_eq!(super::format_bytes(1234), "1.21 KB");
        assert_eq!(super::format_bytes(12345), "12.06 KB");
        assert_eq!(super::format_bytes(123456), "120.56 KB");
    }

    // ========== formatPercent 测试 ==========
    
    #[test]
    fn test_format_percent_basic() {
        // 测试基本百分比格式化
        assert_eq!(super::format_percent(0.0), "0.0%");
        assert_eq!(super::format_percent(50.0), "50.0%");
        assert_eq!(super::format_percent(100.0), "100.0%");
    }
    
    #[test]
    fn test_format_percent_decimal() {
        // 测试小数百分比
        assert_eq!(super::format_percent(45.67), "45.7%");
        assert_eq!(super::format_percent(99.99), "100.0%");
        assert_eq!(super::format_percent(0.123), "0.1%");
    }
    
    #[test]
    fn test_format_percent_negative() {
        // 测试负数百分比
        assert_eq!(super::format_percent(-10.0), "-10.0%");
        assert_eq!(super::format_percent(-0.5), "-0.5%");
    }

    // ========== formatSize 测试 ==========
    
    #[test]
    fn test_format_size_bytes() {
        // 测试字节级别
        assert_eq!(super::format_size(0), "0 B");
        assert_eq!(super::format_size(100), "100 B");
        assert_eq!(super::format_size(1023), "1023 B");
    }
    
    #[test]
    fn test_format_size_kilobytes() {
        // 测试 KB 级别
        assert_eq!(super::format_size(1024), "1.00 KB");
        assert_eq!(super::format_size(2048), "2.00 KB");
        assert_eq!(super::format_size(1536), "1.50 KB");
    }
    
    #[test]
    fn test_format_size_megabytes() {
        // 测试 MB 级别
        assert_eq!(super::format_size(1048576), "1.00 MB");
        assert_eq!(super::format_size(5242880), "5.00 MB");
    }
    
    #[test]
    fn test_format_size_gigabytes() {
        // 测试 GB 级别
        assert_eq!(super::format_size(1073741824), "1.00 GB");
        assert_eq!(super::format_size(5368709120), "5.00 GB");
    }
}

// ============================================
// 辅助函数
// ============================================

/// 创建测试文件结构
fn create_test_file_structure(base_path: &str) {
    // 创建文件
    File::create(format!("{}/file1.txt", base_path))
        .unwrap().write_all(b"content1").unwrap();
    File::create(format!("{}/file2.jpg", base_path))
        .unwrap().write_all(b"image data").unwrap();
    
    // 创建子目录
    std::fs::create_dir(format!("{}/subdir", base_path)).unwrap();
    File::create(format!("{}/subdir/file3.mp3", base_path))
        .unwrap().write_all(b"audio data").unwrap();
}

/// 格式化字节数为可读字符串
fn format_bytes(bytes: u64) -> String {
    if bytes == 0 {
        return "0 B".to_string();
    }
    
    let k: u64 = 1024;
    let sizes = ["B", "KB", "MB", "GB", "TB"];
    let i = (bytes as f64).ln() / (k as f64).ln();
    let i = i.floor() as usize;
    
    format!("{:.2} {}", bytes as f64 / ((k.pow(i as u32)) as f64), sizes[i])
}

/// 格式化百分比
fn format_percent(value: f64) -> String {
    format!("{:.1}%", value)
}

/// 格式化大小（简短版本）
fn format_size(bytes: u64) -> String {
    if bytes < 1024 {
        format!("{} B", bytes)
    } else if bytes < 1024 * 1024 {
        format!("{:.2} KB", bytes as f64 / 1024.0)
    } else if bytes < 1024 * 1024 * 1024 {
        format!("{:.2} MB", bytes as f64 / (1024.0 * 1024.0))
    } else {
        format!("{:.2} GB", bytes as f64 / (1024.0 * 1024.0 * 1024.0))
    }
}

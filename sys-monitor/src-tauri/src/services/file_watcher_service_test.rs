/// 文件监听服务单元测试
/// 
/// 测试范围：
/// - FileEventType枚举转换
/// - FileChangeEvent结构
/// - DebouncedEvent聚合逻辑
/// - 事件处理流程

#[cfg(test)]
mod tests {
    use super::*;
    use std::time::Instant;

    #[test]
    fn test_file_event_type_to_string() {
        assert_eq!(FileEventType::Created.to_string(), "Created");
        assert_eq!(FileEventType::Modified.to_string(), "Modified");
        assert_eq!(FileEventType::Deleted.to_string(), "Deleted");
    }

    #[test]
    fn test_file_change_event_creation() {
        let event = FileChangeEvent {
            folder_id: 1,
            folder_path: "/test/path".to_string(),
            event_type: "Created".to_string(),
            file_path: "/test/path/file.txt".to_string(),
            file_size: Some(1024),
            timestamp: 1234567890,
        };

        assert_eq!(event.folder_id, 1);
        assert_eq!(event.folder_path, "/test/path");
        assert_eq!(event.event_type, "Created");
        assert_eq!(event.file_path, "/test/path/file.txt");
        assert_eq!(event.file_size, Some(1024));
        assert!(event.timestamp > 0);
    }

    #[test]
    fn test_file_change_event_with_none_size() {
        let event = FileChangeEvent {
            folder_id: 2,
            folder_path: "/another/path".to_string(),
            event_type: "Deleted".to_string(),
            file_path: "/another/path/deleted.txt".to_string(),
            file_size: None,
            timestamp: 1234567891,
        };

        assert_eq!(event.file_size, None);
    }

    #[test]
    fn test_debounced_event_structure() {
        let events = vec![
            FileChangeEvent {
                folder_id: 1,
                folder_path: "/test".to_string(),
                event_type: "Created".to_string(),
                file_path: "/test/a.txt".to_string(),
                file_size: Some(100),
                timestamp: 1000,
            },
            FileChangeEvent {
                folder_id: 1,
                folder_path: "/test".to_string(),
                event_type: "Modified".to_string(),
                file_path: "/test/b.txt".to_string(),
                file_size: Some(200),
                timestamp: 1001,
            },
        ];

        let debounced = DebouncedEvent {
            folder_id: 1,
            folder_path: "/test".to_string(),
            events: events.clone(),
            last_update: Instant::now(),
        };

        assert_eq!(debounced.folder_id, 1);
        assert_eq!(debounced.events.len(), 2);
        assert_eq!(debounced.events[0].file_path, "/test/a.txt");
        assert_eq!(debounced.events[1].file_path, "/test/b.txt");
    }

    #[test]
    fn test_debounced_event_elapsed() {
        let events = vec![FileChangeEvent {
            folder_id: 1,
            folder_path: "/test".to_string(),
            event_type: "Created".to_string(),
            file_path: "/test/file.txt".to_string(),
            file_size: Some(100),
            timestamp: 1000,
        }];

        let debounced = DebouncedEvent {
            folder_id: 1,
            folder_path: "/test".to_string(),
            events,
            last_update: Instant::now(),
        };

        // 刚创建，经过时间应该很短
        assert!(debounced.last_update.elapsed().as_millis() < 100);
    }

    #[test]
    fn test_event_aggregation_counts() {
        // 模拟多个事件的聚合
        let mut create_count = 0;
        let mut delete_count = 0;
        let mut modify_count = 0;

        let events = vec![
            FileChangeEvent {
                folder_id: 1,
                folder_path: "/test".to_string(),
                event_type: "Created".to_string(),
                file_path: "/test/a.txt".to_string(),
                file_size: Some(100),
                timestamp: 1000,
            },
            FileChangeEvent {
                folder_id: 1,
                folder_path: "/test".to_string(),
                event_type: "Created".to_string(),
                file_path: "/test/b.txt".to_string(),
                file_size: Some(200),
                timestamp: 1001,
            },
            FileChangeEvent {
                folder_id: 1,
                folder_path: "/test".to_string(),
                event_type: "Deleted".to_string(),
                file_path: "/test/c.txt".to_string(),
                file_size: None,
                timestamp: 1002,
            },
            FileChangeEvent {
                folder_id: 1,
                folder_path: "/test".to_string(),
                event_type: "Modified".to_string(),
                file_path: "/test/d.txt".to_string(),
                file_size: Some(300),
                timestamp: 1003,
            },
        ];

        for event in &events {
            match event.event_type.as_str() {
                "Created" => create_count += 1,
                "Deleted" => delete_count += 1,
                "Modified" => modify_count += 1,
                _ => {}
            }
        }

        assert_eq!(create_count, 2);
        assert_eq!(delete_count, 1);
        assert_eq!(modify_count, 1);
        assert_eq!(events.len(), 4);
    }

    #[test]
    fn test_sample_files_extraction() {
        let events = vec![
            FileChangeEvent {
                folder_id: 1,
                folder_path: "/test".to_string(),
                event_type: "Created".to_string(),
                file_path: format!("/test/file_{}.txt", i),
                file_size: Some(100),
                timestamp: 1000 + i,
            }
        ];

        let mut sample_files = Vec::new();
        for event in &events {
            if sample_files.len() < 3 {
                sample_files.push(event.file_path.clone());
            }
        }

        // 应该只取前3个
        assert!(sample_files.len() <= 3);
        assert_eq!(sample_files.len(), 1); // 实际只有1个事件
    }

    #[test]
    fn test_sample_files_limit() {
        let events: Vec<FileChangeEvent> = (0..10)
            .map(|i| FileChangeEvent {
                folder_id: 1,
                folder_path: "/test".to_string(),
                event_type: "Created".to_string(),
                file_path: format!("/test/file_{}.txt", i),
                file_size: Some(100),
                timestamp: 1000 + i,
            })
            .collect();

        let mut sample_files = Vec::new();
        for event in &events {
            if sample_files.len() < 3 {
                sample_files.push(event.file_path.clone());
            }
        }

        // 应该限制在3个
        assert_eq!(sample_files.len(), 3);
        assert_eq!(sample_files[0], "/test/file_0.txt");
        assert_eq!(sample_files[1], "/test/file_1.txt");
        assert_eq!(sample_files[2], "/test/file_2.txt");
    }

    #[test]
    fn test_empty_events_handling() {
        let debounced = DebouncedEvent {
            folder_id: 1,
            folder_path: "/test".to_string(),
            events: vec![],
            last_update: Instant::now(),
        };

        assert_eq!(debounced.events.len(), 0);
        assert!(debounced.events.is_empty());
    }

    #[test]
    fn test_event_serialization() {
        let event = FileChangeEvent {
            folder_id: 1,
            folder_path: "/test/path".to_string(),
            event_type: "Created".to_string(),
            file_path: "/test/path/file.txt".to_string(),
            file_size: Some(1024),
            timestamp: 1234567890,
        };

        // 验证可以序列化为JSON
        let json = serde_json::to_string(&event).unwrap();
        assert!(json.contains("folder_id"));
        assert!(json.contains("Created"));
        assert!(json.contains("file.txt"));
    }

    #[test]
    fn test_event_deserialization() {
        let json = r#"{
            "folder_id": 1,
            "folder_path": "/test/path",
            "event_type": "Modified",
            "file_path": "/test/path/file.txt",
            "file_size": 2048,
            "timestamp": 1234567890
        }"#;

        let event: FileChangeEvent = serde_json::from_str(json).unwrap();
        assert_eq!(event.folder_id, 1);
        assert_eq!(event.event_type, "Modified");
        assert_eq!(event.file_size, Some(2048));
    }
}

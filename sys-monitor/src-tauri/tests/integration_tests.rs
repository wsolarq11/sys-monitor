use std::fs::File;
use std::io::Write;
use tempfile::tempdir;

#[test]
fn test_file_type_classification() {
    use sys_monitor_lib::utils::file_types::classify_file;

    let test_cases = vec![
        ("test.txt", "Documents"),
        ("test.jpg", "Images"),
        ("test.mp4", "Videos"),
        ("test.mp3", "Audio"),
        ("test.exe", "Executables"),
        ("test.zip", "Archives"),
        ("test.doc", "Documents"),
        ("test.pdf", "Documents"),
        ("test.js", "Code"),
        ("test.rs", "Code"),
        ("test.html", "Code"),
        ("test.db", "Data"),
        ("test", "Other"),
    ];

    for (filename, expected) in test_cases {
        let result = classify_file(filename);
        assert_eq!(result, expected, "Failed for file: {}", filename);
    }
}

#[test]
fn test_database_operations() {
    let temp_dir = tempdir().expect("Failed to create temp dir");
    let db_path = format!("{}/test.db", temp_dir.path().display());

    let repo = sys_monitor_lib::db::repository::DatabaseRepository::new(&db_path)
        .expect("Failed to create repository");

    // Test folder scan creation
    let scan_timestamp = chrono::Utc::now().timestamp();
    let scan_id = repo
        .create_folder_scan("/test/path", scan_timestamp)
        .expect("Failed to create folder scan");

    assert!(scan_id > 0, "Scan ID should be positive");

    // Test scan update
    repo.update_folder_scan(scan_id, 1024, 10, 2, 100)
        .expect("Failed to update folder scan");

    // Test scan retrieval
    let scans = repo
        .get_folder_scans("/test/path", 10)
        .expect("Failed to get folder scans");

    assert_eq!(scans.len(), 1, "Should have 1 scan");
    assert_eq!(scans[0].total_size, 1024, "Total size should be 1024");
    assert_eq!(scans[0].file_count, 10, "File count should be 10");
    assert_eq!(scans[0].folder_count, 2, "Folder count should be 2");
}

#[test]
fn test_scan_small_folder() {
    let temp_dir = tempdir().expect("Failed to create temp dir");
    let scan_path = temp_dir.path().to_str().unwrap();

    // Create test files
    File::create(format!("{}/file1.txt", scan_path))
        .unwrap()
        .write_all(b"test content 1")
        .unwrap();
    File::create(format!("{}/file2.txt", scan_path))
        .unwrap()
        .write_all(b"test content 2")
        .unwrap();
    std::fs::create_dir(format!("{}/subfolder", scan_path)).unwrap();
    File::create(format!("{}/subfolder/file3.txt", scan_path))
        .unwrap()
        .write_all(b"test content 3")
        .unwrap();

    // Test folder scan using repository directly
    let db_path = format!("{}/test.db", temp_dir.path().display());
    let repo = sys_monitor_lib::db::repository::DatabaseRepository::new(&db_path)
        .expect("Failed to create repository");

    let scan_timestamp = chrono::Utc::now().timestamp();
    let scan_id = repo
        .create_folder_scan(scan_path, scan_timestamp)
        .expect("Failed to create folder scan");

    // Simulate scanning files
    let files = vec![
        (format!("{}/file1.txt", scan_path), "file1.txt", 14u64),
        (format!("{}/file2.txt", scan_path), "file2.txt", 14u64),
        (
            format!("{}/subfolder/file3.txt", scan_path),
            "file3.txt",
            14u64,
        ),
    ];

    let mut total_size = 0u64;
    for (path, name, size) in files {
        let item = sys_monitor_lib::models::folder::FolderItem {
            id: None,
            scan_id,
            path,
            name: name.to_string(),
            size,
            item_type: "file".to_string(),
            extension: Some("txt".to_string()),
            parent_path: Some(scan_path.to_string()),
        };
        repo.insert_folder_item(&item)
            .expect("Failed to insert folder item");
        total_size += size;
    }

    // Update scan results
    repo.update_folder_scan(scan_id, total_size, 3, 1, 0)
        .expect("Failed to update folder scan");

    // Verify results
    let scans = repo
        .get_folder_scans(scan_path, 10)
        .expect("Failed to get scans");
    assert_eq!(scans.len(), 1, "Should have 1 scan");
    assert_eq!(scans[0].file_count, 3, "Expected 3 files");
    assert_eq!(scans[0].folder_count, 1, "Expected 1 folder");
}

#[test]
fn test_scan_empty_folder() {
    let temp_dir = tempdir().expect("Failed to create temp dir");
    let scan_path = temp_dir.path().to_str().unwrap();

    let db_path = format!("{}/test.db", temp_dir.path().display());
    let repo = sys_monitor_lib::db::repository::DatabaseRepository::new(&db_path)
        .expect("Failed to create repository");

    let scan_timestamp = chrono::Utc::now().timestamp();
    let scan_id = repo
        .create_folder_scan(scan_path, scan_timestamp)
        .expect("Failed to create folder scan");

    // Update with empty results
    repo.update_folder_scan(scan_id, 0, 0, 0, 0)
        .expect("Failed to update folder scan");

    let scans = repo
        .get_folder_scans(scan_path, 10)
        .expect("Failed to get scans");
    assert_eq!(scans.len(), 1, "Should have 1 scan");
    assert_eq!(scans[0].total_size, 0, "Expected 0 size");
    assert_eq!(scans[0].file_count, 0, "Expected 0 files");
}

#[test]
fn test_scan_history() {
    let temp_dir = tempdir().expect("Failed to create temp dir");
    let scan_path = temp_dir.path().to_str().unwrap();
    let db_path = format!("{}/test.db", temp_dir.path().display());
    let repo = sys_monitor_lib::db::repository::DatabaseRepository::new(&db_path)
        .expect("Failed to create repository");

    // Create multiple scans
    for i in 0..5 {
        let scan_timestamp = chrono::Utc::now().timestamp() + i;
        let scan_id = repo
            .create_folder_scan(scan_path, scan_timestamp)
            .expect("Failed to create folder scan");
        repo.update_folder_scan(scan_id, (100 * (i + 1)) as u64, (i + 1) as u64, 1, 0)
            .expect("Failed to update folder scan");
    }

    // Test limit
    let scans = repo
        .get_folder_scans(scan_path, 3)
        .expect("Failed to get scans");
    assert_eq!(scans.len(), 3, "Should have 3 scans with limit");
}

#[test]
fn test_delete_folder_scan() {
    let temp_dir = tempdir().expect("Failed to create temp dir");
    let scan_path = temp_dir.path().to_str().unwrap();
    let db_path = format!("{}/test.db", temp_dir.path().display());
    let repo = sys_monitor_lib::db::repository::DatabaseRepository::new(&db_path)
        .expect("Failed to create repository");

    let scan_timestamp = chrono::Utc::now().timestamp();
    let scan_id = repo
        .create_folder_scan(scan_path, scan_timestamp)
        .expect("Failed to create folder scan");

    // Verify scan exists
    let scans = repo
        .get_folder_scans(scan_path, 10)
        .expect("Failed to get scans");
    assert_eq!(scans.len(), 1, "Should have 1 scan");

    // Delete scan
    repo.delete_folder_scan(scan_id)
        .expect("Failed to delete folder scan");

    // Verify scan is deleted
    let scans = repo
        .get_folder_scans(scan_path, 10)
        .expect("Failed to get scans");
    assert_eq!(scans.len(), 0, "Should have 0 scans after deletion");
}

#[test]
fn test_file_type_distribution() {
    let temp_dir = tempdir().expect("Failed to create temp dir");
    let scan_path = temp_dir.path().to_str().unwrap();
    let db_path = format!("{}/test.db", temp_dir.path().display());
    let repo = sys_monitor_lib::db::repository::DatabaseRepository::new(&db_path)
        .expect("Failed to create repository");

    let scan_timestamp = chrono::Utc::now().timestamp();
    let scan_id = repo
        .create_folder_scan(scan_path, scan_timestamp)
        .expect("Failed to create folder scan");

    // Insert file type stats directly
    let stats_to_insert = vec![("Documents", 3u64, 300u64), ("Images", 1u64, 100u64)];

    for (file_type, count, total_size) in stats_to_insert {
        let stat = sys_monitor_lib::models::folder::FileTypeStat {
            id: None,
            scan_id,
            file_type: file_type.to_string(),
            count,
            total_size,
        };
        repo.insert_file_type_stat(&stat)
            .expect("Failed to insert file type stat");
    }

    // Get file type stats
    let stats = repo
        .get_file_type_stats(scan_id)
        .expect("Failed to get file type stats");

    // Verify we have stats
    assert!(!stats.is_empty(), "Should have file type stats");

    // Verify total count matches
    let total_count: u64 = stats.iter().map(|s| s.count).sum();
    assert_eq!(total_count, 4, "Should have 4 total files in stats");
}

#[test]
fn test_scan_error_handling() {
    let temp_dir = tempdir().expect("Failed to create temp dir");
    let db_path = format!("{}/test.db", temp_dir.path().display());
    let repo = sys_monitor_lib::db::repository::DatabaseRepository::new(&db_path)
        .expect("Failed to create repository");

    // Test with invalid path (should still create scan record)
    let scan_timestamp = chrono::Utc::now().timestamp();
    let scan_id = repo
        .create_folder_scan("/nonexistent/path", scan_timestamp)
        .expect("Should be able to create scan for non-existent path");

    assert!(scan_id > 0, "Scan ID should be positive");
}

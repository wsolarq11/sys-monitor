use std::path::Path;

/// Get file extension from path
pub fn get_extension(path: &str) -> Option<String> {
    Path::new(path)
        .extension()
        .and_then(|ext| ext.to_str())
        .map(|s| s.to_lowercase())
}

/// Get file type category from extension
pub fn get_file_type_category(extension: &str) -> String {
    let ext = extension.to_lowercase();
    
    match ext.as_str() {
        // Images
        "jpg" | "jpeg" | "png" | "gif" | "bmp" | "svg" | "webp" | "ico" | "tiff" | "tif" => "Images",
        // Videos
        "mp4" | "avi" | "mkv" | "mov" | "wmv" | "flv" | "webm" | "m4v" | "mpg" | "mpeg" => "Videos",
        // Audio
        "mp3" | "wav" | "flac" | "aac" | "ogg" | "oga" | "m4a" | "wma" | "aiff" | "alac" => "Audio",
        // Documents
        "pdf" | "doc" | "docx" | "xls" | "xlsx" | "ppt" | "pptx" | "txt" | "rtf" | "odt" | "ods" | "odp" => "Documents",
        // Archives
        "zip" | "rar" | "7z" | "tar" | "gz" | "bz2" | "xz" | "lz" | "lzma" | "zst" => "Archives",
        // Code
        "rs" | "js" | "ts" | "py" | "java" | "cpp" | "h" | "c" | "cs" | "go" | "rb" | "php" | "swift" | "kt" | "scala" | "sql" | "html" | "css" | "json" | "xml" | "yaml" | "yml" | "md" | "csv" => "Code",
        // Shell scripts (special case - handled separately)
        "sh" | "bash" | "zsh" => "Scripts",
        // Fonts
        "ttf" | "otf" | "woff" | "woff2" | "eot" => "Fonts",
        // Data
        "db" | "sqlite" | "sqlite3" | "mdb" | "accdb" => "Data",
        // Config
        "ini" | "cfg" | "conf" | "config" | "toml" => "Config",
        // Executables
        "exe" | "msi" | "bat" | "cmd" | "app" | "deb" | "rpm" => "Executables",
        // Other
        _ => "Other",
    }.to_string()
}

/// Classify a file by its extension
pub fn classify_file(path: &str) -> String {
    get_extension(path)
        .map(|ext| get_file_type_category(&ext))
        .unwrap_or_else(|| "Other".to_string())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_get_extension() {
        assert_eq!(get_extension("file.txt"), Some("txt".to_string()));
        assert_eq!(get_extension("file.JPG"), Some("jpg".to_string()));
        assert_eq!(get_extension("no_extension"), None);
        assert_eq!(get_extension("/path/to/file.mp3"), Some("mp3".to_string()));
    }

    #[test]
    fn test_get_file_type_category() {
        assert_eq!(get_file_type_category("jpg"), "Images");
        assert_eq!(get_file_type_category("mp4"), "Videos");
        assert_eq!(get_file_type_category("mp3"), "Audio");
        assert_eq!(get_file_type_category("pdf"), "Documents");
        assert_eq!(get_file_type_category("zip"), "Archives");
        assert_eq!(get_file_type_category("rs"), "Code");
        assert_eq!(get_file_type_category("sh"), "Scripts");
        assert_eq!(get_file_type_category("unknown"), "Other");
    }

    #[test]
    fn test_classify_file() {
        assert_eq!(classify_file("image.jpg"), "Images");
        assert_eq!(classify_file("video.mp4"), "Videos");
        assert_eq!(classify_file("song.mp3"), "Audio");
        assert_eq!(classify_file("document.pdf"), "Documents");
        assert_eq!(classify_file("archive.zip"), "Archives");
        assert_eq!(classify_file("code.rs"), "Code");
        assert_eq!(classify_file("script.sh"), "Scripts");
        assert_eq!(classify_file("file_without_extension"), "Other");
    }
}

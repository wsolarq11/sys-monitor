import os

path = 'src/services/file_watcher_service.rs'
with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Fix 1: Add use std::fmt
content = content.replace(
    'use std::collections::HashMap;',
    'use std::collections::HashMap;\nuse std::fmt;'
)

# Fix 2: Replace ToString with Display
old = '''impl ToString for FileEventType {
    fn to_string(&self) -> String {
        match self {
            FileEventType::Created => "Created".to_string(),
            FileEventType::Modified => "Modified".to_string(),
            FileEventType::Deleted => "Deleted".to_string(),
        }
    }
}'''

new = '''impl fmt::Display for FileEventType {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            FileEventType::Created => write!(f, "Created"),
            FileEventType::Modified => write!(f, "Modified"),
            FileEventType::Deleted => write!(f, "Deleted"),
        }
    }
}'''

content = content.replace(old, new)

# Fix 3: Replace len() > 0 with !is_empty()
content = content.replace('sample_files.len() > 0', '!sample_files.is_empty()')

with open(path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)

print('All fixes applied successfully')

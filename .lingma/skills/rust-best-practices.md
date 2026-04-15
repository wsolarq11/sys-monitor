# Rust Best Practices Skill

## 概述

本 Skill 封装了 Rust 语言的安全、性能和工程化最佳实践，帮助 Agent 编写高质量、符合 Rust 惯用法的代码。

**适用场景**:
- 编写新的 Rust 代码
- 重构现有 Rust 代码
- 代码审查和安全检查
- 性能优化建议

## 核心原则

### 1. 内存安全优先
- ✅ 使用所有权系统避免数据竞争
- ✅ 优先使用引用而非克隆
- ✅ 合理使用 `Rc`/`Arc` 处理共享所有权
- ❌ 避免不必要的 `clone()`
- ❌ 避免过度使用 `unsafe`

### 2. 错误处理规范化
- ✅ 使用 `Result<T, E>` 处理可恢复错误
- ✅ 使用 `panic!` 处理不可恢复错误
- ✅ 自定义错误类型实现 `std::error::Error`
- ✅ 使用 `?` 运算符简化错误传播
- ❌ 避免使用 `.unwrap()`（测试代码除外）
- ❌ 避免使用 `.expect()` 除非有明确理由

### 3. 并发安全
- ✅ 使用 `Send` + `Sync` trait bounds
- ✅ 优先使用消息传递（`mpsc`）而非共享状态
- ✅ 使用 `Mutex`/`RwLock` 时注意死锁
- ✅ 使用 `async/await` 处理异步 I/O
- ❌ 避免在多个线程间共享可变状态

### 4. 性能优化
- ✅ 使用迭代器而非循环（零成本抽象）
- ✅ 使用 `Cow<str>` 避免不必要的字符串分配
- ✅ 使用 `smallvec` 优化小集合
- ✅ 使用 `#[inline]` 提示编译器内联
- ❌ 避免过早优化
- ❌ 避免不必要的堆分配

## 代码规范

### 命名约定
```rust
// ✅ 正确
let user_name = String::from("Alice");  // snake_case for variables
struct UserProfile { ... }               // PascalCase for types
fn calculate_total() -> u32 { ... }      // snake_case for functions
const MAX_RETRY: u32 = 3;                // SCREAMING_SNAKE_CASE for constants

// ❌ 错误
let userName = String::from("Alice");    // 不要使用 camelCase
struct user_profile { ... }              // 不要使用 snake_case for types
```

### 模块组织
```rust
// lib.rs 或 main.rs
pub mod models;      // 数据模型
pub mod services;    // 业务逻辑
pub mod utils;       // 工具函数
pub mod errors;      // 错误定义

// 每个模块独立文件
// src/models/user.rs
// src/services/auth.rs
// src/utils/validation.rs
```

### 错误处理模式
```rust
// ✅ 推荐：自定义错误类型
#[derive(Debug)]
enum AppError {
    Io(std::io::Error),
    Parse(std::num::ParseIntError),
    NotFound(String),
}

impl std::fmt::Display for AppError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            AppError::Io(e) => write!(f, "IO error: {}", e),
            AppError::Parse(e) => write!(f, "Parse error: {}", e),
            AppError::NotFound(msg) => write!(f, "Not found: {}", msg),
        }
    }
}

impl std::error::Error for AppError {}

// 实现 From trait 便于使用 ? 运算符
impl From<std::io::Error> for AppError {
    fn from(error: std::io::Error) -> Self {
        AppError::Io(error)
    }
}

// ✅ 使用 Result 返回
fn read_config(path: &str) -> Result<Config, AppError> {
    let content = std::fs::read_to_string(path)?;  // 自动转换 IoError
    let config: Config = serde_json::from_str(&content)?;
    Ok(config)
}

// ❌ 避免：使用 unwrap
fn read_config_bad(path: &str) -> Config {
    let content = std::fs::read_to_string(path).unwrap();  // 可能 panic
    serde_json::from_str(&content).unwrap()
}
```

### 生命周期管理
```rust
// ✅ 明确标注生命周期
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}

// ✅ 使用结构体存储引用
struct Parser<'a> {
    input: &'a str,
    position: usize,
}

impl<'a> Parser<'a> {
    fn new(input: &'a str) -> Self {
        Parser { input, position: 0 }
    }
}

// ❌ 避免：不必要的生命周期标注
fn greet(name: &str) -> String {  // 不需要标注，编译器可推断
    format!("Hello, {}!", name)
}
```

### Trait 设计
```rust
// ✅ 定义清晰的 Trait
trait Serializable {
    fn serialize(&self) -> Result<Vec<u8>, SerializationError>;
    fn deserialize(data: &[u8]) -> Result<Self, SerializationError> where Self: Sized;
}

// ✅ 提供默认实现
trait Logger {
    fn log(&self, message: &str);
    
    fn log_error(&self, error: &dyn std::error::Error) {
        self.log(&format!("ERROR: {}", error));
    }
    
    fn log_warning(&self, warning: &str) {
        self.log(&format!("WARNING: {}", warning));
    }
}

// ✅ 使用 Trait Bounds 约束泛型
fn process_items<T: Serializable + Clone>(items: Vec<T>) -> Result<(), AppError> {
    for item in items {
        let data = item.serialize()?;
        // 处理数据...
    }
    Ok(())
}
```

## 性能优化指南

### 1. 减少内存分配
```rust
// ✅ 使用字符串切片
fn process_text(text: &str) -> usize {
    text.split_whitespace().count()
}

// ❌ 避免：不必要的 String 创建
fn process_text_bad(text: String) -> usize {  // 占用所有权
    text.split_whitespace().count()
}

// ✅ 使用 Cow 避免克隆
use std::borrow::Cow;

fn normalize(input: &str) -> Cow<str> {
    if input.contains("  ") {
        Cow::Owned(input.replace("  ", " "))  // 需要修改时分配
    } else {
        Cow::Borrowed(input)  // 无需修改时借用
    }
}
```

### 2. 迭代器优化
```rust
// ✅ 使用迭代器链
let sum: i32 = numbers.iter()
    .filter(|&&x| x > 0)
    .map(|&x| x * 2)
    .sum();

// ❌ 避免：手动循环
let mut sum = 0;
for &x in &numbers {
    if x > 0 {
        sum += x * 2;
    }
}

// ✅ 使用 rayon 并行处理大数据集
use rayon::prelude::*;

let sum: i32 = numbers.par_iter()  // 并行迭代
    .filter(|&&x| x > 0)
    .map(|&x| x * 2)
    .sum();
```

### 3. 数据结构选择
```rust
// ✅ 小数组使用 smallvec
use smallvec::SmallVec;

let mut vec: SmallVec<[i32; 4]> = SmallVec::new();  // 栈上分配最多4个元素
vec.push(1);
vec.push(2);

// ✅ 频繁查找使用 HashMap
use std::collections::HashMap;

let mut map = HashMap::new();
map.insert("key", "value");

// ✅ 有序数据使用 BTreeMap
use std::collections::BTreeMap;

let mut sorted_map = BTreeMap::new();  // 按键排序
sorted_map.insert(3, "three");
sorted_map.insert(1, "one");
```

## 安全检查清单

### 编译时检查
```bash
# 启用所有 lint
cargo clippy --all-targets --all-features -- -D warnings

# 检查未使用的依赖
cargo udeps

# 检查安全漏洞
cargo audit

# 格式化检查
cargo fmt --all -- --check
```

### 常见安全问题

#### 1. 整数溢出
```rust
// ✅ 使用 saturating 操作
let result = a.saturating_add(b);  // 溢出时饱和到最大值
let result = a.checked_add(b);     // 溢出时返回 None

// ❌ 避免：直接相加可能溢出
let result = a + b;  // debug 模式 panic，release 模式回绕
```

#### 2. 资源泄漏
```rust
// ✅ 使用 Drop trait 自动清理
struct FileHandle {
    fd: std::os::unix::io::RawFd,
}

impl Drop for FileHandle {
    fn drop(&mut self) {
        unsafe { libc::close(self.fd); }  // 自动关闭文件描述符
    }
}

// ✅ 使用 RAII 模式
{
    let file = std::fs::File::create("output.txt")?;
    // 文件在此作用域结束时自动关闭
}
```

#### 3. 并发数据竞争
```rust
// ✅ 使用 Arc<Mutex<T>> 安全共享
use std::sync::{Arc, Mutex};

let data = Arc::new(Mutex::new(vec![1, 2, 3]));
let data_clone = Arc::clone(&data);

std::thread::spawn(move || {
    let mut d = data_clone.lock().unwrap();
    d.push(4);
});

// ❌ 避免：裸指针共享
static mut GLOBAL_DATA: Vec<i32> = vec![];  // 不安全！
```

## Tauri 特定最佳实践

### 1. Command 设计
```rust
// ✅ 清晰的 Command 签名
#[tauri::command]
async fn scan_folder(
    path: String,
    recursive: bool,
) -> Result<ScanResult, String> {
    // 验证输入
    if !std::path::Path::new(&path).exists() {
        return Err(format!("Path not found: {}", path));
    }
    
    // 执行扫描
    let result = perform_scan(&path, recursive).await
        .map_err(|e| e.to_string())?;
    
    Ok(result)
}

// ✅ 注册 Command
fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            scan_folder,
            get_folder_info,
            watch_folder,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

### 2. 数据库操作
```rust
// ✅ 使用连接池
use sqlx::{SqlitePool, Row};

#[derive(Clone)]
pub struct Database {
    pool: SqlitePool,
}

impl Database {
    pub async fn new(database_url: &str) -> Result<Self, sqlx::Error> {
        let pool = SqlitePool::connect(database_url).await?;
        Ok(Self { pool })
    }
    
    pub async fn save_scan_result(
        &self,
        path: &str,
        size: i64,
    ) -> Result<(), sqlx::Error> {
        sqlx::query(
            "INSERT INTO scan_results (path, size, scanned_at) VALUES (?, ?, datetime('now'))"
        )
        .bind(path)
        .bind(size)
        .execute(&self.pool)
        .await?;
        
        Ok(())
    }
}
```

### 3. 异步任务管理
```rust
// ✅ 使用 tokio 管理异步任务
use tokio::task::JoinHandle;

pub struct TaskManager {
    handles: Vec<JoinHandle<()>>,
}

impl TaskManager {
    pub fn spawn_scan(&mut self, path: String) {
        let handle = tokio::spawn(async move {
            // 执行扫描任务
            scan_folder_async(&path).await;
        });
        
        self.handles.push(handle);
    }
    
    pub async fn wait_all(&mut self) {
        for handle in self.handles.drain(..) {
            let _ = handle.await;
        }
    }
}
```

## 工具和资源

### 开发工具
```bash
# 安装 Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 常用 cargo 命令
cargo build              # 构建项目
cargo run                # 运行项目
cargo test               # 运行测试
cargo clippy             # Lint 检查
cargo fmt                # 格式化代码
cargo doc --open         # 生成文档
cargo bench              # 基准测试
```

### 质量检查
```bash
# 完整的质量检查流程
cargo fmt --all                    # 格式化
cargo clippy --all-targets -- -D warnings  # Lint
cargo test                         # 单元测试
cargo audit                        # 安全审计
cargo udeps                        # 未使用依赖
```

### CI/CD 集成
```yaml
# .github/workflows/rust.yml
name: Rust

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install Rust
        uses: dtolnay/rust-toolchain@stable
        with:
          components: clippy, rustfmt
      
      - name: Cache dependencies
        uses: Swatinem/rust-cache@v2
      
      - name: Format check
        run: cargo fmt --all -- --check
      
      - name: Lint
        run: cargo clippy --all-targets -- -D warnings
      
      - name: Test
        run: cargo test --all-features
      
      - name: Security audit
        run: cargo audit
```

## 学习资源

### 官方文档
- [The Rust Book](https://doc.rust-lang.org/book/) - 官方教程
- [Rust By Example](https://doc.rust-lang.org/rust-by-example/) - 示例代码
- [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/) - API 设计规范

### 进阶阅读
- [Rust Design Patterns](https://rust-unofficial.github.io/patterns/) - 设计模式
- [Async Book](https://rust-lang.github.io/async-book/) - 异步编程
- [Nomicon](https://doc.rust-lang.org/nomicon/) - Unsafe Rust

### 社区资源
- [r/rust](https://www.reddit.com/r/rust/) - Reddit 社区
- [This Week in Rust](https://this-week-in-rust.org/) - 每周通讯
- [Are We Web Yet?](https://www.arewewebyet.org/) - Web 开发生态

---

**最后更新**: 2026-04-15  
**版本**: v1.0.0  
**状态**: ✅ Active  
**来源**: Anthropic rust-best-practices + 项目实践经验

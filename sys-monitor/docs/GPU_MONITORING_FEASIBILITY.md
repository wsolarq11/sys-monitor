# GPU 监控可行性报告

**日期**: 2026-04-16  
**状态**: Phase 3 完成（原型实现）  
**作者**: Core Agent  

## 概述

本报告评估在 sys-monitor 项目中实现跨平台 GPU 监控的可行性，并记录当前实现的原型方案。

## 技术方案评估

### 1. NVIDIA GPU（✅ 已实现）

**支持平台**: Windows, Linux  
**数据源**: `nvidia-smi` CLI 工具  
**实现方式**: 调用外部命令解析 CSV 输出  

#### 优势
- ✅ 成熟稳定的官方工具
- ✅ 提供完整的 GPU 指标（使用率、显存、温度）
- ✅ 跨平台一致性好（Windows/Linux）
- ✅ 无需额外依赖（驱动自带）

#### 局限
- ⚠️ 仅支持 NVIDIA GPU
- ⚠️ 需要安装完整驱动（nvidia-smi 随驱动安装）
- ⚠️ 进程调用开销（每次 ~50-100ms）

#### 实现示例
```bash
nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu,name \
           --format=csv,noheader,nounits
```

输出：
```
45.0, 4096, 8192, 65, NVIDIA GeForce RTX 3070
```

---

### 2. AMD GPU（⚠️ 部分可行）

**支持平台**: Windows, Linux  
**数据源**: 
- Windows: WMI (`Win32_VideoController`) 或 AMD Adrenalin CLI
- Linux: `/sys/class/drm/` 和 `rocm-smi`

#### Windows 方案
```rust
// 通过 WMI 查询（需要 wmi crate）
let wmi_con = WMIConnection::new(COMLibrary::new()?)?;
let results: Vec<VideoController> = wmi_con.query()?;
```

**问题**:
- ❌ WMI 仅提供基础信息（型号、驱动版本），无实时使用率
- ❌ AMD Adrenalin CLI 非标准安装，不可靠

#### Linux 方案
```rust
// 读取 sysfs
let gpu_info = std::fs::read_to_string("/sys/class/drm/card0/device/gpu_busy_percent")?;
```

**问题**:
- ⚠️ 不同内核版本路径不一致
- ⚠️ 需要 root 权限访问某些传感器
- ⚠️ ROCm 仅支持专业卡（Radeon Pro）

**结论**: 暂缓实现，等待更成熟的 Rust crate

---

### 3. Intel GPU（⚠️ 有限支持）

**支持平台**: Linux  
**数据源**: `/sys/class/drm/card*/` 和 `intel_gpu_top`

#### Linux 实现
```bash
# 需要安装 intel-gpu-tools
sudo intel_gpu_top -s 1000
```

**问题**:
- ❌ 需要 root 权限
- ❌ Windows 无官方 CLI 工具
- ⚠️ 集成显卡使用率低，监控价值有限

**结论**: 暂缓实现

---

### 4. Apple Silicon（🔮 待研究）

**支持平台**: macOS (M1/M2/M3)  
**数据源**: IOKit Framework  

#### 技术挑战
- ❌ 需要 Objective-C/Swift 绑定
- ❌ Rust IOKit crate 不成熟
- ❌ Apple Silicon GPU 指标文档稀缺

#### 潜在方案
```rust
// 伪代码 - 需要 Metal framework 绑定
use metal::Device;
let device = Device::system_default().unwrap();
// 无法直接获取使用率，需要通过性能计数器间接计算
```

**结论**: 高复杂度，暂缓实现

---

## 当前实现状态

### 已完成
✅ **NVIDIA GPU 监控原型**
- 自动检测 nvidia-smi 可用性
- 获取 GPU 使用率、显存占用、温度
- 优雅降级：未检测到 GPU 时显示友好提示
- 前端组件：GpuMonitor.tsx（带进度条和温度告警）

### 代码结构
```
src-tauri/src/commands/gpu.rs
├── detect_gpu_vendor()      // 平台特定的 GPU 检测
├── get_nvidia_gpu_info()    // NVIDIA 数据获取
├── get_amd_gpu_info()       // AMD 占位符（Linux only）
└── get_gpu_info()           // 主入口命令

src/components/SystemMonitor/GpuMonitor.tsx
├── 条件渲染（支持/不支持）
├── 实时指标展示（使用率、显存、温度）
└── 可视化进度条和温度告警
```

### API 设计
```rust
#[tauri::command]
pub fn get_gpu_info() -> Result<Option<GpuInfo>, AppError>
```

返回示例（有 GPU）：
```json
{
  "vendor": "NVIDIA",
  "model": "GeForce RTX 3070",
  "usage_percent": 45.0,
  "memory_used": 4096,
  "memory_total": 8192,
  "temperature": 65
}
```

返回示例（无 GPU）：
```json
null
```

---

## 性能分析

### 调用开销
| 操作 | 耗时 | 频率 |
|------|------|------|
| nvidia-smi 调用 | 50-100ms | 每 5 秒 |
| 数据解析 | < 1ms | - |
| 前端渲染 | < 10ms | - |

### 优化建议
1. **缓存策略**: 前端 5 秒轮询已足够（GPU 变化较慢）
2. **异步调用**: Tauri command 天然异步，不阻塞 UI
3. **错误容忍**: nvidia-smi 失败时返回 None，不影响其他监控

---

## 未来改进方向

### P1: 完善 AMD/Intel 支持
- 调研 `amdgpu-sysfs` crate（Linux）
- 实现 WMI 查询（Windows AMD）
- 添加 `intel_gpu_top` 集成（需解决权限问题）

### P2: 多 GPU 支持
- 当前实现仅处理第一个 GPU
- 扩展为返回 `Vec<GpuInfo>`
- 前端支持切换查看不同 GPU

### P3: 历史数据图表
- 后端缓存最近 60 个数据点
- 前端绘制 GPU 使用率趋势图
- 类似 NetworkMonitor 的实现

### P4: Apple Silicon 支持
- 研究 Metal Performance Shaders
- 探索 `oslog` API 获取 GPU 指标
- 贡献到开源 Rust IOKit 绑定项目

---

## 风险评估

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| nvidia-smi 路径变化 | 中 | 低 | 使用 PATH 搜索而非硬编码路径 |
| 多语言系统输出格式 | 低 | 低 | `--format=csv` 保证一致性 |
| 权限不足（Linux） | 中 | 中 | 文档说明需要 video 组权限 |
| 驱动未安装 | 高 | 低 | 优雅降级，显示提示信息 |

---

## 结论

### 当前阶段（Phase 3）成果
✅ **成功实现 NVIDIA GPU 监控原型**
- 后端：跨平台检测和 nvidia-smi 集成
- 前端：美观的监控组件（支持暗色模式）
- 文档：完整的可行性分析和未来路线图

### 推荐策略
1. **短期**: 保持当前实现，收集用户反馈
2. **中期**: 根据用户需求优先级实现 AMD/Intel 支持
3. **长期**: 等待 Rust 生态成熟（更好的跨平台 crate）

### 暂缓项说明
**P3: 硬件传感器（温度/风扇）** 已明确暂缓，原因：
- 跨平台复杂度过高
- 依赖不成熟的 Rust crate
- 与 GPU 温度功能重叠（NVIDIA 已包含）

---

## 参考资料

1. [nvidia-smi 官方文档](https://developer.nvidia.com/nvidia-system-management-interface)
2. [AMD GPU SysFS](https://dri.freedesktop.org/docs/drm/gpu/amdgpu.html)
3. [Intel GPU Tools](https://gitlab.freedesktop.org/drm/igt-gpu-tools)
4. [Metal Framework Documentation](https://developer.apple.com/documentation/metal)
5. [sysinfo crate](https://docs.rs/sysinfo/) - 不包含 GPU 监控

---

**附录: 测试命令**

验证 nvidia-smi 可用性：
```bash
# Windows
where nvidia-smi

# Linux
which nvidia-smi

# 测试查询
nvidia-smi --query-gpu=name,utilization.gpu,memory.total --format=csv
```

预期输出：
```
name, utilization.gpu [%], memory.total [MiB]
NVIDIA GeForce RTX 3070, 45 %, 8192 MiB
```

# kb_magager.py 修复记录

## 修复日期
2026-06-02

## 问题概述
运行 `kb_magager.py` 时出现多个错误，导致程序无法正常执行。

---

## 修复详情

### 修复 1: 初始化参数缺少默认值
**位置**: 第 22 行  
**问题**: `__init__` 方法的参数没有默认值，导致不传参调用时报 TypeError  
**原代码**:
```python
def __init__(self, faq_file_path: str, index_path: str):
```

**修复后**:
```python
def __init__(self, faq_file_path: str = None, index_path: str = None):
```

**说明**: 添加默认值 `None`，使降级处理逻辑（`or setting.xxx`）能够正常工作

---

### 修复 2: 字符串与字典拼接错误
**位置**: 第 52-54 行  
**问题**: 尝试使用 `+` 运算符拼接字符串和字典对象  
**原代码**:
```python
with open(self.version_file, "r", encoding="utf-8") as f:
    print("获取版本信息：" + json.load(f))
    return json.load(f)
```

**修复后**:
```python
with open(self.version_file, "r", encoding="utf-8") as f:
    version_data = json.load(f)
    print("获取版本信息：", version_data)
    return version_data
```

**说明**: 
- 将 JSON 数据先赋值给变量
- 使用逗号分隔打印（而非字符串拼接）
- 避免重复读取文件

---

### 修复 3: 版本号生成逻辑错误
**位置**: 第 64 行  
**问题**: `__generate_version_info()` 调用了没有返回值的 `__init_version_info()`  
**原代码**:
```python
version_info = self.__init_version_info()
```

**修复后**:
```python
version_info = self.__get_version_info()
```

**说明**: 应该调用 `__get_version_info()` 来获取版本信息，而不是 `__init_version_info()`

---

### 修复 4: Windows 文件名包含非法字符
**位置**: 第 327 行  
**问题**: 备份名称中包含冒号 `:`，Windows 不允许文件名有此字符  
**原代码**:
```python
backup_name = f"backup_name:{version_number}_{timestamp}"
```

**修复后**:
```python
backup_name = f"backup_v{version_number}_{timestamp}"
```

**说明**: 将冒号改为下划线前缀，符合 Windows 文件命名规范

---

### 修复 5: 目录复制方法错误
**位置**: 第 336-338 行  
**问题**: 使用 `shutil.copy2()` 复制目录（该方法只能复制文件）  
**原代码**:
```python
if os.path.exists(self.index_path):
    shutil.copy2(self.index_path, os.path.join(backup_path, "index.json"))
```

**修复后**:
```python
if os.path.exists(self.index_path):
    backup_index_dest = os.path.join(backup_path, "faiss_index")
    if os.path.isdir(self.index_path):
        shutil.copytree(self.index_path, backup_index_dest)
    else:
        shutil.copy2(self.index_path, backup_index_dest)
```

**说明**: 
- 判断是目录还是文件
- 目录使用 `shutil.copytree()`
- 文件使用 `shutil.copy2()`

---

## 测试结果

修复后程序正常运行，输出如下：

```
====知识库管理系统=====
获取版本信息： {'current_version': '1.0.0', 'versions': [], 'created_at': '2026-06-02T15:32:12.492935'}
当前FAQ数量：14
知识库验证：成功
获取版本信息： {'current_version': '1.0.0', 'versions': [], 'created_at': '2026-06-02T15:32:12.492935'}
获取版本信息： {'current_version': '1.0.0', 'versions': [], 'created_at': '2026-06-02T15:32:12.492935'}
创建备份成功：backup_v1.0.1_20260602153757
备份创建成功：backup_v1.0.1_20260602153757
获取版本信息： {'current_version': '1.0.1', 'versions': [{'version': '1.0.1', 'backup_name': 'backup_v1.0.1_20260602153757', 'timestamp': '20260602153757', 'description': '测试备份', 'faq_count': 14}], 'created_at': '2026-06-02T15:32:12.492935'}
备份数量：1
```

---

## 修复统计

| 修复项 | 行数 | 错误类型 |
|--------|------|----------|
| 初始化参数默认值 | 22 | TypeError |
| 字符串拼接字典 | 52-54 | TypeError |
| 版本号生成逻辑 | 64 | AttributeError |
| Windows 文件名规范 | 327 | WinError 267 |
| 目录复制方法 | 336-338 | PermissionError |

**总计**: 修复 5 处错误，涉及 8 行代码

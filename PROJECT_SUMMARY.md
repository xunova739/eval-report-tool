# 标注评测报告生成工具 - 项目总结

## 项目概述

**项目名称**: 标注评测报告生成工具 (eval-report-tool)

**技术栈**:
- Python 3.9
- Streamlit (Web框架)
- pandas + openpyxl (Excel处理)
- OpenAI SDK (LLM API调用)
- python-docx (Word导出)

**功能模块**:
- 数据上传与清洗
- AI解析统计口径
- 口径配置确认
- 自动统计计算
- 评测报告生成
- Bad Case / Good Case 筛选导出

---

## 文件结构

```
eval-report-tool/
├── app.py              # 主应用入口 (~2100行)
├── domain_1.py         # 领域模型层 (Condition, Metric, StatsResult 等)
├── domain_1_1.py       # 异常定义层
├── services_2_1.py     # 数据服务 (DataService)
├── services_2_2.py     # LLM 服务 (LLMService)
├── prompts_3.py        # Prompt 模板
├── config_5.py         # 配置管理
├── exports_6.py        # 导出服务 (Word/Excel)
├── utils_7.py          # 格式化工具
├── utils_7_2.py        # 验证与自动修复工具
└── requirements.txt    # 依赖列表
```

---

## 已解决的问题

### 1. Python 3.9 类型注解兼容性

**问题**: Python 3.9 不支持 `X | Y` 联合类型语法

**解决**: 使用 `Optional[X]` 或 `Union[X, Y]`

```python
# 错误写法
def foo() -> int | None:

# 正确写法
from typing import Optional
def foo() -> Optional[int]:
```

### 2. Python 3.9 tuple 类型注解

**问题**: `tuple[bool, str]` 在 Python 3.9 中报错

**解决**: 从 typing 导入 Tuple

```python
from typing import Tuple
def test_connection(self) -> Tuple[bool, str]:
```

### 3. ���文引号语法错误

**问题**: 代码中混入了 Unicode 中文引号 `""` 导致语法错误

**解决**: 批量替换为英文引号

```python
# 错误
text = ""你好""

# 正确
text = '"你好"'
```

### 4. UI 中文化

**解决**: 通过 CSS 自定义样式实现中文化，包括：
- 文件上传按钮
- 右上角菜单（菜单、设置、录制等）

---

## 当前未解决的坑

（坑1~3 均已解决，详见 BUGS_AND_SOLUTIONS.md）

---

## 依赖版本

```
streamlit==1.38.0
pandas==2.2.0
openpyxl==3.1.2
openai==1.40.0
python-docx==1.1.0
Pillow==10.4.0
httpx==0.27.2   # 重要：需固定此版本，避免代理参数兼容问题
```

---

## 启动命令

```bash
cd /Users/xunova/claude code 反代/eval-report-tool
python3 -m streamlit run app.py --server.port 8502
```

访问地址: http://localhost:8502

---

## 下一步排查建议

1. **API 问题**: 请用户提供具体的错误截图和 API 配置信息（隐藏密钥）
2. **Excel 上传**: 检查浏览器控制台错误，尝试清除缓存
3. **UI 英文**: 评估是否接受 CSS 方案的局限性

---

## 更新日志

| 日期 | 修改内容 |
|------|----------|
| 2026-03-18 | 修复 Python 3.9 类型注解兼容性 |
| 2026-03-18 | 修复中文引号语法错误 |
| 2026-03-18 | 添加 UI 中文化 CSS |
| 2026-03-18 | 优化 API 连接测试错误处理 |
| 2026-03-22 | v2.0 面向对象架构重构（新增 domain_1、services_2_1 等模块） |
| 2026-03-22 | 修复 prompts_3.py 中 _GSB_RULES JSON 示例大括号未转义问题 |
| 2026-03-22 | 修复 StatsResult 不可迭代（session_state 改为存 dict） |
| 2026-03-22 | 修复分组统计所有分组均显示 0 的问题（self.df 被 set_dataframe_and_calculate 覆盖） |
| 2026-03-22 | 修复 apply_condition 不兼容 dict 格式条件导致 Case 筛选报错 |
| 2026-03-22 | 简化指标编辑 UI：删除 OR 组独立编辑区，统一用 AND/OR 开关控制 |
| 2026-03-22 | 新增 migrate_or_conditions_to_flat() 将 AI 解析的 OR 结构平铺 |
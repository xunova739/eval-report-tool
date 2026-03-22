# 知识文档库 - Bug 记录与解决方案

> 记录本项目开发过程中遇到的所有问题，供后续参考。
> 版本：v2.0.0 (面向对象重构版)

---

## BUG-001：Python 3.9 类型注解不兼容

**发现时间**: 2026-03-18
**文件**: `llm_service.py`, `app.py`

**错误信息**:
```
TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'
```

**根本原因**:
Python 3.10 引入了 `X | Y` 联合类型语法，Python 3.9 不支持。

**错误代码**:
```python
def test_connection(self) -> tuple[bool, str]:
def read_excel_cached(file_bytes: bytes, header_index: int | None):
```

**修复方案**:
```python
from typing import Optional, Tuple
def test_connection(self) -> Tuple[bool, str]:
def read_excel_cached(file_bytes: bytes, header_index: Optional[int]):
```

---

## BUG-002：中文引号导致语法错误

**发现时间**: 2026-03-18
**文件**: `app.py`

**错误信息**:
```
SyntaxError: invalid character '"' (U+201C)
```

**根本原因**:
代码中混入了中文全角引号 `""`，Python 无法识别。

**修复方案**:
批量替换为英文引号：
```python
replacements = {
    '\u201c': '"',  # "
    '\u201d': '"',  # "
    '\u2018': "'",  # '
    '\u2019': "'",  # '
}
```

**预防措施**:
编辑器开启"显示不可见字符"，避免输入中文标点到代码中。

---

## BUG-003：CSS 导致文件上传功能失效

**发现时间**: 2026-03-18
**文件**: `app.py`

**现象**:
文件上传区域可见但无法点击，完全失效。

**根本原因**:
```css
/* 这行代码隐藏了整个上传组件，包括点击区域 */
.stFileUploader section {
    display: none;
}
```

**修复方案**:
删除该 CSS，使用精确选择器只替换文字：
```css
.stFileUploader label[data-testid="stFileUploaderDropzoneInstructions"] > div > span {
    font-size: 0 !important;
}
.stFileUploader label[data-testid="stFileUploaderDropzoneInstructions"] > div > span::before {
    font-size: 14px;
    content: "拖拽文件到此处";
}
```

**教训**:
修改 CSS 前必须验证不影响组件的交互功能。

---

## BUG-004：httpx 版本过高导致 API 连接失败

**发现时间**: 2026-03-18
**文件**: `llm_service.py`

**错误信息**:
```
连接失败：当前依赖版本与代理参数不兼容，请将 httpx 固定为 0.27.2
```

**根本原因**:
httpx 0.28+ 移除了 `proxies` 参数，OpenAI SDK 内部调用时传递了该参数，导致报错。

**修复方案**:
```bash
python3 -m pip install httpx==0.27.2
```

并在 `requirements.txt` 中锁定版本：
```
httpx==0.27.2
```

**验证方法**:
```bash
python3 -c "import httpx; print(httpx.__version__)"
# 输出应为：0.27.2
```

---

## BUG-005：OpenAI SDK 代理设置导致中转站报错

**发现时间**: 2026-03-18
**文件**: `llm_service.py`

**错误信息**:
```
连接失败：代理设置异常，请检查代理配置
```

**根本原因**:
OpenAI SDK 会自动读取系统环境变量中的代理设置（`HTTP_PROXY`, `HTTPS_PROXY`），中转站 API 不支持代理转发，导致连接失败。

**错误代码**:
```python
# 这种方式会继承系统代理
client = OpenAI(api_key=key, base_url=url, timeout=30.0)
```

**修复方案**:
```python
import httpx
from openai import OpenAI

http_client = httpx.Client(
    timeout=30.0,
    proxies=None,
    trust_env=False  # 关键：不读取环境变量中的代理
)
client = OpenAI(
    api_key=api_key,
    base_url=base_url,
    http_client=http_client
)
```

**适用场景**:
所有使用中转站 API 的场景（aihubmix、deepseek 等非官方 OpenAI 接口）。

---

## BUG-006：st.image() 参数不兼容

**发现时间**: 2026-03-18
**文件**: `app.py`

**错误信息**:
```
TypeError: image() got an unexpected keyword argument 'use_container_width'
```

**根本原因**:
Streamlit 1.38.0 的 `st.image()` 不支持 `use_container_width` 参数。

**修复方案**:
```python
# 错误
st.image(img, use_container_width=True)

# 正确
st.image(img, width=600)
```

---

## BUG-007：Streamlit 服务启动卡住

**发现时间**: 2026-03-18

**现象**:
服务启动后卡在邮箱输入提示，无法正常访问。

**根本原因**:
Streamlit 首次启动会询问是否订阅邮件，在 headless 环境下会卡住。

**修复方案**:
启动时加入 `--server.headless true` 参数：
```bash
python3 -m streamlit run app.py --server.port 8502 --server.headless true
```

或者提前配置：
```bash
echo "" | python3 -m streamlit run app.py --server.port 8502
```

---

## BUG-008：视觉模型与文本模型混用

**发现时间**: 2026-03-18

**现象**:
配置了 DeepSeek V3 后，截图口径解析功能无法使用。

**根本原因**:
DeepSeek V3 是纯文本模型，不支持图片输入。截图解析需要多模态视觉模型。

**解决方案**:

| 功能 | 所需模型类型 | 推荐模型 |
|------|------------|---------|
| 文字/Excel 口径解析 | 文本模型 | deepseek-v3, glm-4, qwen-plus |
| 截图口径解析 | 视觉模型 | glm-4v, qwen-vl-max, gpt-4o |

---

## BUG-009：numerator_logic 与条件类型不匹配

**发现时间**: 2026-03-21
**文件**: `services_2_1.py`, `prompts_3.py`

**现象**:
指标统计结果异常，分子计数不符合预期（通常偏低或 0）。

**根本原因**:
AI 解析生成的 JSON 中，`numerator_or_conditions` 非空，但 `numerator_logic` 被错误设置为 `"and"`。
```json
{
  "name": "服装还原",
  "numerator_or_conditions": [
    [{"field": "上装服装问题", "op": "contains", "value": "L2 上装还原问题"}],
    [{"field": "下装服装问题", "op": "contains", "value": "L2 下装还原问题"}]
  ],
  "numerator_logic": "and"  // ❌ 错误：应该是 "or"
}
```

**修复方案**:
1. 在 `prompts_3.py` 中强化了 Prompt，明确 `numerator_logic` 的填写规则
2. 在 `utils_7_2.py` 中实现验证逻辑，确认口径时检查并显示警告

**预防措施**:
- 确认口径时，检查 `numerator_logic` 是否与条件类型匹配
- Prompt 中增加了明确的 bad/good 示例

---

## BUG-010：旧文件与新文件架构冲突

**发现时间**: 2026-03-22
**文件**: `data_processor.py`, `llm_service.py`, `export_utils.py`, `prompts.py`

**现象**:
项目重构后，存在旧文件和新文件同时存在的情况，可能导致导入混乱。

**根本原因**:
v2.0 重构采用了新的模块化架构，但旧文件未删除：

| 旧文件 | 新文件 | 处理 |
|--------|--------|------|
| `data_processor.py` | `services_2_1.py` + `domain_1.py` | 删除 |
| `llm_service.py` | `services_2_2.py` | 删除 |
| `export_utils.py` | `exports_6.py` | 删除 |
| `prompts.py` | `prompts_3.py` | 删除 |

**修复方案**:
```bash
# 删除旧文件
rm data_processor.py llm_service.py export_utils.py prompts.py
```

---


---

## BUG-011：app.py 中缺失辅助函数导致运行错误

**发现时间**: 2026-03-22
**文件**: `app.py`, `services_2_1.py`

**现象**:
删除旧文件 data_processor.py 后，app.py 中调用的 `remove_duplicates()` 和 `get_column_summary()` 函数丢失。

**根本原因**:
这两个函数原本在 data_processor.py 中，但在重构为 services_2_1.py 时未迁移，因为是作为辅助函数在 app.py 中使用的。

**修复方案**:
1. 在 app.py 中添加了 `remove_duplicates()` 和 `get_column_summary()` 函数定义
2. 这两个函数是辅助函数，不属于服务层，保留在 app.py 中更合适

**经验教训**:
删除旧文件前，需要确认所有函数调用都已迁移或有新的替代方案。

---

## BUG-012：calculate_metrics_with_grouping 函数缺失

**发现时间**: 2026-03-22
**文件**: `services_2_1.py`, `domain_1.py`

**现象**:
app.py 中调用了 `calculate_metrics_with_grouping()` 函数，但 services_2_1.py 中没有定义。

**根本原因**:
原 data_processor.py 中有这个函数，但重构时未迁移到新的 DataService 类中。

**修复方案**:
1. 在 services_2_1.py 的 DataService 类中添加了 `calculate_metrics_with_grouping()` 方法
2. 在 domain_1.py 的 StatsResult 类中添加了 `group_results` 字段

**新增方法签名**:
```python
def calculate_metrics_with_grouping(
    self,
    metrics_config: MetricsConfig,
    group_field: str
) -> StatsResult:
    """分组统计模式，按分组字段拆分数据分别计算"""
```

---

## BUG-013：format_stats_for_prompt 导入路径错误

**发现时间**: 2026-03-22
**文件**: `app.py`, `utils_7.py`, `exports_6.py`

**现象**:
app.py 中从 exports_6 导入 `format_stats_for_prompt`，但该函数实际在 utils_7.py 中。

**修复方案**:
修改导入语句：
```python
# 错误
from exports_6 import ExportService, format_stats_for_prompt

# 正确
from exports_6 import ExportService
from utils_7 import format_stats_for_prompt
```

---

## ENHANCEMENT-003：app.py 完成面向对象重构

**更新时间**: 2026-03-22
**文件**: `app.py`

**背景**:
v2.0 重构完成后，app.py 仍使用旧函数式 API 调用，需要适配新的类 API。

**改造内容**:
1. `clean_dataframe(df)` → `DataService(df).clean_dataframe()`
2. `build_field_distribution(df)` → `DataService(df).build_field_distribution()`
3. `apply_conditions(df, conditions)` → `DataService(df).apply_conditions(conditions)`
4. `calculate_metrics(df, config)` → `DataService(df).calculate_metrics(config)`
5. `calculate_metrics_with_comparison(...)` → `DataService(df).calculate_metrics_with_comparison(...)`
6. `calculate_metrics_with_grouping(...)` → `DataService(df).calculate_metrics_with_grouping(...)`
7. `export_to_word(...)` → `ExportService().export_to_word(...)`
8. `export_indicators_to_excel(...)` → `ExportService().export_indicators_to_excel(...)`
9. `export_filtered_cases_to_excel(...)` → `ExportService().export_filtered_cases_to_excel(...)`

**清理导入**:
- 删除未使用的导入：`format_columns_info`, `MetricsConfig`, `Metric`, `Condition`
- 修正导入路径：`format_stats_for_prompt` 从 utils_7 导入

**验证结果**:
- app.py 语法验证通过
- 应用启动正常，健康检查通过

## ENHANCEMENT-001：AI 口径解析稳定性优化

**更新时间**: 2026-03-21
**文件**: `prompts_3.py`

**背景**:
AI 解析口径时，经常出现以下问题：
1. 多选字段误用 `==` 而非 `contains`
2. `numerator_logic` 与条件类型不匹配
3. OR 语义被错误转换为 AND 条件

**优化方案**:
1. 在 `_PARSE_COMMON_RULES` 中添加了能力声明（AI 作为表格识别专家）
2. 在 OR 条件处理部分添加了正反对比 JSON 示例
3. 在 `_PARSE_OUTPUT_SCHEMA` 中明确了 `numerator_logic` 的填写规则
4. `PARSE_METRIC_EXCEL_PROMPT` 中加强了能力声明前缀

**效果**:
减少 `numerator_logic` 不匹配、`contains` 误用等常见错误，降低人工修复频次。

---

## ENHANCEMENT-002：面向对象架构重构

**更新时间**: 2026-03-22
**文件**: 全部模块

**背景**:
v1.0 版本采用函数式架构，代码分散在 5 个文件中，存在以下问题：
1. 高耦合度：`app.py` 混合 UI 和业务逻辑
2. 函数爆炸：`data_processor.py` 中 17 个函数缺乏组织
3. 无领域模型：使用裸字典传递结构化数据
4. 重复逻辑：多处存在相似的条件应用逻辑
5. 扩展困难：新增统计模式需修改多处函数

**重构方案**:
1. 创建领域模型层 (`domain_1.py`, `domain_1_1.py`)
2. 创建服务层 (`services_2_1.py`, `services_2_2.py`)
3. 创建工具层 (`utils_7.py`, `utils_7_2.py`)
4. 创建配置层 (`config_5.py`)
5. 创建导出层 (`exports_6.py`)
6. 优化 Prompt 层 (`prompts_3.py`)

**效果**:
- 代码组织：从 5 个单体文件 → 9 个模块化文件
- 数据传递：从裸字典 → 类型安全的 dataclass
- 业务逻辑：从散落在 app.py → 封装在服务类中
- 可测试性：从难以单元测试 → 服务可独立测试
- 扩展性：从违反开闭原则 → 符合开闭原则

---

## BUG-014：分组统计 self.df 被覆盖导致后续分组全部返回 0

**发现时间**: 2026-03-22
**文件**: `services_2_1.py`

**错误信息**:
分组统计结果中，第一个分组（如"手指交叉"）正常，其余分组（"手持物"、"手指下垂/手指未露出"等）全部显示 N/A (0/0)。

**根本原因**:
`calculate_metrics_with_grouping` 在循环里对每个分组调用 `set_dataframe_and_calculate(df_group, ...)`，而该方法内部会执行 `self.set_dataframe(df)`，把 `self.df` 替换成当前分组的子集。

下一个分组的过滤 `self.df[...str.contains(group_value)...]` 就在上一个分组的子集上执行，而不是原始全量数据，导致找不到任何行（返回 0 行）。

**错误代码**:
```python
for group_value in group_values:
    ...
    df_group = self.df[  # ← self.df 已经是上一组的子集！
        self.df[group_field].astype(str).str.contains(...)
    ]
    group_stats = self.set_dataframe_and_calculate(df_group, ...)  # 覆盖 self.df
```

**修复方案**:
在循环开始前保存原始 df，所有分组筛选基于 `original_df`：
```python
original_df = self.df  # 保存原始数据

for group_value in group_values:
    if group_value == "全部":
        df_group = original_df
    else:
        df_group = original_df[  # 始终从原始数据过滤
            original_df[group_field].astype(str).str.contains(str(group_value), regex=False, na=False)
        ].reset_index(drop=True)
    group_stats = self.set_dataframe_and_calculate(df_group, metrics_config)
```

**预防措施**:
任何在循环中调用 `set_dataframe_and_calculate` 的地方，都必须提前保存原始 `self.df`，否则循环会污染数据源。

---

## BUG-015：apply_condition 不支持 dict 格式条件导致 Case 筛选报错

**发现时间**: 2026-03-22
**文件**: `services_2_1.py`

**错误信息**:
```
AttributeError: 'dict' object has no attribute 'field'
File "app.py", line 992, in render_case_filter_tab
    result_df = DataService(df).filter_cases(conditions)
File "services_2_1.py", line 268, in apply_condition
    field = condition.field
```

**根本原因**:
`apply_condition` 方法假设 `condition` 是 `Condition` dataclass 对象（用 `.field`、`.op`、`.value` 访问），但 UI 层（`render_case_filter_tab`）传入的是 Python dict（用 `["field"]` 访问）。类型不匹配导致 AttributeError。

**修复方案**:
在 `apply_condition` 开头加入类型分支：
```python
if isinstance(condition, dict):
    field = condition.get("field", "")
    op = condition.get("op", "==")
    value = condition.get("value", "")
else:
    field = condition.field
    op = condition.op
    value = condition.value
```

**预防措施**:
服务层方法应对调用方传入的两种形式（dict 和 dataclass）均兼容，尤其是对外暴露的 `filter_cases`、`apply_conditions` 等 API。

---

## 经验总结

### 口径配置质量检查
1. AI 解析后检查 `numerator_logic` 是否与条件类型匹配
2. `numerator_or_conditions` 非空时，`numerator_logic` 必须为 `"or"`
3. 确认口径前验证字段名是否存在于 DataFrame 中

### Python 版本相关
1. 确认 Python 版本，使用对应的类型注解语法（`Optional`/`Union`/`Tuple`）
2. 检查 `requirements.txt` 中关键依赖版本是否锁定
3. 了解目标 Streamlit 版本支持的组件参数

### 修改 CSS 前
1. 确认选择器精确，不会误伤其他元素
2. 修改后验证组件仍可正常交互
3. 避免使用 `display: none` 隐藏功能性组件

### API 接入前
1. 确认模型类型（文本 vs 视觉）
2. 中转站必须禁用代理：`trust_env=False`
3. 锁定 httpx 版本为 0.27.2

### 代码提交前
```bash
# 验证所有新文件语法
python3 -m py_compile domain_1.py domain_1_1.py
python3 -m py_compile services_2_1.py services_2_2.py
python3 -m py_compile prompts_3.py config_5.py
python3 -m py_compile utils_7.py utils_7_2.py exports_6.py
```

---

## 新增问题记录模板

```markdown
## BUG-XXX：[问题简述]

**发现时间**: YYYY-MM-DD
**文件**: `文件名.py`

**错误信息**:
```
[错误输出内容]
```

**根本原因**:
[详细解释问题的根本原因]

**修复方案**:
```python
# 修复代码示例
```

**预防措施**:
[如何避免类似问题再次发生]
```

---

## 数据资产管理说明

本文档是项目核心数据资产，记录了我们团队在开发过程中积累的经验教训。

### 维护原则
1. **及时性**: 遇到问题立即记录，不要事后补
2. **完整性**: 包含错误信息、原因分析、修复方案
3. **可搜索**: 使用统一的编号和标签
4. **可复用**: 确保后来者能通过文档快速解决问题

### 更新流程
1. 遇到问题 → 分析原因 → 修复
2. 修复后立即更新本文档
3. 定期回顾（每月一次），合并相似问题
4. 版本发布时，更新经验总结部分

# CLAUDE.md - 项目开发规范

> 本文件会被 Claude 自动读取，用于指导本项目的开发行为。
> 版本：v2.2.1 (Bug 修复版)

---

## 用户沟通规范

**用户是代码小白，每次给出技术解释时必须包含：**

1. **现象描述**：用户在界面上会看到/感受到什么（从截图/操作视角描述）
2. **影响说明**：这个变化会造成什么效果，或者如果不修复会有什么问题
3. **白话版本**：计划/方案可以包含代码，但必须同时给出普通人能看懂的说明

示例格式：
> **你会看到**：筛选结果不需要点按钮，改了条件后表格会自动刷新。
> **影响**：节省操作步骤，数据量不超过1万行时速度很快不会卡。

---

## 项目信息

- **项目名称**: 标注评测报告生成工具
- **Python 版本**: 3.9（严格遵守）
- **运行方式**: `python3 -m streamlit run app.py --server.port 8502 --server.headless true`
- **架构版本**: v2.0 面向对象模块化架构

---

## 文件命名规范

采用 `模块号_子模块号.py` 格式：

| 模块号 | 模块名称 | 文件 |
|--------|----------|------|
| domain_1 | 领域模型层 | `domain_1.py`, `domain_1_1.py` |
| services_2 | 服务层 | `services_2_1.py`, `services_2_2.py` |
| prompts_3 | Prompt 模板 | `prompts_3.py` |
| config_5 | 配置管理 | `config_5.py` |
| exports_6 | 导出服务 | `exports_6.py` |
| utils_7 | 工具类 | `utils_7.py`, `utils_7_2.py` |

---

## 强制规范

### 1. Python 3.9 类型注解

❌ 禁止：
```python
def foo() -> int | None: ...
def bar(x: str | int): ...
def baz() -> tuple[bool, str]: ...
```

✅ 必须：
```python
from typing import Optional, Union, Tuple
def foo() -> Optional[int]: ...
def bar(x: Union[str, int]): ...
def baz() -> Tuple[bool, str]: ...
```

### 2. 依赖版本锁定

```
httpx==0.27.2     # 不可升级！0.28+ 移除 proxies 参数导致中转站报错
openai==1.30.0    # 推荐版本，1.40+ 与中转站兼容性差
streamlit==1.38.0
```

### 3. OpenAI 客户端初始化

必须使用以下方式，禁止直接传 timeout：

```python
import httpx
from openai import OpenAI

http_client = httpx.Client(
    timeout=30.0,
    proxies=None,
    trust_env=False  # 禁止读取系统代理
)
client = OpenAI(
    api_key=api_key,
    base_url=base_url,
    http_client=http_client
)
```

### 4. Streamlit 组件规范

- `st.image()` 不支持 `use_container_width`，使用 `width=600`
- CSS 不可用 `display: none` 隐藏 `.stFileUploader section`，会导致上传功能失效
- 修改 CSS 前先确认不会影响组件交互功能

---

## 口径配置规范

### numerator_logic 必须与条件类型匹配

| 条件情况 | numerator_logic 值 |
|---------|-------------------|
| 只有 `numerator_or_conditions`（非空） | `"or"` |
| 只有 `numerator_conditions`（非空） | `"and"` |
| 两者都非空 | `"or"` |

❌ 错误写法：
```json
{"numerator_or_conditions": [[...]], "numerator_logic": "and"}
```

✅ 正确写法：
```json
{"numerator_or_conditions": [[...]], "numerator_logic": "or"}
```

### 分母类型（denominator_type）说明

| 值 | 含义 |
|----|------|
| `"common"` | 使用公共分母（受 `common_denominator.conditions` 过滤） |
| `"all"` | 所有数据（忽略公共分母，全量计算） |
| `"custom"` | 自定义分母（使用 `custom_denominator_conditions`） |

### 运算符选择规则

- `categorical_with_multi` 字段（多选逗号分隔）：只能用 `contains` / `not_contains`
- `categorical` 字段（固定值）：用 `==` / `!=` / `in` / `not_in`
- "排除多个值"：用 `not_in`，value 填逗号分隔（如 `"C,D"`）

---

## Prompt 优化最佳实践

### 约束条件的写法
- 使用自然描述，不使用"固定变量词"（如 `label_col`, `category` 等假设的列名）
- 提供正反对比示例（bad/good JSON），让模型通过示例学习
- 增强模型能力声明（"你是在表格识别方面具有专业能力的 AI 专家"）

### Prompt 修改前检查
1. `python3 -m py_compile prompts_3.py` 验证语法
2. 确认 `{{` / `}}` 转义正确（f-string 格式的字典需双重大括号）
3. 确认 `_PARSE_OUTPUT_SCHEMA` 中包含 `numerator_logic` 字段

---

## 代码修改前必做

1. `python3 -m py_compile <文件名>` 验证语法
2. 检查是否有 `|` 类型注解
3. 检查 CSS 是否影响组件可点击性
4. 确认新代码与领域模型层（domain_1）的类型定义一致
5. **检查 session_state 存储列表/字典时是否需要深拷贝**

---

## 架构原则

### 分层职责
- **domain_1**: 纯数据模型，无业务逻辑
- **services_2**: 业务逻辑封装，可独立测试
- **app.py**: UI 编排，不包含业务规则

### 扩展新功能的流程
1. 在 domain_1.py 中添加新的领域模型（如需要）
2. 在 services_2_*.py 中添加服务方法
3. 在 app.py 中调用新服务

---

## v2.2.1 更新说明 (2026-03-22)

### 核心 Bug 修复

#### 1. session_state 存储列表必须用深拷贝

**问题**：`st.session_state[key_a] = my_list` 存的是引用，不是副本。如果另一个 key 也指向同一列表，修改其中一个会影响另一个。

**场景**：Case 筛选实时过滤失效——`prev_conditions` 和 `conditions` 指向同一对象，修改条件后签名比较永远相等。

```python
# ❌ 错误：存的是引用，改 conditions 也会改 prev_conditions
st.session_state[prev_conditions_key] = conditions

# ✅ 正确：存的是快照，互不影响
import copy
st.session_state[prev_conditions_key] = copy.deepcopy(conditions)
```

#### 2. fragment 内按钮不要用 st.rerun()

**问题**：`@st.fragment` 内的 `if st.button(): ... st.rerun()` 会导致双重渲染（点击触发一次，rerun 再触发一次），表现为页面闪动。

**解决**：使用 `on_click` 回调代替：

```python
# ❌ 错误：会闪动
if st.button("添加条件"):
    conditions.append(new_cond)
    st.rerun()

# ✅ 正确：无闪动
def _cb_add_cond(key):
    conditions = st.session_state.get(key, [])
    conditions.append(new_cond)
    st.session_state[key] = conditions

st.button("添加条件", on_click=_cb_add_cond, args=(conditions_key,))
```

#### 3. 预设条件填入要记录"上次选中的预设名"

**问题**：每次渲染都检查 `当前条件 != 预设条件` 就重置，导致选预设后无法添加新条件（添加后被重置回去）。

**解决**：记录 `last_applied_preset`，只在预设名称变化时才填入：

```python
selected = st.selectbox("选择预设", preset_names, key="preset_select")
last_applied = st.session_state.get("last_applied_preset", "")

if selected != "（手动配置）" and selected != last_applied:
    # 只有预设名变化时才填入
    st.session_state[conditions_key] = copy.deepcopy(preset["conditions"])
    st.session_state["last_applied_preset"] = selected
    st.rerun()
```

#### 4. GroupDimension.from_dict 参数名必须与字段名一致

**问题**：dataclass 字段名是 `group_field`，但 `from_dict` 传的是 `field=`，导致 `TypeError`。

```python
# ❌ 错误
return cls(field=data.get("field", ""), values=data.get("values", []))

# ✅ 正确
return cls(group_field=data.get("field", ""), values=data.get("values", []))
```

#### 5. build_stats_table_from_spec 要追加未匹配的指标

**问题**：该函数只遍历 `spec_descriptions`（来自 Excel），计算结果中不在 spec 的指标会被静默丢弃。

**解决**：遍历完后追加未匹配的结果：

```python
matched_result_names = set()
# ... 匹配逻辑 ...

# 追加计算了但没在 spec 里的指标
for rname, rdata in results_map.items():
    if rname not in matched_result_names:
        rows.append({"指标名称": rname, ...})
```

---

## v2.2 更新说明 (2026-03-22)

### 核心 Bug 修复

#### 分组统计 self.df 被覆盖问题

`set_dataframe_and_calculate(df_group, config)` 内部会执行 `self.set_dataframe(df)`，即把 `self.df` 替换为传入的分组子集。

**规范**：在循环中调用 `set_dataframe_and_calculate` 之前，**必须先保存原始 df**：

```python
# ✅ 正确
original_df = self.df
for group_value in group_values:
    df_group = original_df[original_df[field].str.contains(group_value)]
    self.set_dataframe_and_calculate(df_group, config)

# ❌ 错误：self.df 在第一次循环后已被覆盖
for group_value in group_values:
    df_group = self.df[self.df[field].str.contains(group_value)]
    self.set_dataframe_and_calculate(df_group, config)
```

#### apply_condition 兼容 dict 和 Condition 对象

UI 层传入的条件是 dict，服务层内部使用 Condition dataclass。`apply_condition` 已改为同时支持两种格式：

```python
if isinstance(condition, dict):
    field = condition.get("field", "")
    ...
else:
    field = condition.field
    ...
```

### session_state 只存 dict，不存领域对象

`StatsResult`、`MetricsConfig` 等 dataclass 不能直接存入 `session_state`，因为 Streamlit 重渲染时 `"groups" in stats_result` 等 `in` 操作会对 dataclass 报 TypeError。

**规范**：统计完成后立即转为 dict：
```python
stats_result = stats_result.to_dict() if hasattr(stats_result, 'to_dict') else stats_result
st.session_state["stats_result"] = stats_result
```

---



### app.py 完成面向对象适配

**变更说明**:
将 app.py 中的函数式调用改为类方法调用：

| 原函数式调用 | 新类方法调用 |
|-------------|-------------|
| `clean_dataframe(df)` | `DataService(df).clean_dataframe()` |
| `build_field_distribution(df)` | `DataService(df).build_field_distribution()` |
| `apply_conditions(df, conditions)` | `DataService(df).apply_conditions(conditions)` |
| `calculate_metrics(df, config)` | `DataService(df).calculate_metrics(config)` |
| `export_to_word(...)` | `ExportService().export_to_word(...)` |

**新增服务方法**:
- `DataService.calculate_metrics_with_grouping()` - 分组统计模式
- `StatsResult.group_results` - 分组结果字段

**辅助函数**:
以下辅助函数保留在 app.py 中（不属于服务层）:
- `remove_duplicates(df)` - 删除重复行
- `get_column_summary(df)` - 获取列摘要信息

### 导入规范

```python
# ✅ 正确的导入方式
from services_2_1 import DataService
from services_2_2 import LLMService, format_api_error
from exports_6 import ExportService
from utils_7 import format_stats_for_prompt, format_stats_result_for_display
from prompts_3 import PARSE_METRIC_EXCEL_PROMPT, REPORT_PROMPT_TEMPLATE

# ❌ 错误：导入未使用的项
# from domain_1 import MetricsConfig, Metric, Condition  # 仅在类型注解中使用
```

---

## Design System

**Always read DESIGN.md before making any visual or UI decisions.**

所有字体选择、颜色、间距和美学方向都在 `DESIGN.md` 中定义。

**核心原则**：
- 功能优先，无多余装饰
- 使用 Inter 字体（无衬线），不要使用 Times 等衬线字体
- 主色 `#0F172A`，强调色 `#10B981`（翠绿）
- 间距使用 8px 基准
- 不要偏离设计系统，除非用户明确批准

**在 QA 模式下，标记任何不符合 DESIGN.md 的代码**。

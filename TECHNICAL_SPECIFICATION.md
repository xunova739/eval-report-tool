# 标注评测报告生成工具 - 技术说明书

> 版本：v2.2.0 (Bug 修复版)
> 更新日期：2026-03-22
> 作者：Claude Code

---

## 一、系统概述

### 1.1 项目定位

标注评测报告生成工具是一款面向 AI 标注质量评估的自动化工具，采用面向对象架构设计，支持：

- **数据自动清洗**: Excel/CSV 数据上传后自动清洗、去重、字段分析
- **口径 AI 解析**: 通过大模型自动解析统计口径文档，转化为可执行的结构化条件
- **统计计算**: 支持普通模式、版本对比模式、分组统计模式
- **报告生成**: AI 自动生成评测分析报告
- **Case 筛选**: 问题案例/优质案例筛选与导出

### 1.2 技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| 运行环境 | Python | 3.9 (严格遵守) |
| Web 框架 | Streamlit | 1.38.0 |
| LLM 调用 | OpenAI SDK | 1.30.0 |
| HTTP 客户端 | httpx | 0.27.2 (不可升级) |
| 数据处理 | pandas | - |
| 文档导出 | python-docx | - |

### 1.3 架构演进

v2.0 相比 v1.0 的重大改进：

| 特性 | v1.0 (函数式) | v2.0 (面向对象) |
|------|--------------|----------------|
| 代码组织 | 5 个单体文件 | 模块化分层架构 |
| 数据传递 | 裸字典 `Dict[str, Any]` | 类型安全的 dataclass |
| 业务逻辑 | 散落在 app.py 中 | 封装在服务类中 |
| 可测试性 | 难以单元测试 | 服务可独立测试 |
| 扩展性 | 修改多处 | 开闭原则 |

---

## 二、系统架构图

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              标注评测报告生成工具 (v2.0)                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │   文件上传   │───▶│  DataService │───▶│  字段分析   │───▶│  LLMService │      │
│  │  (Excel/CSV) │    │  (数据清洗)  │    │  (类型识别)  │    │  (口径解析)  │      │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘      │
│                                                                  │              │
│                                                                  ▼              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │   Export    │◀───│  AI 报告生成  │◀───│  DataService │◀───│  MetricsConfig │  │
│  │   Service   │    │  (LLM)      │    │  (统计计算)  │    │  (人工确认)  │      │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘      │
│                                                                                 │
│                              ┌─────────────┐                                    │
│                              │ Domain Models │                                   │
│                              │ (领域模型层)  │                                   │
│                              └─────────────┘                                    │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 模块目录结构

```
eval-report-tool/
├── app.py                   # Streamlit 主入口
├── domain_1.py              # 领域模型层：Condition, Metric, MetricsConfig 等
├── domain_1_1.py            # 异常定义：ValidationError, ConfigLoadError 等
├── services_2_1.py          # 数据服务：DataService (清洗、筛选、统计)
├── services_2_2.py          # LLM 服务：LLMService (API 调用、JSON 解析)
├── prompts_3.py             # Prompt 模板：口径解析、报告生成模板
├── config_5.py              # 配置管理：APIConfig, ConfigManager
├── exports_6.py             # 导出服务：Word/Excel导出
├── utils_7.py               # 格式化工具：统计结果格式化
├── utils_7_2.py             # 验证工具：口径配置验证、自动修复
├── requirements.txt         # 依赖列表
├── temp/                    # 运行时目录
│   ├── exported/            # 导出的报告/Excel
│   └── uploaded/            # 上传的临时文件
├── CLAUDE.md                # Claude 开发规范
├── TECHNICAL_SPECIFICATION.md # 本技术说明书
├── CODE_INDEX.md            # 代码索引
├── DESIGN.md                # 设计规范
├── BUGS_AND_SOLUTIONS.md    # Bug 记录与解决方案
└── PROJECT_SUMMARY.md       # 项目总结
```

### 2.3 模块编号规则

文件命名采用 `模块号_子模块号.py` 格式：

| 模块号 | 模块名称 | 文件 |
|--------|----------|------|
| domain_1 | 领域模型层 | `domain_1.py`, `domain_1_1.py` |
| services_2 | 服务层 | `services_2_1.py`, `services_2_2.py` |
| prompts_3 | Prompt 模板 | `prompts_3.py` |
| config_5 | 配置管理 | `config_5.py` |
| exports_6 | 导出服务 | `exports_6.py` |
| utils_7 | 工具类 | `utils_7.py`, `utils_7_2.py` |

### 2.4 数据流向图

```
用户上传 Excel
      │
      ▼
┌─────────────────┐
│  DataService    │  数据清洗 → 字段分析
│  (services_2_1) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLMService     │  口径 AI 解析
│  (services_2_2) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  MetricsConfig  │  人工确认/修正
│  (domain_1)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  DataService    │  统计计算
│  (services_2_1) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  ExportService  │  报告导出
│  (exports_6)    │
└─────────────────┘
```

---

## 三、领域模型层 (domain_1)

### 3.1 枚举类型

#### 3.1.1 OperatorType - 运算符类型

```python
class OperatorType(str, Enum):
    EQ = "=="           # 等于
    NEQ = "!="          # 不等于
    CONTAINS = "contains"      # 包含
    NOT_CONTAINS = "not_contains"  # 不包含
    IS_EMPTY = "is_empty"        # 为空
    IS_NOT_EMPTY = "is_not_empty" # 不为空
    IN = "in"           # 属于
    NOT_IN = "not_in"   # 不属于
    GREATER_THAN = "greater_than"  # 大于
    LESS_THAN = "less_than"      # 小于
```

#### 3.1.2 FieldType - 字段类型

```python
class FieldType(str, Enum):
    CATEGORICAL = "categorical"              # 低基数分类
    CATEGORICAL_WITH_MULTI = "categorical_with_multi"  # 多选字段
    HIGH_CARDINALITY = "high_cardinality"    # 高基数
    SKIP = "skip"                            # 无意义字段
```

### 3.2 核心模型

#### 3.2.1 Condition - 条件

```python
@dataclass
class Condition:
    """标注筛选条件 - 数据过滤的最小单元"""
    field: str = ""      # 字段名
    op: str = "=="       # 运算符
    value: str = ""      # 比较值
```

#### 3.2.2 Metric - 指标

```python
@dataclass
class Metric:
    """统计指标定义 - 封装分子分母逻辑"""
    name: str
    numerator_conditions: List[Condition] = field(default_factory=list)
    numerator_or_conditions: List[List[Condition]] = field(default_factory=list)
    numerator_logic: str = "and"  # "and" 或 "or"
    denominator_type: str = "common"  # "common" 或 "custom"
    custom_denominator_conditions: List[Condition] = field(default_factory=list)
```

#### 3.2.3 MetricsConfig - 口径配置

```python
@dataclass
class MetricsConfig:
    """完整统计口径配置 - 系统的核心配置对象"""
    common_denominator: CommonDenominator
    metrics: List[Metric]
    field_mappings: List[FieldMapping] = field(default_factory=list)
    group_dimensions: List[GroupDimension] = field(default_factory=list)
```

### 3.3 类关系图

```
┌─────────────────┐         ┌─────────────────┐
│  Condition      │         │  FieldMapping   │
│  - field        │         │  - description  │
│  - op           │         │  - field        │
│  - value        │         │  - operator     │
└────────┬────────┘         │  - value        │
         │                  │  - confidence   │
         │                  └─────────────────┘
         ▼
┌─────────────────┐
│  Metric         │
│  - name         │
│  - conditions   │
│  - logic        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐         ┌─────────────────┐
│ MetricsConfig   │────────▶│  MetricResult   │
│ - common_denom  │  计算   │  - name         │
│ - metrics       │         │  - numerator    │
│ - field_mappings│         │  - denominator  │
│ - group_dims    │         │  - percentage   │
└─────────────────┘         └─────────────────┘
```

---

## 四、服务层 (services_2)

### 4.1 DataService - 数据服务 (services_2_1.py)

#### 4.1.1 核心方法

| 方法 | 功能 | 返回值 |
|------|------|--------|
| `clean_dataframe()` | 数据清洗 | `(DataFrame, 清洗报告)` |
| `build_field_distribution()` | 字段分析 | `Dict[str, Any]` |
| `apply_condition()` | 应用单条件 | `pd.Series (布尔)` |
| `apply_conditions()` | 应用多条件 AND | `DataFrame` |
| `apply_conditions_or()` | 应用条件组 OR | `DataFrame` |
| `calculate_metrics()` | 计算统计指标 | `StatsResult` |

#### 4.1.2 数据清洗流程

```
┌─────────────────────────────────────────┐
│  数据清洗拦截链                          │
├─────────────────────────────────────────┤
│  1. 列名清理 (去除首尾空格)               │
│  2. 全空行删除                           │
│  3. 重复行检测                           │
│  4. 空值统计                             │
└─────────────────────────────────────────┘
```

#### 4.1.3 字段分析规则

```
阈值：threshold = 50, 高唯一率 = 0.8, 人名匹配 = 0.7

┌──────────────────────┐
│  开始分析字段          │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ unique_count ≤ 1?    │──是──▶ SKIP (常量列)
└──────────┬───────────┘
           │ 否
           ▼
┌──────────────────────┐
│ unique_count == 总数？│──是──▶ SKIP (全唯一列)
└──────────┬───────────┘
           │ 否
           ▼
┌──────────────────────┐
│ 唯一率 > 80%?        │──是──▶ SKIP (高唯一率)
└──────────┬───────────┘
           │ 否
           ▼
┌──────────────────────┐
│ 疑似人名？(中文 2-4 字) │──是──▶ SKIP (人名列)
└──────────┬───────────┘
           │ 否
           ▼
┌──────────────────────┐
│ unique ≤ 50?         │
└──────┬───────────────┘
       │
   ┌───┴────┐
   │ 是     │ 否
   ▼        ▼
┌─────┐  ┌──────────────┐
│含逗号│  │HIGH_CARDINAL │
└──┬──┘  └──────────────┘
   │
┌──┴─────┐
│是   │否
▼      ▼
MULTI  CATEGORICAL
```

### 4.2 LLMService - LLM 服务 (services_2_2.py)

#### 4.2.1 核心方法

| 方法 | 功能 |
|------|------|
| `call_text()` | 发送文本对话请求 |
| `call_multimodal()` | 发送文本 + 图片请求 |
| `parse_json_response()` | 提取并解析 JSON（支持截断修复） |
| `test_connection()` | 测试 API 连接 |

#### 4.2.2 JSON 解析流程

```
LLM 响应
    │
    ▼
┌─────────────────┐
│ 尝试直接解析     │──成功──▶ 返回
└────────┬────────┘
         │ 失败
         ▼
┌─────────────────┐
│ 提取 ```json 代码块│──成功──▶ 返回
└────────┬────────┘
         │ 失败
         ▼
┌─────────────────┐
│ 直接匹配{...}   │──成功──▶ 返回
└────────┬────────┘
         │ 失败
         ▼
┌─────────────────┐
│ 修复截断的 JSON  │──成功──▶ 返回
└────────┬────────┘
         │ 失败
         ▼
┌─────────────────┐
│ 抛出 ValueError │
└─────────────────┘
```

---

## 五、拦截条件详解

### 5.1 运算符自动修正

**触发条件**: 字段类型 = `categorical_with_multi`

**修正规则**:
- `==` → `contains`
- `!=` → `not_contains`
- `in` → `contains`
- `not_in` → `not_contains`

**原因**: 多选字段单元格可能包含多个值（如"L1 问题，L2 问题"），必须使用 contains 匹配。

### 5.2 值模糊匹配修正

**触发条件**: 条件值不在字段有效值列表中

**匹配算法**: `difflib.get_close_matches`

**相似度阈值**:
- 值长度 ≤ 4: cutoff = 0.85
- 值长度 > 4: cutoff = 0.70

### 5.3 等级编码修正

**触发条件**:
1. 条件值包含 L 编号（如"L2 问题"）
2. 条件值不在有效值列表中
3. 口径文本中存在其他 L 编号

**修正规则**:
1. 从条件值提取关键词（前 2 字）和 L 编号
2. 在口径文本中搜索关键词所在行
3. 提取该行的所有 L 编号
4. 尝试替换 L 编号匹配有效值

---

## 六、统计模式说明

### 6.1 普通模式

```
输入:
  - 数据：DataFrame
  - 口径配置：MetricsConfig

处理:
  1. 应用公共分母条件 → 分母数据集
  2. 对每个指标:
     a. 确定分母 (公共/自定义)
     b. 应用分子条件 → 分子数据集
     c. 计算百分比 = 分子数 / 分母数 * 100

输出:
  {
    "denominator_count": 1000,
    "denominator_description": "全部数据",
    "results": [
      {"name": "指标 1", "numerator": 850, "denominator": 1000,
       "percentage": 85.0, "status": "ok"}
    ]
  }
```

### 6.2 版本对比模式

```
输入:
  - 数据：DataFrame
  - 口径配置：MetricsConfig
  - 对比字段：如"版本"
  - 版本 A 值：如"v1.0"
  - 版本 B 值：如"v2.0"

处理:
  1. 按对比字段拆分 → df_a, df_b
  2. 分别计算统计指标
  3. 计算 Gap = percentage_b - percentage_a
  4. 判断趋势：improved/declined/unchanged

输出:
  {
    "compare_field": "版本",
    "version_a": "v1.0",
    "version_b": "v2.0",
    "results": [
      {
        "name": "指标 1",
        "percentage_a": 80.0,
        "percentage_b": 85.0,
        "gap": 5.0,
        "trend": "improved"  // ↑
      }
    ]
  }
```

### 6.3 分组统计模式

```
输入:
  - 数据：DataFrame
  - 口径配置：MetricsConfig
  - 分组字段：如"场景类型"

处理:
  1. 获取分组字段的所有唯一值
  2. 添加"全部"作为总计组
  3. 对每个分组值:
     a. 筛选该分组的数据
     b. 计算统计指标

输出:
  {
    "group_field": "场景类型",
    "groups": ["全部", "室内", "室外", "夜间"],
    "results": [
      {
        "name": "指标 1",
        "全部": {"numerator": 850, "denominator": 1000, "percentage": 85.0},
        "室内": {"numerator": 350, "denominator": 400, "percentage": 87.5},
        ...
      }
    ]
  }
```

---

## 七、Prompt 工程说明 (prompts_3.py)

### 7.1 口径解析通用规则

核心规则包括：
1. **字段类型决定运算符**: categorical_with_multi 只能用 contains/not_contains
2. **分母理解规则**: "全部数据" → conditions 为空数组
3. **OR 条件处理**: "满足任意一个条件" → numerator_or_conditions
4. **numerator_logic 匹配**: 使用 OR 条件时必须设置`numerator_logic: "or"`
5. **等级代码精确匹配**: L3 问题不能写成 L0/L1/L2

### 7.2 输出 Schema

```json
{
  "common_denominator": {
    "description": "分母的文字描述",
    "type": "all",
    "conditions": []
  },
  "metrics": [{
    "name": "指标名称",
    "numerator_conditions": [...],
    "numerator_or_conditions": [],
    "numerator_logic": "and",
    "denominator_type": "common",
    "custom_denominator_conditions": []
  }],
  "field_mappings": [{
    "description": "口径中的原始描述",
    "field": "映射到的实际字段名",
    "operator": "运算符",
    "value": "映射到的实际值",
    "confidence": 95
  }],
  "group_dimensions": [...]
}
```

### 7.3 提示词优化原则

世界第一的提示词工程原则：

1. **角色定义前置**: "你是一名在表格识别、语义理解和数据分析方面具有专业能力的 AI 专家"
2. **结构化规则**: 用清晰的层级组织规则（【】符号分隔模块）
3. **正误示例对比**: 明确告诉模型什么对什么错（❌ 禁止，✅ 正确）
4. **思维链引导**: 告诉模型思考步骤（第一步、第二步、第三步）
5. **输出约束**: 明确输出格式，禁止多余内容（"严格输出以下 JSON 格式，不要输出其他内容"）

---

## 八、导出服务 (exports_6.py)

### 8.1 导出格式

| 导出类型 | 文件格式 | 内容 |
|----------|----------|------|
| 评测报告 | Word (.docx) | 标题、统计概览、表格、AI 报告正文 |
| 统计表 | Excel (.xlsx) | 指标名称、分子、分母、百分比 |
| 口径配置 | JSON | 完整的 MetricsConfig |
| 原始数据 | Excel (.xlsx) | 清洗后的 DataFrame |
| 筛选 Case | Excel (.xlsx) | 筛选后的数据子集 |

### 8.2 Word 导出样式

- 标题字体：Microsoft YaHei, 22pt, 颜色 #1d6f64
- 正文字体：Microsoft YaHei, 11pt
- 表头背景：#1d6f64 (深绿色), 白色文字
- 趋势符号：↑ (改善), ↓ (退化), → (持平)

---

## 九、配置管理 (config_5.py)

### 9.1 API 配置

```python
@dataclass
class APIConfig:
    api_key: str = ""
    base_url: str = ""
    model_name: str = "glm-4"
```

### 9.2 配置文件

- `.api_config.json`: API 配置持久化
- `.env`: 环境变量

### 9.3 默认阈值

```python
DEFAULT_THRESHOLDS = {
    "field_dist_threshold": 50,  # 字段分布低基数阈值
    "field_dist_high_unique_ratio": 0.8,  # 高唯一率阈值
    "field_dist_name_match_ratio": 0.7,  # 人名匹配阈值
    "confidence_high": 80,  # 高置信度阈值
    "confidence_medium": 60,  # 中置信度阈值
}
```

---

## 十、Python 3.9 类型注解规范

### 10.1 强制要求

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

### 10.2 依赖版本锁定

```
httpx==0.27.2     # 不可升级！0.28+ 移除 proxies 参数
openai==1.30.0    # 推荐版本，1.40+ 兼容性差
streamlit==1.38.0
```

---

## 十一、验证与测试

### 11.1 语法验证

```bash
python3 -m py_compile domain_1.py
python3 -m py_compile services_2_1.py
python3 -m py_compile services_2_2.py
# ... 对所有新文件执行
```

### 11.2 功能验证

```bash
# 启动应用
python3 -m streamlit run app.py --server.port 8502 --server.headless true
```

### 11.3 测试清单

- [ ] 数据上传与清洗
- [ ] 字段分布分析
- [ ] 口径 Excel 解析
- [ ] 口径人工确认与修正
- [ ] 统计计算（普通模式）
- [ ] 统计计算（版本对比）
- [ ] 统计计算（分组统计）
- [ ] AI 报告生成
- [ ] Word 导出
- [ ] Excel 导出
- [ ] Case 筛选

---

## 十二、版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v2.0.0 | 2026-03-22 | 面向对象重构，模块化架构 |
| v1.0.0 | 2026-03-21 | 初始版本，函数式架构 |

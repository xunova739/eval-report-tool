# 代码索引与编号总览 (v2.0 面向对象版)

> 版本：v2.2.0
> 更新日期：2026-03-22

---

## 文件级编号

### 核心模块

| 编号 | 文件名 | 模块类型 | 作用 |
|------|--------|----------|------|
| #01 | `app.py` | 应用层 | 项目主控，负责页面交互、流程编排 |
| #02 | `domain_1.py` | 领域模型层 | Condition, Metric, MetricsConfig 等核心模型 |
| #03 | `domain_1_1.py` | 领域模型层 | ValidationError, ConfigLoadError 等异常定义 |
| #04 | `services_2_1.py` | 服务层 | DataService (数据清洗、筛选、统计) |
| #05 | `services_2_2.py` | 服务层 | LLMService (API 调用、JSON 解析) |
| #06 | `prompts_3.py` | Prompt 层 | 口径解析与报告生成的提示词模板 |
| #07 | `config_5.py` | 配置层 | APIConfig, ConfigManager (配置管理) |
| #08 | `exports_6.py` | 导出层 | ExportService (Word/Excel导出) |
| #09 | `utils_7.py` | 工具层 | 格式化工具 (统计结果格式化) |
| #10 | `utils_7_2.py` | 工具层 | 验证工具 (口径配置验证、自动修复) |

### 技术文档

| 编号 | 文件名 | 作用 |
|------|--------|------|
| #D01 | `TECHNICAL_SPECIFICATION.md` | 完整技术说明书 |
| #D02 | `CLAUDE.md` | 项目开发规范 |
| #D03 | `BUGS_AND_SOLUTIONS.md` | Bug 记录与解决方案 |
| #D04 | `CODE_INDEX.md` | 本文件，代码索引 |

---

## 领域模型层详细编号 (domain_1.py)

### 枚举类型

| 编号 | 名称 | 作用 |
|------|------|------|
| [DOM-001-01] | `OperatorType` | 运算符类型枚举 (==, !=, contains 等) |
| [DOM-001-02] | `FieldType` | 字段类型枚举 (categorical, multi 等) |
| [DOM-001-03] | `DenominatorType` | 分母类型枚举 (common, custom) |
| [DOM-001-04] | `NumeratorLogic` | 分子逻辑类型 (and, or) |
| [DOM-001-05] | `MetricStatus` | 指标状态枚举 (ok, denominator_zero) |

### 数据类

| 编号 | 名称 | 作用 |
|------|------|------|
| [DOM-001-10] | `Condition` | 标注筛选条件 (字段 + 运算符 + 值) |
| [DOM-001-11] | `CommonDenominator` | 公共分母配置 |
| [DOM-001-12] | `FieldMapping` | 口径描述到实际字段的映射 |
| [DOM-001-13] | `GroupDimension` | 分组维度配置 |
| [DOM-001-14] | `Metric` | 统计指标定义 (分子/分母逻辑) |
| [DOM-001-15] | `MetricResult` | 单个指标的统计结果 |
| [DOM-001-16] | `MetricsConfig` | 完整统计口径配置 |
| [DOM-001-17] | `StatsResult` | 统计计算结果容器 |

---

## 异常层详细编号 (domain_1_1.py)

| 编号 | 名称 | 作用 |
|------|------|------|
| [EXC-001-01] | `DomainException` | 领域层基础异常 |
| [EXC-001-02] | `ValidationError` | 验证失败异常 |
| [EXC-001-03] | `ConfigLoadError` | 配置加载失败异常 |
| [EXC-001-04] | `DataServiceError` | 数据服务异常 |
| [EXC-001-05] | `DataFilterError` | 数据筛选失败异常 |
| [EXC-001-06] | `ExportError` | 导出失败异常 |

---

## 服务层详细编号

### DataService (services_2_1.py)

| 编号 | 方法名 | 作用 |
|------|--------|------|
| [SVC-D-001-01] | 常量定义 | FIELD_DIST_THRESHOLD 等阈值配置 |
| [SVC-D-001-10] | `DataService` | 数据处理服务类 |
| [SVC-D-001-11] | `set_dataframe` | 设置 DataFrame |
| [SVC-D-001-20] | `clean_dataframe` | 数据清洗 |
| [SVC-D-001-30] | `build_field_distribution` | 构建字段分布 |
| [SVC-D-001-31] | `get_field_distribution` | 获取字段分布 |
| [SVC-D-001-40] | `apply_condition` | 应用单个条件 |
| [SVC-D-001-41] | `apply_conditions` | 应用多条件 AND |
| [SVC-D-001-42] | `apply_conditions_or` | 应用条件组 OR |
| [SVC-D-001-50] | `filter_cases` | Case 筛选 |
| [SVC-D-001-60] | `calculate_metrics` | 计算统计指标 |
| [SVC-D-001-61] | `_calculate_single_metric` | 计算单个指标 (内部) |
| [SVC-D-001-62] | `_apply_numerator_or` | 应用分子 OR 条件 (内部) |
| [SVC-D-001-70] | `calculate_metrics_with_comparison` | 版本对比统计 |
| [SVC-D-001-71] | `set_dataframe_and_calculate` | 设置数据并计算 |
| [SVC-D-001-72] | `calculate_metrics_with_grouping` | 分组统计模式 |

### LLMService (services_2_2.py)

| 编号 | 方法名 | 作用 |
|------|--------|------|
| [SVC-L-002-01] | `format_api_error` | 格式化 API 错误为中文 |
| [SVC-L-002-02] | `get_column_values` | 获取列唯一值 |
| [SVC-L-002-03] | `format_columns_info` | 格式化字段信息 |
| [SVC-L-002-10] | `LLMService` | LLM 服务类 |
| [SVC-L-002-11] | `call_text` | 发送文本对话请求 |
| [SVC-L-002-12] | `call_multimodal` | 发送多模态请求 |
| [SVC-L-002-13] | `parse_json_response` | 提取并解析 JSON |
| [SVC-L-002-14] | `_try_repair_truncated_json` | 修复截断的 JSON |
| [SVC-L-002-15] | `test_connection` | 测试 API 连接 |

---

## Prompt 层详细编号 (prompts_3.py)

| 编号 | 名称 | 作用 |
|------|------|------|
| [PROMPT-001] | `_PARSE_COMMON_RULES` | 口径解析通用规则 |
| [PROMPT-002] | `_PARSE_OUTPUT_SCHEMA` | 口径解析输出 Schema |
| [PROMPT-003] | `PARSE_METRIC_EXCEL_PROMPT` | Excel 口径解析 Prompt |
| [PROMPT-004] | `_GSB_RULES` | GSB 对比场景专用规则 |
| [PROMPT-005] | `PARSE_METRIC_GSB_PROMPT` | GSB 对比口径解析 Prompt |
| [PROMPT-006] | `REPORT_PROMPT_TEMPLATE` | 报告生成 Prompt |
| [PROMPT-007] | `EMPTY_METRICS_CONFIG` | 空的默认配置 |

---

## 工具层详细编号

### utils_7.py (格式化)

| 编号 | 函数名 | 作用 |
|------|--------|------|
| [utils_7-001-01] | `format_stats_result_for_display` | 格式化统计结果为 DataFrame |
| [utils_7-001-02] | `format_stats_for_prompt` | 格式化统计结果为 Prompt 文本 |
| [utils_7-001-03] | `_format_single_grouping` | 格式化单个分组维度 (内部) |
| [utils_7-001-04] | `format_condition_as_text` | 格式化条件为可读文本 |
| [utils_7-001-05] | `format_conditions_as_text` | 格式化条件列表 |
| [utils_7-001-06] | `format_stats_result_for_grouping` | 格式化分组统计结果为 DataFrame |
### utils_7_2.py (验证器)

| 编号 | 函数名 | 作用 |
|------|--------|------|
| [utils_7-002-01] | `validate_metrics_config` | 验证口径配置 |
| [utils_7-002-02] | `validate_field_mappings` | 检查字段映射置信度 |
| [utils_7-002-03] | `auto_fix_operators` | 自动修正运算符 |
| [utils_7-002-04] | `auto_fix_values` | 自动修正值 (模糊匹配) |
| [utils_7-002-05] | `auto_fix_level_codes` | 自动修正等级编号 (L0/L1/L2/L3) |

### app.py 辅助函数 (不属于服务层)

| 函数名 | 作用 |
|--------|------|
| `remove_duplicates` | 删除重复行 |
| `get_column_summary` | 获取列摘要信息 |
| `extract_group_dimensions_from_spec` | 从口径 Excel 表头提取分组维度 |
| `extract_spec_descriptions` | 从口径 Excel 提取各行描述列 |
| `build_stats_table_from_spec` | 以口径 Excel 结构为基准构建统计表 |
| `migrate_or_conditions_to_flat` | 将 AI 解析的 OR 条件组平铺到 numerator_conditions |
| `auto_fix_level_codes` | 自动修正口径中的等级编号 |

---

## 导出层详细编号 (exports_6.py)

| 编号 | 方法名 | 作用 |
|------|--------|------|
| [EXP-006-01] | `set_cell_shading` | 设置 Word 单元格背景色 |
| [EXP-006-02] | `_add_markdown_to_doc` | 添加 Markdown 到 Word |
| [EXP-006-03] | `_add_formatted_text` | 添加带格式文本 |
| [EXP-006-04] | `format_stats_for_prompt` | 格式化统计结果为 Prompt(在 utils_7.py 中) |
| [EXP-006-02] | `_add_markdown_to_doc` | 添加 Markdown 到 Word |
| [EXP-006-03] | `_add_formatted_text` | 添加带格式文本 |
| [EXP-006-10] | `ExportService` | 导出服务类 |
| [EXP-006-11] | `export_to_word` | 导出 Word 报告 |
| [EXP-006-12] | `export_indicators_to_excel` | 导出指标 Excel |
| [EXP-006-13] | `export_filtered_cases_to_excel` | 导出筛选 Case |
| [EXP-006-14] | `export_full_report` | 导出完整报告包 |
| [EXP-006-15] | `_format_stats_for_excel` | 格式化统计结果为 Excel |

---

## 配置层详细编号 (config_5.py)

| 编号 | 名称 | 作用 |
|------|------|------|
| [CFG-005-01] | `APIConfig` | API 配置数据类 |
| [CFG-005-10] | `ConfigManager` | 配置管理器 |
| [CFG-005-11] | `get_config_path` | 获取配置文件路径 |
| [CFG-005-12] | `load_api_config` | 加载 API 配置 |
| [CFG-005-13] | `save_api_config` | 保存 API 配置 |
| [CFG-005-14] | `delete_api_config` | 删除 API 配置 |
| [CFG-005-15] | `load_env` | 加载环境变量 |
| [CFG-005-20] | `DEFAULT_API_CONFIG` | 默认 API 配置 |
| [CFG-005-21] | `DEFAULT_OUTPUT_DIR` | 默认输出目录 |
| [CFG-005-22] | `DEFAULT_THRESHOLDS` | 默认阈值配置 |

---

## 面向对象改造理解

### 架构分层
```
┌─────────────────────────────────────┐
│           app.py (UI 层)             │  负责页面交互和流程编排
├─────────────────────────────────────┤
│  services_2_*.py (服务层)           │  业务逻辑封装，可独立测试
├─────────────────────────────────────┤
│  domain_1.py (领域模型层)           │  核心数据模型，类型安全
├─────────────────────────────────────┤
│  utils_7_*.py (工具层)              │  通用工具函数
└─────────────────────────────────────┘
```

### 核心设计原则
1. **领域模型无逻辑**: domain_1.py 中的 dataclass 只包含数据和简单转换方法
2. **服务层封装业务**: 所有业务逻辑放在 services_2_*.py 的类方法中
3. **工具层可复用**: utils_7_*.py 提供通用工具，不依赖具体业务
4. **UI 层只编排**: app.py 只负责调用服务和展示，不包含业务规则

### 扩展新功能的流程
1. 在 `domain_1.py` 中添加新的领域模型（如需要）
2. 在 `services_2_*.py` 中添加服务方法
3. 在 `utils_7_*.py` 中添加工具函数（如需要）
4. 在 `app.py` 中调用新服务

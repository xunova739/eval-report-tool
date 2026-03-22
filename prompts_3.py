"""
[prompts_3-001] 提示词模板模块
负责口径解析与报告生成的标准提示词配置

核心职责:
- 提供口径解析的通用规则和输出 Schema
- 提供 Excel 解析、GSB 对比、报告生成等场景的 Prompt 模板
- 提供空的默认配置

为什么这样设计:
将提示词集中管理，便于版本控制、优化和复用，
同时确保 AI 解析的一致性。

世界第一的提示词优化原则:
1. 角色定义前置：让模型进入专家角色
2. 结构化规则：用清晰的层级组织规则
3. 正误示例对比：明确告诉模型什么对什么错
4. 思维链引导：告诉模型思考步骤
5. 输出约束：明确输出格式，禁止多余内容
"""

# ==================== 口径解析通用规则 ====================

# [PROMPT-001] 口径解析通用规则
# 定义字段类型、运算符、核心原则、OR 条件处理等关键规则
_PARSE_COMMON_RULES = """
你是一名在表格识别、语义理解和数据分析方面具有专业能力的 AI 专家。
你能够准确识别表格中的复杂逻辑关系、多层级条件和等级编号。

【字段分布说明】
每个字段有以下类型：
- type=categorical：有固定可选值的标签列，values 列出了该字段数据中实际出现的所有值，用 == / != / in / not_in 匹配
- type=categorical_with_multi：多选字段，单元格内可能包含多个逗号分隔的值，options 列出了所有独立选项，必须用 contains / not_contains 匹配，不能用 == 或 in
- type=high_cardinality：高基数列（ID/路径/自由文本等），值不固定
- type=skip：系统过滤掉的无意义列，不要使用

【可用运算符】
- "==": 等于某个具体值
- "!=": 不等于某个具体值
- "contains": 单元格内容包含某个子串（用于多选字段，如单元格值为"L2 问题，L1 问题"时匹配"L2"）
- "not_contains": 单元格内容不包含某个子串
- "is_empty": 值为空/NaN
- "is_not_empty": 值不为空/NaN
- "in": 值属于某几个选项之一（value 用英文逗号分隔）
- "not_in": 值不属于某几个选项（value 用英文逗号分隔）

【核心原则：先理解字段，再理解口径，最后做映射】

第一步：看字段分布
- 拿到口径描述后，先在字段分布里找语义最接近的字段
- 字段名可能和口径描述不完全一致，需要语义推断（如"生成状态"对应口径里的"是否生成"）

第二步：看字段的实际值
- categorical 字段有明确的 values，要从这里找最匹配的值
- categorical_with_multi 字段有明确的 options，每个 option 是独立选项，从这里找匹配值
- 不要自造值，不要假设值的格式

第三步：选择运算符（字段类型决定运算符，这是硬性规则）
- categorical_with_multi 字段：只能用 contains 或 not_contains，绝对禁止用 ==、!=、in、not_in
- categorical 字段有明确二值（如"是/否"）时，"不为空/有值"映射为 == 正向值，而不是 is_not_empty
- categorical 字段是自由文本时，"不为空"才用 is_not_empty
- categorical 字段"剔除/排除 X 和 Y"时，用 not_in，value 填"X,Y"

【分母理解规则】
- 口径中出现"全部数据"、"所有记录"、"总数"、"汇总"、"评测总数"等描述时，分母 conditions 必须为空数组 []
- 空 conditions 表示不过滤，即全部数据作为分母
- 不要把文字描述当成条件，description 字段只填简短说明即可

【OR 条件处理 - 极其重要】
口径中"满足任意一个条件"是 OR 逻辑，必须用 numerator_or_conditions，不能用 numerator_conditions（AND）。

识别 OR 语义的关键词：
- "任意一个"、"其中一个"、"至少一个"
- "或"、"or"
- "存在 X 问题"（多个字段中任意一个有问题）
- "整体异常"、"整体不还原"（多个子字段中任意一个异常）

典型 OR 场景：
1. "字段 A 或 字段 B 满足某条件" → numerator_or_conditions: [[{{"field":"字段 A","op":"contains","value":"目标值"}}], [{{"field":"字段 B","op":"contains","value":"目标值"}}]]
2. "整体异常"（多个子字段中任意一个有问题）→ 每个字段单独一组，组间 OR
3. "存在 X 问题或 Y 问题" → 两个字段各一组，组间 OR

❌ 错误示例（禁止）：
把"字段 A 或 字段 B"写成 numerator_conditions: [{{"field":"字段 A","op":"contains","value":"目标值"}}, {{"field":"字段 B","op":"contains","value":"目标值"}}]
这是 AND 逻辑（两个条件同时满足），完全错误！

✅ 正确示例：
{{
  "name": "服装还原",
  "numerator_or_conditions": [
    [{{"field": "上装服装问题", "op": "contains", "value": "L2 上装还原问题"}}],
    [{{"field": "下装服装问题", "op": "contains", "value": "L2 下装还原问题"}}]
  ],
  "numerator_conditions": [],
  "numerator_logic": "or"
}}

【numerator_logic 必须与实际条件类型匹配 - 极其重要】
- 使用了 numerator_or_conditions（非空列表）→ numerator_logic 必须填 "or"
- 只使用了 numerator_conditions（且 numerator_or_conditions 为空）→ numerator_logic 必须填 "and"

❌ 混用错误：
{{
  "numerator_or_conditions": [[...]],  // 非空
  "numerator_logic": "and"             // 错误！应为 "or"
}}

✅ 正确：
{{
  "numerator_or_conditions": [[...]],  // 非空
  "numerator_logic": "or"             // 正确匹配
}}

【categorical_with_multi 字段的排除逻辑】
- categorical_with_multi 字段排除某值：必须用 not_contains，绝对不能用 not_in
- 例：排除某选项 → {{"field":"问题字段","op":"not_contains","value":"无问题"}}

【等级代码精确匹配 - 极其重要】
口径中出现的等级编号（L0、L1、L2、L3 等）必须与条件 value 中的等级编号完全一致：
- "无 L3 问题" → not_contains 的 value 必须包含 "L3"，绝对不能写成 L0/L1/L2
- "出现 L2 问题" → contains 的 value 必须包含 "L2"，绝对不能写成 L0/L1/L3
- 不同等级代表不同严重程度，混用会导致统计结果完全错误

操作步骤（必须按顺序）：
第一步：从口径描述中提取准确的等级编号。例如"L3 为肢体异常" → 提取到 L3
第二步：到字段分布的 values/options 中，找包含该编号的选项。例如在"肢体问题分类"的 options 中找含"L3"的项
第三步：将该选项原文作为 value。例如找到"L3 肢体问题" → value="L3 肢体问题"

❌ 错误（常见陷阱，绝对禁止）：
口径描述"L3 为肢体异常" → 生成 {{"op": "contains", "value": "L0 肢体问题"}}
原因：把 L3 误识别/误替换成了 L0，这是完全错误的！

✅ 正确：
口径描述"L3 为肢体异常" → 从字段分布找到"L3 肢体问题" → 生成 {{"op": "contains", "value": "L3 肢体问题"}}

【分组维度识别】
- 口径中如果有多层表头（如"手指状态/手持物"），前者是分组字段名，后者是具体值
- 将这些识别为 group_dimensions，field 填数据中对应的实际字段名
- "全部数据"、"汇总"等总计列不放入 group_dimensions
- 没有分组需求时 group_dimensions 为空数组 []
"""

# [PROMPT-002] 口径解析输出 Schema
# 定义 AI 解析后必须遵循的 JSON 输出格式
_PARSE_OUTPUT_SCHEMA = """
【输出要求】
严格输出以下 JSON 格式，不要输出其他内容：
{{
  "common_denominator": {{
    "description": "分母的文字描述",
    "type": "all",
    "conditions": []
  }},
  "metrics": [
    {{
      "name": "指标名称",
      "numerator_conditions": [
        {{"field": "字段名", "op": "运算符", "value": "值"}}
      ],
      "numerator_or_conditions": [],
      "numerator_logic": "and",
      "denominator_type": "common",
      "custom_denominator_conditions": []
    }}
  ],
  "field_mappings": [
    {{
      "description": "口径中的原始描述",
      "field": "映射到的实际字段名",
      "operator": "运算符",
      "value": "映射到的实际值",
      "confidence": 95
    }}
  ],
  "group_dimensions": [
    {{"field": "数据中的实际字段名", "values": ["值 1", "值 2"]}}
  ]
}}

说明：
- common_denominator.type：分母类型，"all"表示全部数据（conditions 留空），"custom"表示有过滤条件（conditions 非空）
- numerator_conditions：AND 条件列表，所有条件同时满足
- numerator_or_conditions：OR 条件组列表，每组内部 AND，组间 OR。例如"上装 L2 或下装 L2"：
  [
    [{{"field": "字段 A", "op": "contains", "value": "目标值"}}],
    [{{"field": "字段 B", "op": "contains", "value": "目标值"}}]
  ]
- 两者可同时使用：先满足 OR 条件组，再满足 AND 条件
- numerator_logic：必须与实际使用的条件类型一致
  - 使用了 numerator_or_conditions（非空）→ 必须填 "or"
  - 只使用了 numerator_conditions（且 numerator_or_conditions 为空）→ 必须填 "and"
  - 混用两者时 → 必须填 "or"（先 OR，再 AND 过滤）

confidence 评分规则：
- 95-100：字段名完全匹配，值也完全匹配
- 80-94：语义相似，能确定映射关系
- 60-79：推测匹配，有一定不确定性
- <60：无法确定，需要人工确认
"""

# ==================== Excel 口径解析 Prompt ====================

# [PROMPT-003] Excel 口径解析 Prompt
# 用于解析用户上传的口径 Excel 文件
PARSE_METRIC_EXCEL_PROMPT = """
你是一名在表格识别、语义理解和数据分析方面具有专业能力的 AI 专家。
请根据以下口径表格内容，仔细分析每个指标的实际含义，解析为结构化 JSON。

【标注数据的字段分布】
{field_distribution}

【口径 Excel 内容】
{excel_content}

【多层表头说明】
表头中的 "A/B" 格式有两种含义，请根据上下文区分：

1. 表头层级（分组维度）：如"手指状态/手持物"，说明原始 Excel 有多层表头
   - "A" 是上层分组维度（如"手指状态"）
   - "B" 是该分组下的具体子类（如"手持物"、"手指交叉"）
   - 每个 "A/B" 列对应一个独立的统计条件（对数据中某个字段按值筛选）
   - 请将分组维度体现在每个指标的条件中，确保不遗漏子分组

2. 数据值中的 "a/b" 格式：如某个单元格值为 "3/10"，表示"a 为分子，b 为分母"
   - 这是统计结果的表达方式，a 是符合条件的数量，b 是总数
   - 此时不要将其理解为层级关系

判断方法：表头行中的 "A/B" 通常是层级分组；数据行中的 "数字/数字" 通常是分子/分母。
""" + _PARSE_COMMON_RULES + _PARSE_OUTPUT_SCHEMA

# ==================== GSB 对比口径解析 Prompt ====================

# [PROMPT-004] GSB 对比场景专用规则
# GSB（Good/Same/Bad）是 A/B 对比评测的常见场景
_GSB_RULES = """
【GSB 场景专用规则】

1. 标签映射规则
- "左边好"、"左边胜"、"Left Win" → contains "左边好" 或对应原始值
- "右边好"、"右边胜"、"Right Win" → contains "右边好" 或对应原始值
- "一样好"、"平局"、"Tie" → contains "一样好" 或对应原始值
- "一样差"、"都错"、"Both Bad" → contains "一样差" 或对应原始值
- 标签值直接使用数据中的原始值，不要自造标签

2. 胜率计算口径
- 左边胜率 = 左边好 / (左边好 + 右边好 + 一样好)
- 右边胜率 = 右边好 / (左边好 + 右边好 + 一样好)
- 不含平局胜率 = 左边好 / (左边好 + 右边好)
- 如果口径中提到"排除平局"、"不含平局"，分母只取胜负，不含"一样好"

3. 分母确认
- GSB 场景分母通常是：所有有效评测数据
- 检查是否有"有效样本"、"有效评测数"等字段作为分母过滤条件
- 分母 conditions 为空表示全部评测数据

4. 分组统计
- GSB 常见分组：按问题类型、按场景、按难度等
- 分组维度放在 group_dimensions 中
- 每个分组值对应一个独立的统计条件

❌ 错误示例：
口径"左边胜率"写成 numerator_conditions: [{{"field":"结果标签","op":"==","value":"左边好"}}]
这是分子条件，没有体现胜率的分母计算！

✅ 正确示例 - 左边胜率：
{{
  "name": "左边胜率",
  "numerator_conditions": [{{"field": "评测结果", "op": "contains", "value": "左边好"}}],
  "numerator_or_conditions": [],
  "numerator_logic": "and",
  "denominator_type": "custom",
  "custom_denominator_conditions": [
    {{"field": "评���结果", "op": "in", "value": "左边好，右边好，一样好"}}
  ]
}}

✅ 正确示例 - 按问题类型分组的左边胜率：
假设数据中有"问题类型"字段，口径按类型分组统计胜率：
{{
  "name": "左边胜率 - 按问题类型",
  "group_dimensions": [
    {{"field": "问题类型", "values": ["类型 A", "类型 B", "类型 C"]}}
  ],
  ...
}}

5. OR 条件处理（GSB 场景常见）
- "左边好或右边好" → 用 numerator_or_conditions
- "非平局结果" → 用 in 匹配胜负标签，或 not_contains 排除平局标签

【GSB 典型口径解析示例】

示例 1：基础胜率统计
口径描述："左边胜率（含平局）"
{{
  "name": "左边胜率",
  "numerator_conditions": [{{"field": "对比结果", "op": "contains", "value": "左边好"}}],
  "numerator_or_conditions": [],
  "numerator_logic": "and",
  "denominator_type": "custom",
  "custom_denominator_conditions": [
    {{"field": "对比结果", "op": "in", "value": "左边好，右边好，一样好"}}
  ]
}}

示例 2：不含平局的胜率
口径描述："左边胜率（不含平局）"
{{
  "name": "左边胜率 - 不含平局",
  "numerator_conditions": [{{"field": "对比结果", "op": "contains", "value": "左边好"}}],
  "denominator_type": "custom",
  "custom_denominator_conditions": [
    {{"field": "对比结果", "op": "in", "value": "左边好，右边好"}}
  ]
}}

示例 3：某问题类型的左边胜率
口径描述："图像质量问题 - 左边胜率"
{{
  "name": "图像质量问题 - 左边胜率",
  "numerator_conditions": [
    {{"field": "问题类型", "op": "==", "value": "图像质量"}},
    {{"field": "对比结果", "op": "contains", "value": "左边好"}}
  ],
  "numerator_or_conditions": [],
  "numerator_logic": "and",
  "denominator_type": "custom",
  "custom_denominator_conditions": [
    {{"field": "问题类型", "op": "==", "value": "图像质量"}},
    {{"field": "对比结果", "op": "in", "value": "左边好，右边好，一样好"}}
  ]
}}
"""

# [PROMPT-005] GSB 对比口径解析 Prompt
# 专门用于 GSB 对比场景的口径解析
PARSE_METRIC_GSB_PROMPT = """
你是一名数据分析专家，擅长 GSB（Good/Same/Bad）对比评测分析。

【GSB 场景说明】
- GSB 是一种 A/B 对比评测方法，比较两个模型/方案的效果
- 数据中有"左边好"、"右边好"、"一样好"、"一样差"等评测标签
- 行是子项（对应数据字段值），列是模型维度（左边/右边/一样好/一样差等）
- 分母通常一致（所有评测数据或某个子集）
- "左边"、"右边"直接对应数据中的原始值，用 contains 匹配

【标注数据的字段分布】
{field_distribution}

【口径说明】
{metric_description}
""" + _PARSE_COMMON_RULES + _GSB_RULES + _PARSE_OUTPUT_SCHEMA

# ==================== 报告生成 Prompt ====================

# [PROMPT-006] 报告生成模板
# 用于 AI 生成标注评测报告
REPORT_PROMPT_TEMPLATE = """
你是一名专业的 AI 标注质量分析师。
请根据以下信息撰写一份标注评测报告。

【任务背景】
{task_background}

【统计结果】
{stats_text}

{comparison_text}

【报告结构要求】
1. 总体结论（2-3 句话概括本次评测整体质量水平）
2. 核心指标分析（逐个指标说明达标情况、是否存在风险）
3. {comparison_section}
4. 问题归因（基于数据推测可能的问题原因）
5. 改进建议（给出具体可执行的建议）

【格式要求】
- 使用 Markdown 格式
- 数据引用要准确，带百分比和具体数字
- 语言正式简洁
- 篇幅控制在 500-800 字
"""

# ==================== 空的默认配置 ====================

# [PROMPT-007] 空的默认口径配置
# 用于初始化或重置场景
EMPTY_METRICS_CONFIG = {
    "common_denominator": {
        "description": "",
        "type": "all",
        "conditions": [],
        "ai_analyzed_conditions": []
    },
    "metrics": []
}

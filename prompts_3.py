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

**第一步：看字段分布**
- 拿到口径描述后，先在字段分布里找语义最接近的字段
- 字段名可能和口径描述不完全一致，需要语义推断（如"生成状态"对应口径里的"是否生成"）
- 语义推断时，关注词根和近义词：
  - "是否XX" ≈ "XX状态" ≈ "XX标记" ≈ "is_xx" ≈ "has_xx"
  - "XX率" ≈ "XX比例" ≈ "XX占比" ≈ "XX率"
  - "还原" ≈ "恢复" ≈ "复现" ≈ "reconstruction" ≈ "restoration"
  - "异常" ≈ "错误" ≈ "问题" ≈ "缺陷" ≈ "abnormal" ≈ "error"
  - "等级/级别" ≈ "L0/L1/L2/L3" ≈ "严重程度" ≈ "severity"

**第二步：看字段的实际值（硬性约束：必须从原数据中找，不能自造）**
- categorical 字段有明确的 values，**必须**从这里找最匹配的值，禁止自造值
- categorical_with_multi 字段有明确的 options，每个 option 是独立选项，**必须**从这里找匹配值，禁止自造值
- 如果找不到完全匹配的值，选择语义最接近的，并在 confidence 中降低评分
- 不要假设值的格式，以字段分布中实际出现的值为准
- **行标签即原始值（GSB/极端case 场景）**：口径表格中作为行的标签（如"版型不还原"、"款式细节不还原"、"服装整体"、"版型极端改变"）就是数据字段中实际出现的值，不需要语义推断，直接在字段分布的 values/options 中精确查找
- **字段名模糊匹配（极其重要）**：口径描述的字段名与数据字段名可能有前缀/后缀差异，必须做语义匹配：
  - 规则1：口径描述词是数据字段名的**子串**时，视为匹配（如口径写"真实度"，数据字段叫"xxx真实度"）
  - 规则2：数据字段名是口径描述词的子串时，也视为匹配（如口径写"xxx问题"，字段叫"问题"）
  - 规则3：语义高度相近的词（同义词/近义词/缩写），同样视为匹配
  - 匹配成功但不完全精确时，confidence 降低到 65-75 并说明原因
- **禁止因字段映射困难而放弃生成条件**：如果某个指标有部分字段找不到精确匹配，仍必须：
  1. 对能匹配的字段正常生成条件
  2. 对无法匹配的字段，选择语义最近的字段，confidence 标为 60-70
  3. **绝对不允许输出空的 numerator_conditions + 空的 numerator_or_conditions**（除非该指标真的是全量分子=全量分母）

**第三步：选择运算符（字段类型决定运算符，这是硬性规则）**
- categorical_with_multi 字段：只能用 contains 或 not_contains，绝对禁止用 ==、!=、in、not_in
- categorical 字段有明确二值（如"是/否"）时，"不为空/有值"映射为 == 正向值，而不是 is_not_empty
- categorical 字段是自由文本时，"不为空"才用 is_not_empty
- categorical 字段"剔除/排除 X 和 Y"时，用 not_in，value 填"X,Y"

**categorical_with_multi 字段的 not_contains 用前缀，不枚举（极其重要）**
当 categorical_with_multi 字段的 options 中有带公共前缀的等级值（如多个 "L2-xxx"），
排除"L2 级别及以上"时：
- ✅ 正确：生成 **一条** `not_contains "L2"` 覆盖所有 L2 子项
- ❌ 错误：逐一列出所有 L2 子项的 not_contains 条件（如有 5 个 L2 子项就写 5 条）
- ❌ 严重错误：把字段里存储的 JSON 数组字符串拆成片段作为 value（如 `not_contains '["L2-身型不还原",'` 这种含引号和括号的残片）

**not_contains 的 value 必须是字段选项中独立的、干净的子串**：
- 字段存储格式是 JSON 数组：`["L2-身型不还原","L2-异常扩图..."]`
- 系统会自动对每个独立选项做子串匹配
- value 应该填 `"L2"` 或 `"L2-身型不还原"`，而不是 `"[\"L2-身型不还原\","` 这种 JSON 残片

【括号多值写法识别 - 极其重要】
口径描述中，括号内用"+"连接多个值，表示该字段的值满足其中任意一个即可（OR 逻辑）：

常见形式一：**字段值是数字或等级代码**
- `服装还原问题（0+1）` → 服装还原问题字段的值是 0 或 1 → 用 `in`，value="0,1"
- `穿着效果（0）` → 穿着效果字段的值是 0 → 用 `==`，value="0"
- `服装真实度（高+中）` → 服装真实度字段值是 高 或 中 → 用 `in`，value="高,中"
- `极端（无问题）` → 极端字段值是 无问题 → 用 `==`，value="无问题"
- `L3肢体异常（否）` → L3肢体异常字段值是 否 → 用 `==`，value="否"

**数字 0/1/2/3 与等级标签的对应规则（极其重要）**
括号内的数字是等级的**序号**，不是字面值，必须先查字段分布确认实际标签：
- **第一步**：到字段分布的 values/options 中，找该字段实际存在的等级值列表
- **第二步**：按顺序对应：0 → 最低/最好的那个值，1 → 第二个，依此类推
- **第三步**：以字段分布里的实际标签作为条件 value，不要自己造标签格式
- 字段分布里可能是 "L0xxx"、也可能是 "无问题"、"轻微"、"1分" 等任何形式——以实际值为准
- 如果字段的 values 就是纯数字 "0"/"1"/"2"，则直接用数字作为 value

**通过率场景中的括号标签处理（分两类字段，机械执行步骤，不需要推断）**

**categorical 单值字段**的 `(L0+L1)` 通过场景：
- 步骤：去字段分布找 L0 对应的实际标签 + L1 对应的实际标签 → 生成 `in "[L0实际标签],[L1实际标签]"`
- 例：字段值有"L0穿着问题","L1穿着问题","L2穿着问题"，口径`(L0+L1)` → `in "L0穿着问题,L1穿着问题"`

**categorical_with_multi 多选字段**的 `(L0+L1)` 通过场景（拆成多条 contains，放 numerator_or_conditions）：
1. 找出括号里允许的等级：如 `(L0+L1)` → L0、L1
2. 去字段分布的 options 里，找 L0 对应的**完整选项名**、L1 对应的**完整选项名**
3. **每个等级生成一条独立的 contains 条件，全部放入 numerator_or_conditions**
4. 组间 OR：只要包含其中任意一个等级就通过

示例（字段 "上装服装问题" 有选项：L0上装还原问题, L1上装还原问题, L2上装还原问题）：
- 括号内：L0、L1 → 完整名：L0上装还原问题、L1上装还原问题
- ✅ 正确输出（放 numerator_or_conditions）：
  ```
  "numerator_or_conditions": [
    [{{"field":"上装服装问题","op":"contains","value":"L0上装还原问题"}}],
    [{{"field":"上装服装问题","op":"contains","value":"L1上装还原问题"}}]
  ],
  "numerator_logic": "or"
  ```
- ❌ 错误输出：`in "L0上装还原问题,L1上装还原问题"` ← 不要用 in，要拆开
- ❌ 错误输出：`not_contains "L2上装还原问题"` ← 不用推理排除项，直接写允许的

**`(L0+L1+L2)` 三级通过场景**（同样拆成三条 contains）：
- ✅ 正确：每个等级一条 contains，放 numerator_or_conditions

**关键口诀**：
- 括号里写了哪些等级 → 每个等级单独一条 contains → 全部放 numerator_or_conditions → 组间 OR
- ❌ 不要用 `in` 运算符，必须拆成独立的 `contains` 条件

❌ 绝对禁止：只写等级前缀（如 value="L0"），必须写完整选项名（如 value="L0上装还原问题"）
❌ 绝对禁止：用 `in "L0xxx,L1xxx"` 这种写法，必须拆开

**categorical 单值字段 `(0+1)` 与 categorical_with_multi 字段 `(L0+L1)` 的区别**：
- categorical 单值字段：用 `in "L0,L1"` 放 numerator_conditions
- categorical_with_multi 多选字段：拆成多条 contains 放 numerator_or_conditions


**加号分隔的多条件公式（整体通过率场景 - 极其重要）**
口径中出现 `字段A（值）+字段B（值）+字段C（值1+值2）+...` 的连加公式时：
- 每个 `字段（值）` 是一个独立的 AND 条件
- **必须解析公式中所有的 `+` 分隔项，不能遗漏**，即使有 8 个、10 个条件也要全部输出
- 每项独立生成一条 `numerator_conditions` 条目

示例（逻辑结构说明，实际 value 必须查字段分布）：`试衣图（是）+是否存在肢体异常（否）+服装还原问题（0+1）+穿着效果（0）+服装真实度（高+中）`
→ 5 个条件全部进 numerator_conditions：
  - `试衣图对应字段 == [是的实际值]`
  - `肢体异常对应字段 == [否的实际值]`
  - `服装还原问题对应字段 in [0级实际标签,1级实际标签]`（查字段分布）
  - `穿着效果对应字段 == [0级实际标签]`（查字段分布）
  - `服装真实度对应字段 in "高,中"`（直接是字符串值则原样用）

常见形式二：**括号内是叶子类目/子类名称**
- `（上装+下装+连衣裙）款式细节不还原` → 叶子类目 in [上装, 下装, 连衣裙] AND 款式细节不还原
- 括号内是类目名，逻辑：先过滤类目，再过滤问题条件

操作步骤：
1. 识别括号前的字段名（如"服装还原问题"、"服装真实度"）
2. 到字段分布中找对应字段
3. 括号内每个值，到字段的 values 或 options 中找精确匹配
4. 如果是多个值，用 `in` 运算符，value 填逗号分隔（categorical_with_multi 字段改用多条 contains 组合）
5. 如果是单个值，用 `==` 运算符

❌ 错误：将 `服装还原问题（0+1）` 理解为注释说明而忽略括号内容
✅ 正确：将括号内容解析为字段值过滤条件

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

❌ 混用错误1（最常见的错误，绝对禁止）：
将 OR 条件放入 numerator_conditions，再用 numerator_logic: "or" — 这是完全错误的！
{{
  "numerator_conditions": [
    {{"field": "上装服装问题", "op": "contains", "value": "L2上装还原问题"}},
    {{"field": "下装服装问题", "op": "contains", "value": "L2下装还原问题"}}
  ],
  "numerator_or_conditions": [],
  "numerator_logic": "or"   // 错误！conditions 在 numerator_conditions 里，or 无效，实际执行的是 AND
}}

❌ 混用错误2：
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

【去重要求 - 极其重要】
- 同一个指标的 numerator_conditions 或 numerator_or_conditions 中，禁止出现完全相同的条件（field、op、value 三者都相同）
- 生成条件列表后，必须检查并删除重复项
- 示例：以下条件重复，只保留一个
  ❌ 错误：[
    {{"field": "是否生成", "op": "==", "value": "否"}},
    {{"field": "是否生成", "op": "==", "value": "否"}},  // 重复！
    {{"field": "肢体问题分类", "op": "contains", "value": "L3肢体问题"}}
  ]
  ✅ 正确：[
    {{"field": "是否生成", "op": "==", "value": "否"}},
    {{"field": "肢体问题分类", "op": "contains", "value": "L3肢体问题"}}
  ]

【OR 条件的正确写法 - 极其重要】
当口径描述"满足任意一个条件即为异常"（OR 逻辑）时，必须用 numerator_or_conditions：

❌ 错误写法（所有条件放 numerator_conditions，然后 numerator_logic 填 "or"）：
{{
  "numerator_conditions": [
    {{"field": "是否生成", "op": "==", "value": "否"}},
    {{"field": "肢体问题分类", "op": "contains", "value": "L3肢体问题"}},
    {{"field": "上装服装问题", "op": "contains", "value": "L2上装还原问题"}}
  ],
  "numerator_or_conditions": [],
  "numerator_logic": "or"  // 这是错误用法！
}}

✅ 正确写法（每个条件单独一组，放入 numerator_or_conditions）：
{{
  "numerator_conditions": [],
  "numerator_or_conditions": [
    [{{"field": "是否生成", "op": "==", "value": "否"}}],
    [{{"field": "肢体问题分类", "op": "contains", "value": "L3肢体问题"}}],
    [{{"field": "上装服装问题", "op": "contains", "value": "L2上装还原问题"}}]
  ],
  "numerator_logic": "or"
}}
说明：每组内部是 AND（可以有多个条件），组间是 OR。
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
- GSB 场景分母通常不是所有数据，而是**需要根据具体业务场景（如：是否生成了衣服）进行过滤的数据集**。
- 必须仔细检查口径中关于分母的说明，如果有“生成”、“有效”等前置条件，务必将其添加到分母的 conditions 中。
- 如果口径明确指明是全部数据，分母 conditions 才为空。

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

6. 多选字段在 GSB 场景中的处理
- 数据中可能有 JSON 数组格式的问题类型字段，如 ["问题A","问题B"]
- 系统已自动将这些字段识别为 categorical_with_multi，options 中是干净的选项名（不含括号和引号）
- 对多选字段必须使用 contains 运算符，绝对禁止用 ==
- 示例：
  ✅ 正确：{{"field": "左边异常类型", "op": "contains", "value": "版型极端改变"}}
  ❌ 错误：{{"field": "左边异常类型", "op": "==", "value": "版型极端改变"}}
  ❌ 错误：{{"field": "左边异常类型", "op": "==", "value": "["版型极端改变"]"}}（带括号的整个数组）

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
你是一名资深数据分析师，擅长从评测数据中挖掘关键洞察，输出高质量分析报告。

【任务背景】
{task_background}

【统计结果】
{stats_text}

{comparison_text}

---

## 写作原则（必须遵守）

### 1. 结论先行（最重要）
**报告第一段必须是一句话核心结论**，格式：
> 本次评测整体质量【优秀/良好/需改进】，核心问题是 XXX，建议优先处理 YYY。

示例：
> 本次评测整体质量良好，核心问题是人物还原率偏低（78.2%），建议优先优化服装和肢体两个模块。

### 2. 数据驱动的洞察挖掘
你必须从数据中挖掘出以下类型的"金点子"：

| 洞察类型 | 识别方法 | 输出格式 |
|---------|---------|---------|
| **异常发现** | 某指标显著低于/高于其他指标或基准 | "发现异常：XX 指标仅为 X%，远低于整体均值 Y%" |
| **趋势识别** | 多个指标呈现递增/递减模式 | "发现趋势：从 A 到 B 到 C，问题率逐步上升" |
| **对比差异** | 分组对比中某组明显不同 | "发现差异：A 组指标比 B 组高 X 个百分点" |
| **关联发现** | 某两个指标同时高/低 | "发现关联：XX 问题高发时，YY 问题也显著增加" |
| **瓶颈定位** | 拉低整体的关键子项 | "发现瓶颈：XX 子项贡献了 Y% 的问题量" |
| **优势亮点** | 表现特别好的方面 | "发现亮点：XX 指标达到 X%，表现优异" |

### 3. 每个洞察必须包含
1. **数据支撑**：具体的数字和百分比
2. **业务含义**：这个数据意味着什么
3. **行动建议**：建议做什么

---

## 报告结构

### 一、核心结论（1 段话）
一句话概括整体质量 + 核心问题 + 首要建议。

**如果是对比模式（GSB），必须包含：**
1. **胜负判定**：明确说明哪个版本整体更好（"左边模型整体优于右边模型"或反之）
2. **各维度胜负概述**：列出关键指标的胜负情况
   - 格式："在 X 个关键指标中，左边胜 Y 个，右边胜 Z 个，平局 W 个"
   - 示例："在 5 个关键指标中，左边胜 3 个（还原率、准确率、异常率），右边胜 1 个（响应速度），平局 1 个"
3. **建议**：基于胜负给出部署或优化建议

**示例（对比模式）：**
> 本次对比评测中，**左边模型整体优于右边模型**。在 6 个关键指标中，左边胜 4 个（人物还原率、场景准确率、异常检测率、细节完整度），右边胜 1 个（生成速度），平局 1 个。建议优先部署左边模型，同时关注右边模型在速度上的优势。

### 二、关键洞察（2-4 条金点子）
每条洞察使用以下模板：
```
【洞察类型】洞察标题
- 数据发现：[具体数字]
- 业务含义：[这意味着什么]
- 行动建议：[建议做什么]
```

示例：
```
【异常发现】服装还原率显著偏低
- 数据发现：服装还原率仅为 78.2%，远低于整体还原率 92.5%
- 业务含义：服装模块是当前质量的主要短板，影响用户体验
- 行动建议：优先排查服装数据标注规则是否存在歧义，考虑增加服装相关训练样本
```

### 三、指标详情
逐个核心指标分析（达标/风险/异常）。

### 四、{comparison_section}

### 五、问题归因
基于数据推断可能原因，避免空泛描述。

### 六、行动建议
按优先级排序，具体可执行。

---

## 输出要求

- 使用 Markdown 格式
- 每个数据引用必须带具体数字（X% 或 X/Y）
- 语言简洁专业，避免废话
- 篇幅 800-1200 字（重要是说清楚，不是凑字数）
- **禁止**：没有数据的空泛结论（如"整体表现良好需继续努力"）
- **禁止**：不基于数据的臆测
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

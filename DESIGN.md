# Design System — 标注评测报告生成工具设计体系

## Product Context

- **What this is:** 数据统计分析工具，用于标注评测报告生成，支持多场景统计、口径配置和报告导出
- **Who it's for:** 内部数据团队，需要快速生成评测报告的分析人员
- **Space/industry:** 数据分析工具 / 内部效率工具
- **Project type:** Web 应用 / 数据仪表板

***

## Aesthetic Direction

- **Direction:** 极简现代 (Minimal Modern)
- **Decoration level:** Minimal — 功能优先，无多余装饰
- **Mood:** 干净、专业、高效。让用户专注于数据和任务，界面不抢戏
- **Reference sites:**
  - [Linear](https://linear.app) — 项目管理工具，极简现代
  - [Vercel](https://vercel.com) — 开发平台，干净专业
  - [Notion](https://notion.so) — 知识管理，温暖灰调

***

## Typography

### 字体选择

- **Display/Hero:** Inter — 现代无衬线，清晰易读，适合中文混排
- **Body:** Inter — 与标题统一，保持一致性
- **UI/Labels:** Inter Medium (500) — 表单标签、按钮文字
- **Data/Tables:** SF Mono / Monaco / 等宽字体 — 数据展示需要 tabular-nums 特性
- **Code:** JetBrains Mono / SF Mono — 代码展示

### 字体加载

```css
/* Google Fonts CDN */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* CSS 变量 */
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
--font-mono: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
```

### 字体大小比例

| 用途         | 大小              | 字重  |
| ---------- | --------------- | --- |
| H1 页面标题    | 2.5rem (40px)   | 700 |
| H2 区块标题    | 1.5rem (24px)   | 600 |
| H3 子标题     | 1.25rem (20px)  | 600 |
| Body 正文    | 1rem (16px)     | 400 |
| Small 小字   | 0.875rem (14px) | 400 |
| Caption 说明 | 0.75rem (12px)  | 400 |

***

## Color

### 颜色策略

- **Approach:** Balanced — 主色 + 辅助色 + 强调色，语义色用于状态反馈
- **Tone:** 中性冷灰，专业稳重

### 主色板

| 名称            | 色值        | 用途                |
| ------------- | --------- | ----------------- |
| Primary 主色    | `#0F172A` | 标题、主按钮、重要文字       |
| Secondary 辅助色 | `#64748B` | 次要文字、图标、边框        |
| Accent 强调色    | `#10B981` | 成功状态、链接、选中态、主操作反馈 |

### 中性灰阶

| 名称       | 色值        | 用途         |
| -------- | --------- | ---------- |
| Gray 50  | `#F9FAFB` | 页面背景       |
| Gray 100 | `#F3F4F6` | 卡片背景、表格斑马纹 |
| Gray 200 | `#E5E7EB` | 边框、分隔线     |
| Gray 300 | `#D1D5DB` | 输入框边框      |
| Gray 400 | `#9CA3AF` | 占位符文字      |
| Gray 500 | `#6B7280` | 辅助文字       |
| Gray 600 | `#4B5563` | 正文         |
| Gray 700 | `#374151` | 强调文字       |
| Gray 800 | `#1F2937` | 标题         |
| Gray 900 | `#111827` | 最深文字       |

### 语义色

| 名称         | 色值        | 用途         |
| ---------- | --------- | ---------- |
| Success 成功 | `#10B981` | 成功提示、达标状态  |
| Warning 警告 | `#F59E0B` | 警告提示、待处理状态 |
| Error 错误   | `#EF4444` | 错误提示、危险操作  |
| Info 信息    | `#3B82F6` | 信息提示、帮助说明  |

### CSS 变量定义

```css
:root {
  /* 主色 */
  --primary: #0F172A;
  --primary-hover: #1E293B;

  /* 辅助色 */
  --secondary: #64748B;
  --secondary-hover: #475569;

  /* 强调色 */
  --accent: #10B981;
  --accent-hover: #059669;

  /* 中性色 */
  --gray-50: #F9FAFB;
  --gray-100: #F3F4F6;
  --gray-200: #E5E7EB;
  --gray-300: #D1D5DB;
  --gray-400: #9CA3AF;
  --gray-500: #6B7280;
  --gray-600: #4B5563;
  --gray-700: #374151;
  --gray-800: #1F2937;
  --gray-900: #111827;

  /* 语义色 */
  --success: #10B981;
  --warning: #F59E0B;
  --error: #EF4444;
  --info: #3B82F6;
}
```

***

## Spacing

### 间距系统

- **Base unit:** 8px
- **Density:** Compact — 紧凑布局，信息密度高

### 间距比例

| 名称  | 值    | 用途          |
| --- | ---- | ----------- |
| 2xs | 4px  | 微小间距（图标与文字） |
| xs  | 8px  | 紧凑元素间距      |
| sm  | 12px | 小间距         |
| md  | 16px | 标准间距（元素间）   |
| lg  | 24px | 区块间距        |
| xl  | 32px | 大区块间距       |
| 2xl | 48px | 页面区块间距      |
| 3xl | 64px | 最大间距        |

### CSS 变量

```css
:root {
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --space-7: 48px;
  --space-8: 64px;
}
```

***

## Layout

### 布局策略

- **Approach:** Grid-disciplined — 严格网格对齐，整齐划一
- **Max content width:** 1200px
- **Sidebar:** 可折叠侧边栏，默认展开

### 栅格系统

| 断点      | 列数   | 宽度             |
| ------- | ---- | -------------- |
| Mobile  | 4 列  | < 640px        |
| Tablet  | 8 列  | 640px - 1024px |
| Desktop | 12 列 | > 1024px       |

### 圆角层级

| 名称   | 值      | 用途         |
| ---- | ------ | ---------- |
| sm   | 4px    | 小元素（标签、徽章） |
| md   | 8px    | 按钮、输入框     |
| lg   | 12px   | 卡片、区块      |
| full | 9999px | 圆形元素、药丸按钮  |

```css
:root {
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-full: 9999px;
}
```

***

## Motion

### 动效策略

- **Approach:** Minimal-functional — 仅用于辅助理解的过渡动效
- **原则:** 不为装饰而动画，动效必须服务于用户理解

### 动效参数

| 类型        | 时长        | 缓动函数        |
| --------- | --------- | ----------- |
| Micro 微交互 | 50-100ms  | ease-out    |
| Short 短过渡 | 150-250ms | ease-out    |
| Medium 中等 | 250-400ms | ease-in-out |
| Long 长动画  | 400-700ms | ease-in-out |

### CSS 过渡

```css
/* 进入动效 */
transition: all 0.2s ease-out;

/* 退出动效 */
transition: all 0.15s ease-in;

/* 移动/状态变化 */
transition: all 0.3s ease-in-out;
```

***

## Components

### 按钮

```css
/* 主按钮 */
.btn-primary {
  background: var(--primary);
  color: white;
  padding: 8px 16px;
  border-radius: var(--radius-md);
  font-weight: 500;
}
.btn-primary:hover {
  background: var(--primary-hover);
  transform: translateY(-1px);
}

/* 次按钮 */
.btn-secondary {
  background: white;
  color: var(--gray-700);
  border: 1px solid var(--gray-300);
  padding: 8px 16px;
  border-radius: var(--radius-md);
}

/* 强调按钮 */
.btn-accent {
  background: var(--accent);
  color: white;
}

/* 危险按钮 */
.btn-danger {
  background: white;
  color: var(--error);
  border: 1px solid #FCA5A5;
}
```

### 卡片

```css
.card {
  background: white;
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}
```

### 表格

```css
.data-table th {
  background: var(--gray-50);
  font-weight: 600;
  padding: 12px;
  border-bottom: 2px solid var(--gray-200);
}

.data-table td {
  padding: 12px;
  border-bottom: 1px solid var(--gray-100);
}

.data-table tr:hover td {
  background: var(--gray-50);
}

/* 等宽数字 */
.data-table .mono {
  font-family: var(--font-mono);
  font-variant-numeric: tabular-nums;
}
```

### 徽章

```css
.badge {
  display: inline-flex;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 500;
}

.badge-success { background: #D1FAE5; color: #065F46; }
.badge-warning { background: #FEF3C7; color: #92400E; }
.badge-error { background: #FEE2E2; color: #991B1B; }
.badge-info { background: #DBEAFE; color: #1E40AF; }
```

### 步骤指示器

```css
.steps {
  display: flex;
  align-items: center;
  background: white;
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-lg);
  padding: 12px;
}

.step-number {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
}

.step.completed .step-number {
  background: var(--accent);
  color: white;
}

.step.current .step-number {
  background: var(--primary);
  color: white;
}

.step.pending .step-number {
  background: var(--gray-200);
  color: var(--gray-500);
}
```

***

## 业务组件

### 条件编辑器 (Condition Editor)

用于编辑数据筛选条件的行式编辑器，支持多条件配置。

#### 布局结构

```
┌─────────────────────────────────────────────────────────────────┐
│  字段 FIELD     │  运算符 OPERATOR  │  值 VALUE          │  ×  │  ← 表头行
├─────────────────┼──────────────────┼────────────────────┼─────┤
│  [下拉选择字段]  │  [下拉选择运算符]  │  [下拉/输入值]     │  ×  │  ← 条件行1
├─────────────────┼──────────────────┼────────────────────┼─────┤
│  [下拉选择字段]  │  [下拉选择运算符]  │  [下拉/输入值]     │  ×  │  ← 条件行2
└─────────────────┴──────────────────┴────────────────────┴─────┘
                              [+ 添加条件]
```

#### 列宽比例

| 列 | 比例 | 说明 |
|----|------|------|
| 字段 Field | 3 | 选择数据列 |
| 运算符 Operator | 2 | 选择比较方式 |
| 值 Value | 3 | 选择或输入值 |
| 删除按钮 | 0.4 | 极小，弱化视觉 |

#### 表头样式

```css
.condition-header {
  font-size: 12px;
  font-weight: 600;
  color: #64748B;  /* gray-500 */
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}
```

#### 运算符选项

| 显示名 | 值 | 说明 |
|--------|-----|------|
| 等于 | `==` | 精确匹配 |
| 不等于 | `!=` | 排除匹配 |
| 包含 | `contains` | 字符串/多选字段包含 |
| 不包含 | `not_contains` | 字符串/多选字段不包含 |
| 为空 | `is_empty` | 值为空 |
| 不为空 | `is_not_empty` | 值不为空 |
| 属于 | `in` | 多值匹配（逗号分隔） |
| 不属于 | `not_in` | 多值排除 |
| 大于 | `greater_than` | 数值比较 |
| 小于 | `less_than` | 数值比较 |

#### 值输入规则

- **分类字段**：下拉选择，从数据中取唯一值
- **多选字段 (categorical_with_multi)**：下拉选择
- **为空/不为空**：禁用输入，显示 "(无需填写)"
- **属于/不属于**：文本输入，提示 "多个值用英文逗号分隔"
- **大于/小于**：文本输入，提示 "请输入数值"

#### 删除按钮

```css
/* 条件删除按钮 - 弱化视觉 */
.condition-delete-btn {
  background: transparent !important;
  border: none !important;
  color: var(--gray-400);
  font-size: 18px;
  padding: 0 !important;
  min-height: 28px;
  width: 28px;
}
.condition-delete-btn:hover {
  color: var(--error) !important;
  background: rgba(239, 68, 68, 0.08) !important;
  border-radius: 6px;
}
```

---

### 指标卡片 (Metric Card)

用于配置单个统计指标的展开式卡片。

#### 结构

```
┌─────────────────────────────────────────────────────────────────┐
│ ▼ 指标名称                                    [删除]            │
├─────────────────────────────────────────────────────────────────┤
│ 指标名称: [________________]                                     │
│                                                                 │
│ 分子条件关系: ○ 全部满足(AND)  ○ 任一满足(OR)                    │
│                                                                 │
│ ─── 分子条件（AND/OR） ───                                      │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 字段        │ 运算符    │ 值           │ ×                │ │
│ │ [选择字段]  │ [选择]    │ [选择值]     │ ×                │ │
│ └─────────────────────────────────────────────────────────────┘ │
│ [+ 添加条件]                                                     │
│                                                                 │
│ ─── 分母选择 ───                                                │
│ 分母类型: ○ 使用公共分母  ○ 自定义分母                           │
│   └─ 公共分母时：显示当前公共分母内容（只读）                    │
│   └─ 自定义分母时：显示来源选择                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 样式

```css
/* 指标卡片 - 使用 Streamlit expander */
.metric-card {
  background: white;
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-lg);
  margin-bottom: 12px;
}

/* 卡片标题 - 指标名称 */
.metric-card-title {
  font-weight: 600;
  color: var(--gray-900);
}

/* 删除按钮 - 右侧对齐，弱化 */
.metric-delete-btn {
  background: transparent !important;
  border: none !important;
  color: var(--gray-500);
  font-size: 13px;
}
.metric-delete-btn:hover {
  color: var(--error) !important;
}
```

#### 分母来源选项（自定义分母时）

| 选项 | 值 | 说明 |
|------|-----|------|
| AI分析的分母 | `ai` | 使用AI解析的分母条件，可编辑 |
| 全部数据 | `all` | 无过滤条件 |
| 选择条件组 | `group` | 从公共分母的条件组中选择 |
| 手动配置 | `custom` | 手动添加条件 |

---

### 公共分母编辑区 (Common Denominator Editor)

用于配置所有指标共享的分母条件。

#### 结构

```
┌─────────────────────────────────────────────────────────────────┐
│ 公共分母                                                         │
├─────────────────────────────────────────────────────────────────┤
│ 分母类型: ○ AI分析  ○ 手动配置                                   │
│                                                                 │
│ ─── [AI分析模式] ───                                            │
│ AI分析的分母条件                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 条件编辑器...                                               │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ─── [手动配置模式] ───                                          │
│ [🤖 使用AI分母]  [📊 全部数据]                                   │
│                                                                 │
│ 条件组（指标自定义分母可以选择不同组）                            │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 📁 条件组1                                    [−]           │ │
│ │   条件编辑器...                                             │ │
│ │   [+ 添加条件]                                              │ │
│ └─────────────────────────────────────────────────────────────┘ │
│ [+ 添加条件组]                                                   │
│                                                                 │
│ ℹ️ 当前公共分母匹配数据量: 150 / 200 条                          │
└─────────────────────────────────────────────────────────────────┘
```

#### 实时预览

- 底部显示当前分母匹配的数据量和总数
- 使用 `st.info()` 展示，格式：`当前公共分母匹配数据量: **X** / Y 条`

---

### 条件组 (Condition Group)

可复用的条件集合，供多个指标引用。

#### 样式

```css
/* 条件组容器 */
.condition-group {
  background: white;
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-md);
  padding: 16px;
  margin-bottom: 8px;
}

/* 组名输入 */
.group-name-input {
  font-weight: 500;
  border: none;
  background: transparent;
}

/* 删除组按钮 */
.group-delete-btn {
  background: transparent;
  color: var(--gray-500);
  font-size: 16px;
}
```

#### 图标使用

- 📁 条件组图标
- 📈 指标列表图标
- 🤖 AI相关按钮
- 🗑️ 删除按钮

***

## Decisions Log

| Date       | Decision                      | Rationale                                      |
| ---------- | ----------------------------- | ---------------------------------------------- |
| 2026-03-22 | Initial design system created | 基于 Linear/Notion/Vercel 研究，采用极简现代风格，功能优先，无多余装饰 |
| 2026-03-22 | 选择 Inter 字体                   | 现代、清晰、中文兼容，避免使用过时的衬线字体（如 Times）                |
| 2026-03-22 | 选择翠绿强调色 (#10B981)             | 数据工具常用蓝/紫，绿色更清新专业，且传达"成功/正向"的语义                |
| 2026-03-22 | 8px 紧凑间距                      | 信息密集型工具，需要在有限空间展示更多数据                          |
| 2026-03-23 | 条件编辑器 4 列布局                    | 字段(3) + 运算符(2) + 值(3) + 删除(0.4)，平衡信息密度与可读性   |
| 2026-03-23 | 条件删除按钮弱化设计                     | 默认灰色透明背景，hover 时显示红色，避免误操作，不抢夺视觉焦点        |
| 2026-03-23 | 指标卡片展开式设计                      | 使用 expander 组件，默认展开，方便快速编辑多指标               |
| 2026-03-23 | 分母实时预览                        | 底部显示匹配数量，让用户直观了解配置效果                         |

***

*Created by /design-consultation on 2026-03-22*
*Updated: 2026-03-23 - 添加业务组件规范（条件编辑器、指标卡片、公共分母编辑区）*

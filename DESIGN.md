# Design System — 标注评测报告生成工具

## Product Context
- **What this is:** 数据统计分析工具，用于标注评测报告生成，支持多场景统计、口径配置和报告导出
- **Who it's for:** 内部数据团队，需要快速生成评测报告的分析人员
- **Space/industry:** 数据分析工具 / 内部效率工具
- **Project type:** Web 应用 / 数据仪表板

---

## Aesthetic Direction
- **Direction:** 极简现代 (Minimal Modern)
- **Decoration level:** Minimal — 功能优先，无多余装饰
- **Mood:** 干净、专业、高效。让用户专注于数据和任务，界面不抢戏
- **Reference sites:**
  - [Linear](https://linear.app) — 项目管理工具，极简现代
  - [Vercel](https://vercel.com) — 开发平台，干净专业
  - [Notion](https://notion.so) — 知识管理，温暖灰调

---

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
| 用途 | 大小 | 字重 |
|------|------|------|
| H1 页面标题 | 2.5rem (40px) | 700 |
| H2 区块标题 | 1.5rem (24px) | 600 |
| H3 子标题 | 1.25rem (20px) | 600 |
| Body 正文 | 1rem (16px) | 400 |
| Small 小字 | 0.875rem (14px) | 400 |
| Caption 说明 | 0.75rem (12px) | 400 |

---

## Color

### 颜色策略
- **Approach:** Balanced — 主色 + 辅助色 + 强调色，语义色用于状态反馈
- **Tone:** 中性冷灰，专业稳重

### 主色板
| 名称 | 色值 | 用途 |
|------|------|------|
| Primary 主色 | `#0F172A` | 标题、主按钮、重要文字 |
| Secondary 辅助色 | `#64748B` | 次要文字、图标、边框 |
| Accent 强调色 | `#10B981` | 成功状态、链接、选中态、主操作反馈 |

### 中性灰阶
| 名称 | 色值 | 用途 |
|------|------|------|
| Gray 50 | `#F9FAFB` | 页面背景 |
| Gray 100 | `#F3F4F6` | 卡片背景、表格斑马纹 |
| Gray 200 | `#E5E7EB` | 边框、分隔线 |
| Gray 300 | `#D1D5DB` | 输入框边框 |
| Gray 400 | `#9CA3AF` | 占位符文字 |
| Gray 500 | `#6B7280` | 辅助文字 |
| Gray 600 | `#4B5563` | 正文 |
| Gray 700 | `#374151` | 强调文字 |
| Gray 800 | `#1F2937` | 标题 |
| Gray 900 | `#111827` | 最深文字 |

### 语义色
| 名称 | 色值 | 用途 |
|------|------|------|
| Success 成功 | `#10B981` | 成功提示、达标状态 |
| Warning 警告 | `#F59E0B` | 警告提示、待处理状态 |
| Error 错误 | `#EF4444` | 错误提示、危险操作 |
| Info 信息 | `#3B82F6` | 信息提示、帮助说明 |

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

---

## Spacing

### 间距系统
- **Base unit:** 8px
- **Density:** Compact — 紧凑布局，信息密度高

### 间距比例
| 名称 | 值 | 用途 |
|------|------|------|
| 2xs | 4px | 微小间距（图标与文字） |
| xs | 8px | 紧凑元素间距 |
| sm | 12px | 小间距 |
| md | 16px | 标准间距（元素间） |
| lg | 24px | 区块间距 |
| xl | 32px | 大区块间距 |
| 2xl | 48px | 页面区块间距 |
| 3xl | 64px | 最大间距 |

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

---

## Layout

### 布局策略
- **Approach:** Grid-disciplined — 严格网格对齐，整齐划一
- **Max content width:** 1200px
- **Sidebar:** 可折叠侧边栏，默认展开

### 栅格系统
| 断点 | 列数 | 宽度 |
|------|------|------|
| Mobile | 4 列 | < 640px |
| Tablet | 8 列 | 640px - 1024px |
| Desktop | 12 列 | > 1024px |

### 圆角层级
| 名称 | 值 | 用途 |
|------|------|------|
| sm | 4px | 小元素（标签、徽章） |
| md | 8px | 按钮、输入框 |
| lg | 12px | 卡片、区块 |
| full | 9999px | 圆形元素、药丸按钮 |

```css
:root {
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-full: 9999px;
}
```

---

## Motion

### 动效策略
- **Approach:** Minimal-functional — 仅用于辅助理解的过渡动效
- **原则:** 不为装饰而动画，动效必须服务于用户理解

### 动效参数
| 类型 | 时长 | 缓动函数 |
|------|------|----------|
| Micro 微交互 | 50-100ms | ease-out |
| Short 短过渡 | 150-250ms | ease-out |
| Medium 中等 | 250-400ms | ease-in-out |
| Long 长动画 | 400-700ms | ease-in-out |

### CSS 过渡
```css
/* 进入动效 */
transition: all 0.2s ease-out;

/* 退出动效 */
transition: all 0.15s ease-in;

/* 移动/状态变化 */
transition: all 0.3s ease-in-out;
```

---

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

---

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-22 | Initial design system created | 基于 Linear/Notion/Vercel 研究，采用极简现代风格，功能优先，无多余装饰 |
| 2026-03-22 | 选择 Inter 字体 | 现代、清晰、中文兼容，避免使用过时的衬线字体（如 Times） |
| 2026-03-22 | 选择翠绿强调色 (#10B981) | 数据工具常用蓝/紫，绿色更清新专业，且传达"成功/正向"的语义 |
| 2026-03-22 | 8px 紧凑间距 | 信息密集型工具，需要在有限空间展示更多数据 |

---

*Created by /design-consultation on 2026-03-22*
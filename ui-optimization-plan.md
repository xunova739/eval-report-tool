# 标注评测报告工具 UI 优化方案

> 以"世界顶级 SaaS 产品设计"标准重新定义这个工具的用户体验

---

## 一、核心问题诊断

### 1. 信息架构问题

| 问题 | 影响 | 严重性 |
|------|------|--------|
| **10个线性步骤** | 用户认知负担过重，找不到当前位置 | 🔴 高 |
| **步骤命名数字化** | "1. 数据上传"、"2. 数据清洗报告"... 缺乏语义引导 | 🟡 中 |
| **状态不可见** | 用户不知道"我完成了什么"、"接下来要做什么" | 🔴 高 |

### 2. 视觉层次问题

| 问题 | 影响 |
|------|------|
| **所有内容平铺** | 缺乏主次之分，重要操作淹没在信息海洋中 |
| **卡片过度使用** | 到处都是 expander，视觉疲劳 |
| **颜色单调** | 只有蓝色按钮，缺乏语义化色彩系统 |

### 3. 交互反馈问题

| 问题 | 影响 |
|------|------|
| **等待无反馈** | AI 解析时只有 spinner，无进度感 |
| **成功/失败单调** | 只有 success/warning，缺乏层次 |
| **即时性差** | 改了条件需要手动点按钮才刷新 |

---

## 二、设计优化方案

### 方案 A：渐进式披露（推荐）

**核心理念**：不要一次性展示所有信息，按需展开

#### 新的信息架构

```
┌─────────────────────────────────────────────────────────┐
│  📊 标注评测报告生成工具                                   │
├─────────────────────────────────────────────────────────┤
│  [进度条: ══════════░░░░░░░░ 40%]                       │
│  上传数据 → 定义口径 → 执行统计 → 导出报告                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  当前阶段：定义口径 📍                                      │
│  ┌────────────────────────────────────────────────────┐ │
│  │ 上传口径 Excel                                      │ │
│  │ [拖拽上传区域]                                       │ │
│  │                                                     │ │
│  │ 选择评测场景                                         │ │
│  │ [卡片选择] 线上评测  GSB对比  等级对比               │ │
│  │                                                     │ │
│  │ [解析口径 →]                                        │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ✅ 已完成                                               │
│  • 数据上传 (1,234 条记录)                                │
│  • 字段确认 (12 个评估字段)                                │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

#### 关键改进

**1. 四阶段模型替代十步流程**

| 旧流程 | 新阶段 | 心智模型 |
|--------|--------|---------|
| 1-4 步 | **准备数据** | "把数据准备好" |
| 5-6 步 | **定义口径** | "告诉 AI 怎么算" |
| 7-8 步 | **执行统计** | "跑起来看结果" |
| 9-10 步 | **输出报告** | "交付成果" |

**2. 可视化进度条**

```python
# 顶部固定进度条
progress_stage = st.session_state.get("progress_stage", 0)
st.progress(progress_stage / 4, text=f"第 {progress_stage + 1} 阶段 / 共 4 阶段")
```

**3. 卡片式场景选择（替代 radio）**

```python
# 三个大卡片，视觉权重高
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div class="scene-card">
        <div class="icon">📊</div>
        <div class="title">线上评测</div>
        <div class="desc">单模型多维质量评测</div>
    </div>
    """, unsafe_allow_html=True)
```

---

### 方案 B：即时反馈系统

**核心理念**：让用户时刻知道"发生了什么"

#### 1. 实时统计预览

```
┌────────────────────────────────────────────┐
│  口径配置                                   │
│  ┌──────────────┐  ┌──────────────┐       │
│  │ 指标数量: 5   │  │ 分母: 1,234  │       │
│  │ 分组维度: 3   │  │ 条件: 12 个   │       │
│  └──────────────┘  └──────────────┘       │
│                                             │
│  预计统计时间: ~5 秒                         │
└────────────────────────────────────────────┘
```

**实现**：条件改变时实时计算统计快照

```python
@st.fragment
def show_metrics_summary():
    config = st.session_state.get("editing_metrics", {})
    metrics_count = len(config.get("metrics", []))
    conditions_count = sum(len(m.get("numerator_conditions", [])) for m in config.get("metrics", []))

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("指标数量", metrics_count)
    col2.metric("筛选条件", conditions_count)
    col3.metric("分组维度", len(config.get("group_dimensions", [])))
    col4.metric("分母类型", config.get("common_denominator", {}).get("type", "全部数据"))
```

#### 2. 智能提示系统

```python
# 根据当前状态给出下一步建议
if not st.session_state.get("df"):
    st.info("👆 第一步：上传标注数据文件（支持 .xlsx/.xls/.csv）")
elif not st.session_state.get("confirmed_metrics"):
    st.info("👆 第二步：上传口径 Excel 并解析，或手动配置指标")
elif not st.session_state.get("stats_result"):
    st.info("👆 第三步：点击「执行统计」开始计算")
```

#### 3. 状态徽章系统

```
数据状态: ✅ 已上传  ✅ 已清洗  ⏳ 待分析  ○ 待统计
```

```python
def render_status_badges():
    status_html = ""
    badges = [
        ("数据上传", bool(st.session_state.get("df"))),
        ("数据清洗", bool(st.session_state.get("clean_report"))),
        ("口径配置", bool(st.session_state.get("confirmed_metrics"))),
        ("统计完成", bool(st.session_state.get("stats_result"))),
    ]
    for name, done in badges:
        icon = "✅" if done else "○"
        status_html += f'<span class="status-badge">{icon} {name}</span> '
    st.markdown(f'<div class="status-bar">{status_html}</div>', unsafe_allow_html=True)
```

---

### 方案 C：色彩与视觉系统

#### 语义化色彩

```css
/* 状态色系 */
--color-success: #10B981;   /* 翠绿 - 完成/成功 */
--color-warning: #F59E0B;   /* 琥珀 - 警告/注意 */
--color-error: #EF4444;     /* 红色 - 错误/失败 */
--color-info: #3B82F6;      /* 蓝色 - 信息/提示 */
--color-neutral: #6B7280;   /* 灰色 - 默认/禁用 */

/* 功能色系 */
--color-primary: #0F172A;   /* 主色 - 核心操作 */
--color-secondary: #64748B; /* 次色 - 次要信息 */

/* 背景/分隔 */
--bg-page: #F9FAFB;
--bg-card: #FFFFFF;
--border-subtle: #E5E7EB;
```

#### 按钮分层

```css
/* 主按钮 - 核心动作（执行统计、生成报告） */
.stButton.primary button {
    background: #0F172A;
    color: white;
    border: none;
    font-weight: 600;
}

/* 次按钮 - 次要动作（清空、重置） */
.stButton.secondary button {
    background: white;
    color: #0F172A;
    border: 1px solid #D1D5DB;
}

/* 危险按钮 - 破坏性操作（删除、清空） */
.stButton.danger button {
    background: white;
    color: #EF4444;
    border: 1px solid #FCA5A5;
}
```

---

### 方案 D：微交互细节

#### 1. 拖拽上传区域

```
┌─────────────────────────────────────────────┐
│                                             │
│         📄 拖拽文件到此处                     │
│         或 点击选择文件                       │
│                                             │
│         支持 .xlsx .xls .csv                 │
│         最大 50MB                            │
└─────────────────────────────────────────────┘
```

#### 2. 加载状态优化

```python
# 替代单调的 spinner
with st.spinner(""):
    st.markdown("""
    <div class="loading-state">
        <div class="spinner"></div>
        <div class="loading-text">AI 正在解析口径...</div>
        <div class="loading-hint">首次解析可能需要 10-20 秒</div>
    </div>
    """, unsafe_allow_html=True)
    # 执行任务
```

#### 3. 空状态设计

```python
if not st.session_state.get("df"):
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">📊</div>
        <div class="empty-title">还没有数据</div>
        <div class="empty-desc">上传标注数据文件开始使用</div>
    </div>
    """, unsafe_allow_html=True)
```

#### 4. 数据表格增强

```css
/* 数据表格样式 */
.stDataFrame {
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    overflow: hidden;
}

/* 表头 */
.stDataFrame thead th {
    background: #F9FAFB;
    font-weight: 600;
    color: #374151;
    border-bottom: 2px solid #E5E7EB;
}

/* 高亮行（筛选结果） */
.stDataFrame tbody tr:hover {
    background: #EFF6FF;
}
```

---

## 三、实施优先级

### Phase 1：基础体验（1 天）

- [ ] 添加顶部进度条
- [ ] 实现状态徽章系统
- [ ] 优化空状态展示
- [ ] 改善加载状态

### Phase 2：交互优化（2 天）

- [ ] 实时统计预览
- [ ] 智能提示系统
- [ ] 卡片式场景选择
- [ ] 拖拽上传区域

### Phase 3：视觉升级（1 天）

- [ ] 语义化色彩系统
- [ ] 按钮分层设计
- [ ] 微交互动画
- [ ] 数据表格美化

---

## 四、关键代码示例

### 1. 顶部进度条

```python
def render_progress_bar():
    """顶部固定进度条"""
    stages = ["准备数据", "定义口径", "执行统计", "输出报告"]

    # 计算当前阶段
    if not st.session_state.get("df"):
        current = 0
    elif not st.session_state.get("confirmed_metrics"):
        current = 1
    elif not st.session_state.get("stats_result"):
        current = 2
    else:
        current = 3

    # 渲染
    cols = st.columns(len(stages))
    for i, (col, stage) in enumerate(zip(cols, stages)):
        with col:
            if i < current:
                st.success(f"✅ {stage}")
            elif i == current:
                st.info(f"📍 {stage}")
            else:
                st.text(f"○ {stage}")
```

### 2. 卡片式场景选择

```python
def render_scene_cards():
    """场景选择卡片"""
    st.markdown("### 选择评测场景")

    col1, col2, col3 = st.columns(3)

    scenes = [
        ("📊", "线上评测", "单模型多维质量评测，支持 L0/L1/L2/L3 等级"),
        ("⚖️", "GSB对比", "A/B 模型对比评测，计算胜率"),
        ("📈", "等级对比", "按等级标签统计，统一分母"),
    ]

    for col, (icon, title, desc) in zip([col1, col2, col3], scenes):
        with col:
            # 使用 container 替代 radio
            if st.button(f"{icon}\n\n{title}\n\n{desc}", use_container_width=True):
                st.session_state["template_type"] = title
                st.rerun()
```

### 3. 实时统计快照

```python
@st.fragment
def render_metrics_summary():
    """口径配置实时预览"""
    config = st.session_state.get("editing_metrics", {})

    if not config:
        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("指标数量", len(config.get("metrics", [])))

    with col2:
        conds = sum(
            len(m.get("numerator_conditions", [])) +
            sum(len(g) for g in m.get("numerator_or_conditions", []))
            for m in config.get("metrics", [])
        )
        st.metric("筛选条件", conds)

    with col3:
        st.metric("分组维度", len(config.get("group_dimensions", [])))

    with col4:
        denom_type = config.get("common_denominator", {}).get("type", "all")
        denom_label = {"all": "全部数据", "custom": "自定义", "ai": "AI 分析"}.get(denom_type, denom_type)
        st.metric("分母类型", denom_label)
```

---

## 五、设计原则

1. **渐进式披露**：不要一次展示所有信息
2. **即时反馈**：任何操作都有明确结果
3. **状态可见**：用户时刻知道"我在哪"、"完成了什么"
4. **容错设计**：允许撤销、重做、恢复
5. **语义化色彩**：颜色传达含义，不只是装饰
6. **呼吸感**：留白和间距让界面更舒适
7. **一致性**：相同功能用相同的表现形式

---

## 六、效果预期

| 维度 | 优化前 | 优化后 |
|------|--------|--------|
| **完成时间** | 新用户需要 15-20 分钟理解流程 | 5-10 分钟完成首次统计 |
| **错误率** | 20% 用户迷失在步骤中 | < 5% 错误率 |
| **满意度** | "功能强大但复杂" | "专业又易用" |
| **认知负担** | 高（10 步流程） | 低（4 阶段模型） |

---

## 七、后续迭代方向

1. **保存/恢复工作流**：用户可以保存当前状态，下次继续
2. **模板库**：预定义常见评测场景的口径配置
3. **协作功能**：分享口径配置给团队成员
4. **历史记录**：查看过去的统计任务和报告
5. **快捷操作**：键盘快捷键、批量操作

---

*"好的设计不是增加功能，而是减少理解成本。"*
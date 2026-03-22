"""
[utils_7-001] 格式化工具模块
提供数据格式化、展示相关的工具函数

核心职责:
- 格式化统计结果为文本
- 格式化统计结果为 DataFrame
- 格式化条件为可读文本

为什么这样设计:
将格式化逻辑从业务逻辑中分离，
便于复用和测试。
"""

import pandas as pd
from typing import Dict, Any, List, Optional


def format_stats_result_for_display(
    stats_result: Dict[str, Any],
    is_comparison: bool = False
) -> pd.DataFrame:
    """
    [utils_7-001-01] 格式化统计结果为 DataFrame
    将统计结果转换为用于展示的 DataFrame

    Args:
        stats_result: 统计结果字典
        is_comparison: 是否为对比模式

    Returns:
        pd.DataFrame: 格式化后的表格
    """
    if is_comparison:
        rows = []
        for r in stats_result.get("results", []):
            gap = r.get("gap")
            trend = r.get("trend", "")

            trend_symbol = ""
            if trend == "improved":
                trend_symbol = "↑"
            elif trend == "declined":
                trend_symbol = "↓"
            elif trend == "unchanged":
                trend_symbol = "→"

            rows.append({
                "指标名称": r.get("name", ""),
                "版本 A 分子": r.get("numerator_a", 0),
                "版本 A 分母": r.get("denominator_a", 0),
                "版本 A(%)": r.get("percentage_a"),
                "版本 B 分子": r.get("numerator_b", 0),
                "版本 B 分母": r.get("denominator_b", 0),
                "版本 B(%)": r.get("percentage_b"),
                "Gap(%)": gap,
                "趋势": trend_symbol
            })

        return pd.DataFrame(rows)

    # 普通模式
    rows = []
    for r in stats_result.get("results", []):
        pct = r.get("percentage")
        rows.append({
            "指标名称": r.get("name", ""),
            "分子": r.get("numerator", 0),
            "分母": r.get("denominator", 0),
            "百分比": f"{pct}%" if pct is not None else "N/A",
            "原始百分比": pct
        })

    return pd.DataFrame(rows)


def format_stats_for_prompt(
    stats_result: Dict[str, Any],
    is_comparison: bool = False,
    is_grouping: bool = False
) -> str:
    """
    [utils_7-001-02] 格式化统计结果为 Prompt 文本
    将统计结果格式化为 AI 报告生成用的文字

    Args:
        stats_result: 统计结果
        is_comparison: 是否为对比模式
        is_grouping: 是否为分组模式

    Returns:
        str: 格式化后的文字
    """
    # 从数据结构自动检测分组模式
    if stats_result.get("multi_group") or "groups" in stats_result:
        is_grouping = True

    # 多维度分组
    if is_grouping and stats_result.get("multi_group"):
        lines = []
        for gr in stats_result.get("group_results", []):
            lines.append(f"=== 分组字段：{gr.get('group_field', '-')} ===")
            lines.append(_format_single_grouping(gr))
            lines.append("")
        return "\n".join(lines)

    # 单维度分组
    if is_grouping and "groups" in stats_result:
        return _format_single_grouping(stats_result)

    lines = []

    if is_comparison:
        lines.append(f"对比字段：{stats_result.get('compare_field', '-')}")
        lines.append(f"版本 A ({stats_result.get('version_a', '-')}): 分母数 {stats_result.get('denominator_count_a', 0)} 条")
        lines.append(f"版本 B ({stats_result.get('version_b', '-')}): 分母数 {stats_result.get('denominator_count_b', 0)} 条")
        lines.append("")
        lines.append("各指标统计:")
    else:
        lines.append(f"公共分母：{stats_result.get('denominator_count', 0)} 条")
        if stats_result.get('denominator_description'):
            lines.append(f"分母说明：{stats_result['denominator_description']}")
        lines.append("")
        lines.append("各指标统计:")

    for r in stats_result.get("results", []):
        name = r.get("name", "-")

        if is_comparison:
            pct_a = r.get("percentage_a")
            pct_b = r.get("percentage_b")
            gap = r.get("gap")
            trend = r.get("trend", "")

            pct_a_str = f"{pct_a}%" if pct_a is not None else "N/A"
            pct_b_str = f"{pct_b}%" if pct_b is not None else "N/A"

            trend_text = ""
            if trend == "improved":
                trend_text = "（改善）"
            elif trend == "declined":
                trend_text = "（退化）"
            elif trend == "unchanged":
                trend_text = "（持平）"

            gap_str = f"{gap}%" if gap is not None else "N/A"

            lines.append(
                f"- {name}: 版本 A {pct_a_str} ({r.get('numerator_a', 0)}/{r.get('denominator_a', 0)}), "
                f"版本 B {pct_b_str} ({r.get('numerator_b', 0)}/{r.get('denominator_b', 0)}), "
                f"Gap: {gap_str} {trend_text}"
            )
        else:
            pct = r.get("percentage")
            pct_str = f"{pct}%" if pct is not None else "N/A"

            lines.append(
                f"- {name}: {pct_str} ({r.get('numerator', 0)}/{r.get('denominator', 0)})"
            )

    return "\n".join(lines)


def _format_single_grouping(stats_result: Dict[str, Any]) -> str:
    """
    [utils_7-001-03] 格式化单个分组维度的统计结果
    内部函数，处理单个分组维度的格式化
    """
    lines = []
    group_field = stats_result.get("group_field", "-")
    lines.append(f"分组字段：{group_field}")
    lines.append(f"分母描述：{stats_result.get('denominator_description', '未设置')}")
    lines.append("")

    groups = stats_result.get("groups", [])
    for r in stats_result.get("results", []):
        name = r.get("name", "-")
        lines.append(f"- {name}:")
        # 遍历每个分组值的数据
        for group_key, group_data in r.items():
            if group_key == "name":
                continue
            if isinstance(group_data, dict) and ("percentage" in group_data or "pct" in group_data):
                pct = group_data.get("percentage", group_data.get("pct"))
                num = group_data.get("numerator", group_data.get("num", 0))
                denom = group_data.get("denominator", group_data.get("denom", 0))
                pct_str = f"{pct}%" if pct is not None else "N/A"
                lines.append(f"  {group_key}: {pct_str} ({num}/{denom})")

    return "\n".join(lines)




def format_stats_result_for_grouping(
    stats_result: Dict[str, Any]
) -> "pd.DataFrame":
    """
    [utils_7-001-06] 格式化分组统计结果为 DataFrame
    将分组统计结果转换为用于展示的 DataFrame

    Args:
        stats_result: 分组统计结果字典

    Returns:
        pd.DataFrame: 格式化后的分组表格
    """
    import pandas as pd

    groups = stats_result.get("groups", [])
    results = stats_result.get("results", [])

    if not groups or not results:
        return pd.DataFrame()

    rows = []
    for r in results:
        name = r.get("name", "")
        row: Dict[str, Any] = {"指标名称": name}
        for g in groups:
            group_data = r.get(g, {})
            if isinstance(group_data, dict):
                pct = group_data.get("percentage")
                num = group_data.get("numerator", 0)
                denom = group_data.get("denominator", 0)
                row[g] = f"{num}/{denom} ({pct}%)" if pct is not None else f"N/A (0/0)"
            else:
                row[g] = str(group_data) if group_data else "N/A"
        rows.append(row)

    return pd.DataFrame(rows)

def format_condition_as_text(condition: Dict[str, str]) -> str:
    """
    [utils_7-001-04] 格式化条件为可读文本
    将条件对象转换为人类可读的文本

    Args:
        condition: 条件字典 {"field": "", "op": "", "value": ""}

    Returns:
        str: 可读文本
    """
    field = condition.get("field", "")
    op = condition.get("op", "==")
    value = condition.get("value", "")

    op_text_map = {
        "==": "等于",
        "!=": "不等于",
        "contains": "包含",
        "not_contains": "不包含",
        "is_empty": "为空",
        "is_not_empty": "不为空",
        "in": "属于",
        "not_in": "不属于",
        "greater_than": "大于",
        "less_than": "小于"
    }

    op_text = op_text_map.get(op, op)

    if not value:
        return f"{field} {op_text}"
    return f"{field} {op_text} {value}"


def format_conditions_as_text(conditions: List[Dict[str, str]], logic: str = "and") -> str:
    """
    [utils_7-001-05] 格式化条件列表为可读文本
    将多个条件格式化为带逻辑关系的文本

    Args:
        conditions: 条件列表
        logic: 逻辑关系 ("and" 或 "or")

    Returns:
        str: 可读文本
    """
    if not conditions:
        return "无条件"

    logic_text = "且" if logic == "and" else "或"
    texts = [format_condition_as_text(c) for c in conditions]
    return logic_text.join(texts)

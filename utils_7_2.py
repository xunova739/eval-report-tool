"""
[utils_7-002] 验证器模块
提供口径配置验证、数据验证等功能

核心职责:
- 验证口径配置的有效性
- 验证字段映射的置信度
- 自动修复常见问题

为什么这样设计:
将验证逻辑集中化，便于复用和维护，
同时提供详细的错误报告。
"""

from typing import Dict, Any, List, Optional, Tuple


# ==================== 口径配置验证 ====================

def validate_metrics_config(config: Dict[str, Any], df_columns: List[str]) -> Tuple[bool, List[str]]:
    """
    [utils_7-002-01] 验证口径配置
    检查口径配置的有效性

    核心职责:
    - 验证字段名是否存在
    - 验证条件格式是否正确
    - 验证分母类型是否有效

    Args:
        config: 口径配置字典
        df_columns: DataFrame 的列名列表

    Returns:
        Tuple[bool, List[str]]: (是否有效，错误列表)
    """
    errors = []

    # 验证公共分母
    common_denom = config.get("common_denominator", {})
    for cond in common_denom.get("conditions", []):
        field = cond.get("field", "")
        if field and field not in df_columns:
            errors.append(f"公共分母条件中字段 '{field}' 不存在")

    # 验证每个指标
    for metric in config.get("metrics", []):
        metric_name = metric.get("name", "未命名指标")

        # 验证分子条件
        for cond in metric.get("numerator_conditions", []):
            field = cond.get("field", "")
            if field and field not in df_columns:
                errors.append(f"指标 '{metric_name}' 的分子条件中字段 '{field}' 不存在")

        # 验证 OR 条件组
        for group in metric.get("numerator_or_conditions", []):
            for cond in group:
                field = cond.get("field", "")
                if field and field not in df_columns:
                    errors.append(f"指标 '{metric_name}' 的 OR 条件中字段 '{field}' 不存在")

        # 验证自定义分母条件
        for cond in metric.get("custom_denominator_conditions", []):
            field = cond.get("field", "")
            if field and field not in df_columns:
                errors.append(f"指标 '{metric_name}' 的自定义分母条件中字段 '{field}' 不存在")

        # 验证 numerator_logic 与条件类型匹配
        has_or = bool(metric.get("numerator_or_conditions", []))
        logic = metric.get("numerator_logic", "and")
        if has_or and logic != "or":
            errors.append(f"指标 '{metric_name}' 使用了 OR 条件但 numerator_logic 为 '{logic}'，应为 'or'")

    return len(errors) == 0, errors


def validate_field_mappings(config: Dict[str, Any], threshold: int = 80) -> List[Dict[str, Any]]:
    """
    [utils_7-002-02] 检查字段映射置信度
    找出置信度低于阈值的映射

    Args:
        config: 口径配置字典
        threshold: 置信度阈值

    Returns:
        List[Dict]: 低置信度映射列表
    """
    low_confidence = []

    for mapping in config.get("field_mappings", []):
        confidence = mapping.get("confidence", 95)
        if confidence < threshold:
            low_confidence.append({
                "description": mapping.get("description", ""),
                "field": mapping.get("field", ""),
                "confidence": confidence
            })

    return low_confidence


def auto_fix_operators(config: Dict[str, Any], field_distribution: Dict[str, Any]) -> Dict[str, Any]:
    """
    [utils_7-002-03] 自动修正运算符
    根据字段类型自动修正运算符（如 multi_select 字段的 in → contains）

    核心职责:
    - 检测 categorical_with_multi 字段
    - 将 == 改为 contains
    - 将 != 改为 not_contains
    - 将 in/not_in 改为 contains/not_contains

    Args:
        config: 口径配置字典
        field_distribution: 字段分布信息

    Returns:
        Dict: 修正后的配置
    """
    def fix_condition(cond: Dict[str, str]) -> Dict[str, str]:
        field = cond.get("field", "")
        op = cond.get("op", "")
        info = field_distribution.get(field, {})

        if info.get("type") == "categorical_with_multi":
            if op in ("in", "=="):
                cond["op"] = "contains"
            elif op in ("not_in", "!="):
                cond["op"] = "not_contains"

        return cond

    # 修正公共分母
    for cond in config.get("common_denominator", {}).get("conditions", []):
        fix_condition(cond)

    # 修正每个指标
    for metric in config.get("metrics", []):
        for cond in metric.get("numerator_conditions", []):
            fix_condition(cond)
        for group in metric.get("numerator_or_conditions", []):
            for cond in group:
                fix_condition(cond)
        for cond in metric.get("custom_denominator_conditions", []):
            fix_condition(cond)

    return config


def auto_fix_values(
    config: Dict[str, Any],
    field_distribution: Dict[str, Any],
    min_cutoff: float = 0.7
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    [utils_7-002-04] 自动修正值
    根据字段分布模糊匹配修正条件值

    核心职责:
    - 检测条件值是否在有效值列表中
    - 使用模糊匹配找最接近的值
    - 记录修正日志

    Args:
        config: 口径配置字典
        field_distribution: 字段分布信息
        min_cutoff: 最小相似度阈值

    Returns:
        Tuple[Dict, List]: (修正后配置，修正日志)
    """
    import difflib

    fix_log = []

    def get_valid_values(info: Dict[str, Any]) -> List[str]:
        t = info.get("type", "")
        if t == "categorical":
            return info.get("values", [])
        elif t == "categorical_with_multi":
            return info.get("options", [])
        return []

    def fix_value(cond: Dict[str, str]) -> None:
        field = cond.get("field", "")
        op = cond.get("op", "")
        val = cond.get("value", "")

        if op in ("is_empty", "is_not_empty") or not val:
            return

        info = field_distribution.get(field, {})
        valid = get_valid_values(info)

        if not valid:
            return

        if op in ("in", "not_in"):
            parts = [v.strip() for v in val.split(",")]
            new_parts = []
            for p in parts:
                if p in valid:
                    new_parts.append(p)
                else:
                    match_cutoff = 0.85 if len(p) <= 4 else min_cutoff
                    match = difflib.get_close_matches(p, valid, n=1, cutoff=match_cutoff)
                    if match:
                        ratio = difflib.SequenceMatcher(None, p, match[0]).ratio()
                        fix_log.append({
                            "field": field,
                            "old": p,
                            "new": match[0],
                            "ratio": round(ratio * 100, 1)
                        })
                        new_parts.append(match[0])
                    else:
                        new_parts.append(p)
            cond["value"] = ",".join(new_parts)
        else:
            if val not in valid:
                match_cutoff = 0.85 if len(val) <= 4 else min_cutoff
                match = difflib.get_close_matches(val, valid, n=1, cutoff=match_cutoff)
                if match:
                    ratio = difflib.SequenceMatcher(None, val, match[0]).ratio()
                    fix_log.append({
                        "field": field,
                        "old": val,
                        "new": match[0],
                        "ratio": round(ratio * 100, 1)
                    })
                    cond["value"] = match[0]

    # 修正公共分母
    for cond in config.get("common_denominator", {}).get("conditions", []):
        fix_value(cond)

    # 修正每个指标
    for metric in config.get("metrics", []):
        for cond in metric.get("numerator_conditions", []):
            fix_value(cond)
        for group in metric.get("numerator_or_conditions", []):
            for cond in group:
                fix_value(cond)
        for cond in metric.get("custom_denominator_conditions", []):
            fix_value(cond)

    return config, fix_log

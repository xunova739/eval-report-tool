"""
[SVC-D-001] 数据服务模块
封装数据处理、筛选、统计等核心业务逻辑

核心职责:
- DataService: 提供数据清洗、筛选、统计计算服务
- 将原 data_processor.py 中的函数重构为类方法

为什么这样设计:
使用服务类封装业务逻辑，便于依赖注入、单元测试和复用
"""

import re
import pandas as pd
from typing import Tuple, Dict, Any, List, Optional
from dataclasses import dataclass

# 导入领域模型
from domain_1 import (
    Condition,
    Metric,
    MetricsConfig,
    MetricResult,
    StatsResult,
    OperatorType,
    FieldType,
    DenominatorType,
    NumeratorLogic,
    MetricStatus,
)


# ==================== 常量定义 ====================

# [SVC-D-001-01] 字段分布分析阈值配置
FIELD_DIST_THRESHOLD = 50  # 低基数/高基数分界
FIELD_DIST_HIGH_UNIQUE_RATIO = 0.8  # 高唯一率阈值（超过 80% 则为 skip）
FIELD_DIST_NAME_MATCH_RATIO = 0.7  # 人名匹配阈值
FIELD_DIST_NAME_PATTERN = re.compile(r'^[\u4e00-\u9fa5]{2,4}$')  # 中文人名模式（2-4 字符）


# ==================== 数据服务类 ====================

class DataService:
    """[SVC-D-001-10] 数据处理服务
    提供数据清洗、筛选、统计计算等核心功能

    核心职责:
    - 数据清洗：清理列名、删除空行、去重
    - 字段分析：构建字段分布信息，识别字段类型
    - 数据筛选：应用单条件和多条件筛选
    - 统计计算：计算指标达标率

    为什么这样设计:
    将数据相关操作封装在服务类中，提供统一的 API 接口，
    便于上层（如 Streamlit UI）调用和测试
    """

    def __init__(self, df: Optional[pd.DataFrame] = None):
        """
        初始化数据服务

        Args:
            df: 可选的初始 DataFrame
        """
        self.df = df
        self._field_distribution: Optional[Dict[str, Any]] = None

    def set_dataframe(self, df: pd.DataFrame) -> None:
        """[SVC-D-001-11] 设置数据框
        设置服务要处理的 DataFrame

        为什么这样设计:
        支持链式调用和复用服务实例
        """
        self.df = df
        self._field_distribution = None

    # ==================== 数据清洗服务 ====================

    def clean_dataframe(self) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        [SVC-D-001-20] 清洗 DataFrame
        执行数据清洗操作，返回清洗后的数据和清洗报告

        核心职责:
        - 清理列名空格
        - 删除全空行
        - 检测重复行
        - 统计空值

        为什么这样设计:
        数据清洗是分析的前提，返回清洗报告便于用户了解数据变化

        Returns:
            Tuple[pd.DataFrame, Dict]: 清洗后的 DataFrame 和清洗报告
        """
        if self.df is None:
            raise ValueError("未设置 DataFrame")

        report = {
            "original_rows": len(self.df),
            "original_columns": len(self.df.columns),
            "empty_rows_removed": 0,
            "duplicate_rows": 0,
            "column_null_counts": {},
            "columns_renamed": []
        }

        # 1. 清理列名（去除首尾空格）
        original_columns = self.df.columns.tolist()
        self.df.columns = [col.strip() if isinstance(col, str) else col for col in self.df.columns]

        # 记录被重命名的列
        renamed = []
        for old, new in zip(original_columns, self.df.columns):
            if old != new:
                renamed.append({"old": old, "new": new})
        report["columns_renamed"] = renamed

        # 2. 删除全空行（所有值都为 NaN 的行）
        empty_mask = self.df.isna().all(axis=1)
        empty_rows_count = empty_mask.sum()
        report["empty_rows_removed"] = int(empty_rows_count)
        self.df = self.df[~empty_mask].reset_index(drop=True)

        # 3. 检测完全重复行（不删除，仅统计）
        duplicate_count = self.df.duplicated().sum()
        report["duplicate_rows"] = int(duplicate_count)

        # 4. 统计每列的空值数量
        null_counts = self.df.isna().sum().to_dict()
        report["column_null_counts"] = {k: int(v) for k, v in null_counts.items()}

        return self.df, report

    # ==================== 字段分析服务 ====================

    def build_field_distribution(
        self,
        threshold: int = FIELD_DIST_THRESHOLD
    ) -> Dict[str, Any]:
        """
        [SVC-D-001-30] 构建字段分布信息
        分析 DataFrame 中每个字段的类型和值分布

        核心职责:
        - 识别字段类型（categorical/multi/high_cardinality/skip）
        - 过滤无意义字段（常量列、全唯一列、人名列）
        - 为 AI 解析提供背景上下文

        为什么这样设计:
        字段分布是 AI 解析口径的基础，帮助模型理解每个字段的语义和可用运算符

        分类规则:
        - skip: 常量列、全唯一列、高唯一率列、疑似人名列
        - categorical: 唯一值数 <= threshold，传全部值
        - categorical_with_multi: 含逗号/顿号的多选字段
        - high_cardinality: 唯一值数 > threshold 但未被跳过

        Args:
            threshold: 低基数阈值，默认 50

        Returns:
            Dict: 字段分布信息
        """
        if self.df is None:
            raise ValueError("未设置 DataFrame")

        total_rows = len(self.df)
        result: Dict[str, Any] = {}

        for col in self.df.columns:
            series = self.df[col].dropna()
            unique_count = series.nunique()

            # 常量列
            if unique_count <= 1:
                result[col] = {"type": "skip", "reason": "常量列"}
                continue

            # 全唯一列
            if unique_count == total_rows:
                result[col] = {"type": "skip", "reason": "全唯一列"}
                continue

            # 高唯一率列（>80%）
            if total_rows > 0 and unique_count / total_rows > FIELD_DIST_HIGH_UNIQUE_RATIO:
                result[col] = {"type": "skip", "reason": "高唯一率"}
                continue

            # 疑似人名列（取前 20 个样本，70% 以上符合中文 2-4 字符）
            samples = series.astype(str).head(20).tolist()
            name_matches = sum(1 for v in samples if FIELD_DIST_NAME_PATTERN.match(v))
            if len(samples) > 0 and name_matches / len(samples) > FIELD_DIST_NAME_MATCH_RATIO:
                result[col] = {"type": "skip", "reason": "疑似人名列"}
                continue

            # 低基数：评估标签列
            if unique_count <= threshold:
                str_series = series.astype(str)
                raw_values = str_series.tolist()

                # 检测是否为多选字段：JSON 数组格式或逗号/顿号分隔
                import json
                has_json_array = any(str(v).strip().startswith('[') for v in raw_values)
                sep_pattern = re.compile(r'[,，、]')
                has_sep = any(sep_pattern.search(v) for v in raw_values)

                if has_json_array or has_sep:
                    # 拆分后统计独立选项（优先 JSON 解析）
                    all_options = []
                    for v in raw_values:
                        v_str = str(v).strip()

                        # 优先尝试 JSON 数组解析
                        if v_str.startswith('[') and v_str.endswith(']'):
                            try:
                                parsed = json.loads(v_str)
                                if isinstance(parsed, list):
                                    all_options.extend([str(p).strip() for p in parsed if p])
                                    continue
                            except (json.JSONDecodeError, ValueError):
                                pass  # 降级

                            # 二级降级：正则提取引号内的字符串
                            # 处理 ["值A"+,"值B"] 或 ["值A"+"值B"] 等非标准格式
                            quoted = re.findall(r'"([^"]+)"', v_str)
                            if quoted:
                                all_options.extend([q.strip() for q in quoted if q.strip()])
                                continue

                        # 降级：逗号/顿号拆分
                        parts = sep_pattern.split(v_str)
                        all_options.extend([p.strip() for p in parts if p.strip()])

                    option_counts = {}
                    for opt in all_options:
                        option_counts[opt] = option_counts.get(opt, 0) + 1

                    # 记录子类型：json_array 或 comma_separated
                    # json_array 字段每个单元格是 ["选项A","选项B"] 格式
                    # comma_separated 字段每个单元格是 "选项A，选项B" 格式
                    subtype = "json_array" if has_json_array else "comma_separated"
                    result[col] = {
                        "type": "categorical_with_multi",
                        "subtype": subtype,
                        "options": sorted(option_counts.keys()),
                        "option_counts": option_counts,
                        "note": "该字段含多选值，匹配时请用 contains"
                    }
                else:
                    values = sorted(str_series.unique().tolist())
                    result[col] = {"type": "categorical", "values": values}
            else:
                # 高基数但未被跳过
                result[col] = {
                    "type": "high_cardinality",
                    "unique_count": int(unique_count),
                    "samples": series.astype(str).head(3).tolist()
                }

        self._field_distribution = result
        return result

    def get_field_distribution(self) -> Optional[Dict[str, Any]]:
        """[SVC-D-001-31] 获取已构建的字段分布
        如果尚未构建，返回 None
        """
        return self._field_distribution

    # ==================== 条件应用服务 ====================

    def apply_condition(
        self,
        df: pd.DataFrame,
        condition: Condition
    ) -> pd.Series:
        """
        [SVC-D-001-40] 应用单个条件
        根据条件筛选 DataFrame，返回布尔 Series

        核心职责:
        - 支持多列字段（用"/"分隔）的 OR 匹配
        - 支持所有运算符（==, !=, contains, in 等）

        为什么这样设计:
        将条件应用逻辑封装为独立方法，便于复用和测试

        Args:
            df: DataFrame
            condition: 条件对象

        Returns:
            pd.Series: 布尔 Series，True 表示满足条件
        """
        if isinstance(condition, dict):
            field = condition.get("field", "")
            op = condition.get("op", "==")
            value = condition.get("value", "")
        else:
            field = condition.field
            op = condition.op
            value = condition.value

        # 支持多列字段（用"/"分隔），任一列匹配即为 True（OR 逻辑）
        if "/" in field and field not in df.columns:
            sub_fields = [f.strip() for f in field.split("/")]
            valid_fields = [f for f in sub_fields if f in df.columns]
            if not valid_fields:
                return pd.Series([False] * len(df), index=df.index)
            combined_mask = pd.Series([False] * len(df), index=df.index)
            for sf in valid_fields:
                sub_cond = Condition(field=sf, op=op, value=value)
                combined_mask = combined_mask | self.apply_condition(df, sub_cond)
            return combined_mask

        if field not in df.columns:
            return pd.Series([False] * len(df), index=df.index)

        col = df[field]

        if op == "==":
            if value == "":
                mask = col.isna() | (col.astype(str).str.strip() == "")
            else:
                mask = col.astype(str) == str(value)

        elif op == "!=":
            if value == "":
                mask = col.notna() & (col.astype(str).str.strip() != "")
            else:
                mask = col.astype(str) != str(value)

        elif op == "contains":
            mask = col.astype(str).str.contains(str(value), case=False, na=False, regex=False)

        elif op == "not_contains":
            mask = ~col.astype(str).str.contains(str(value), case=False, na=False, regex=False)

        elif op == "is_empty":
            mask = col.isna() | (col.astype(str).str.strip() == "")

        elif op == "is_not_empty":
            mask = col.notna() & (col.astype(str).str.strip() != "")

        elif op == "in":
            values = [v.strip() for v in str(value).split(",")]
            str_col = col.astype(str)
            # 格子里只要包含其中一个值就算（OR 逻辑）
            # 等价于 Excel 里勾选多个筛选条件的行为
            mask = pd.Series([False] * len(df), index=df.index)
            for v in values:
                mask = mask | str_col.str.contains(v, case=False, na=False, regex=False)

        elif op == "not_in":
            values = [v.strip() for v in str(value).split(",")]
            str_col = col.astype(str)
            # 格子里不能包含其中任何一个值
            mask = pd.Series([True] * len(df), index=df.index)
            for v in values:
                mask = mask & ~str_col.str.contains(v, case=False, na=False, regex=False)

        elif op == "greater_than":
            try:
                mask = pd.to_numeric(col, errors='coerce') > float(value)
            except (ValueError, TypeError):
                mask = pd.Series([False] * len(df), index=df.index)

        elif op == "less_than":
            try:
                mask = pd.to_numeric(col, errors='coerce') < float(value)
            except (ValueError, TypeError):
                mask = pd.Series([False] * len(df), index=df.index)

        else:
            mask = pd.Series([True] * len(df), index=df.index)

        mask = mask.fillna(False)
        return mask

    def apply_conditions(
        self,
        conditions: List[Condition],
        df: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        [SVC-D-001-41] 应用多个条件（AND 逻辑）
        筛选 DataFrame，所有条件必须同时满足

        支持条件类型：
        1. 普通条件：{"field":"xxx","op":"==","value":"yyy"}
        2. OR组条件：{"type":"or_group","conditions":[条件1, 条件2, ...]}  # 组内OR

        Args:
            conditions: 条件列表
            df: 可选的 DataFrame，默认使用 self.df

        Returns:
            pd.DataFrame: 筛选后的 DataFrame
        """
        df = df if df is not None else self.df
        if df is None:
            raise ValueError("未设置 DataFrame，请先调用 set_dataframe 或在初始化时传入 df")

        if not conditions:
            return df

        mask = pd.Series([True] * len(df), index=df.index)

        for condition in conditions:
            # 检测是否为 OR 组条件
            if isinstance(condition, dict) and condition.get("type") == "or_group":
                # OR 组：组内条件之间是 OR 关系
                or_conditions = condition.get("conditions", [])
                or_mask = pd.Series([False] * len(df), index=df.index)
                for cond in or_conditions:
                    cond_mask = self.apply_condition(df, cond)
                    or_mask = or_mask | cond_mask  # 组内 OR
                mask = mask & or_mask  # 和主条件 AND
            else:
                # 普通条件：直接 AND
                cond_mask = self.apply_condition(df, condition)
                mask = mask & cond_mask

        return df[mask].reset_index(drop=True)

    def apply_conditions_or(
        self,
        or_condition_groups: List[List[Condition]],
        df: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        [SVC-D-001-42] 应用多组条件（组间 OR，组内 AND）

        Args:
            or_condition_groups: 条件组列表，每组内部 AND，组间 OR
            df: 可选的 DataFrame，默认使用 self.df

        Returns:
            pd.DataFrame: 筛选后的 DataFrame
        """
        df = df if df is not None else self.df
        if df is None:
            raise ValueError("未设置 DataFrame，请先调用 set_dataframe 或在初始化时传入 df")

        if not or_condition_groups:
            return df

        or_mask = pd.Series([False] * len(df), index=df.index)

        for group in or_condition_groups:
            group_mask = pd.Series([True] * len(df), index=df.index)
            for condition in group:
                group_mask = group_mask & self.apply_condition(df, condition)
            or_mask = or_mask | group_mask

        return df[or_mask].reset_index(drop=True)

    # ==================== Case 筛选服务 ====================

    def filter_cases(
        self,
        conditions: List[Condition]
    ) -> pd.DataFrame:
        """
        [SVC-D-001-50] Case 筛选
        对当前数据应用多个条件（AND 逻辑）

        Args:
            conditions: 条件列表

        Returns:
            pd.DataFrame: 筛选后的 DataFrame
        """
        if self.df is None or self.df.empty:
            return pd.DataFrame()

        if not conditions:
            return self.df.copy()

        return self.apply_conditions(conditions)

    def get_column_unique_values(self, column: str) -> List[str]:
        """获取某列的唯一值列表（排序后）"""
        if self.df is None or column not in self.df.columns:
            return []
        return sorted(self.df[column].dropna().astype(str).unique().tolist())

    # ==================== 统计计算服务 ====================

    def calculate_metrics(
        self,
        metrics_config: MetricsConfig
    ) -> StatsResult:
        """
        [SVC-D-001-60] 计算统计指标
        根据口径配置计算各指标的达标率

        核心职责:
        - 应用公共分母条件
        - 计算每个指标的分子分母
        - 处理自定义分母场景

        Args:
            metrics_config: 口径配置

        Returns:
            StatsResult: 统计结果
        """
        if self.df is None or self.df.empty:
            return StatsResult()

        result = StatsResult()

        # 1. 确定分母数据集
        common_denom = metrics_config.common_denominator
        result.denominator_description = common_denom.description

        if common_denom.type == "ai":
            if common_denom.ai_analyzed_conditions:
                df_denom = self.apply_conditions(common_denom.ai_analyzed_conditions)
            else:
                df_denom = self.df
        elif common_denom.is_all_data():
            df_denom = self.df
        else:
            df_denom = self.apply_conditions(common_denom.conditions)

        denominator_count = len(df_denom)
        result.denominator_count = denominator_count

        # 2. 计算每个指标
        for metric in metrics_config.metrics:
            metric_result = self._calculate_single_metric(
                df_denom=df_denom,
                metric=metric,
                denominator_count=denominator_count,
                ai_analyzed_conditions=common_denom.ai_analyzed_conditions,
                condition_groups=common_denom.condition_groups
            )
            result.results.append(metric_result)

        return result

    def _calculate_single_metric(
        self,
        df_denom: pd.DataFrame,
        metric: Metric,
        denominator_count: int,
        ai_analyzed_conditions: Optional[List[Condition]] = None,
        condition_groups: Optional[List[Any]] = None
    ) -> MetricResult:
        """
        [SVC-D-001-61] 计算单个指标
        内部方法，计算指定分子的达标率

        Args:
            df_denom: 分母数据集
            metric: 指标定义
            denominator_count: 分母数量
            ai_analyzed_conditions: AI分析的分母条件

        Returns:
            MetricResult: 指标结果
        """
        # 确定该指标的分母
        if metric.has_custom_denominator():
            # 获取自定义分母来源
            custom_source = getattr(metric, 'custom_denominator_source', 'custom')

            if custom_source == "ai":
                # 使用AI分析的分母
                if ai_analyzed_conditions:
                    df_metric_denom = self.apply_conditions(ai_analyzed_conditions, df=self.df)
                else:
                    df_metric_denom = self.df
                metric_denom_count = len(df_metric_denom)
            elif custom_source == "all":
                # 使用全部数据
                df_metric_denom = self.df
                metric_denom_count = len(df_metric_denom)
            elif custom_source == "group":
                # 使用公共分母某个条件组
                group_name = getattr(metric, 'custom_denominator_group', '')
                group_conds: List[Condition] = []
                if condition_groups:
                    for g in condition_groups:
                        g_name = g.get("name", "") if isinstance(g, dict) else getattr(g, "name", "")
                        if g_name == group_name:
                            g_conds = g.get("conditions", []) if isinstance(g, dict) else getattr(g, "conditions", [])
                            group_conds = g_conds
                            break
                if group_conds:
                    df_metric_denom = self.apply_conditions(group_conds, df=self.df)
                else:
                    df_metric_denom = self.df
                metric_denom_count = len(df_metric_denom)
            else:
                # 手动配置的条件
                df_metric_denom = self.apply_conditions(
                    metric.custom_denominator_conditions,
                    df=df_denom
                )
                metric_denom_count = len(df_metric_denom)
        else:
            df_metric_denom = df_denom
            metric_denom_count = denominator_count

        # 应用分子条件
        if metric.numerator_logic == "or":
            if metric.numerator_or_conditions:
                # AI 解析的 OR 结构：每组内部 AND，组间 OR
                df_numer = self.apply_conditions_or(metric.numerator_or_conditions, df=df_metric_denom)
                if metric.numerator_conditions:
                    df_numer = self.apply_conditions(metric.numerator_conditions, df=df_numer)
            elif metric.numerator_conditions:
                # 手动编辑 OR 模式：条件列表中任一满足即计入
                auto_or_groups = [[c] for c in metric.numerator_conditions]
                df_numer = self.apply_conditions_or(auto_or_groups, df=df_metric_denom)
            else:
                df_numer = df_metric_denom
        else:
            # AND 模式：所有条件同时满足
            df_numer = self.apply_conditions(
                metric.numerator_conditions,
                df=df_metric_denom
            )

        numerator_count = len(df_numer)

        # 计算百分比
        if metric_denom_count == 0:
            percentage = None
            status = MetricStatus.DENOMINATOR_ZERO.value
        else:
            percentage = round(numerator_count / metric_denom_count * 100, 2)
            status = MetricStatus.OK.value

        return MetricResult(
            name=metric.name,
            numerator=numerator_count,
            denominator=metric_denom_count,
            percentage=percentage,
            status=status
        )

    def _apply_numerator_or(
        self,
        df: pd.DataFrame,
        and_conditions: List[Condition],
        or_groups: List[List[Condition]]
    ) -> pd.DataFrame:
        """
        [SVC-D-001-62] 应用分子 OR 条件
        处理 AND 条件和 OR 条件组的组合逻辑

        逻辑：(AND 条件) OR (所有 OR 条件组)
        """
        # 先计算 OR 条件组
        if or_groups:
            or_mask = pd.Series([False] * len(df), index=df.index)
            for group in or_groups:
                group_mask = pd.Series([True] * len(df), index=df.index)
                for condition in group:
                    group_mask = group_mask & self.apply_condition(df, condition)
                or_mask = or_mask | group_mask
            df_or = df[or_mask].reset_index(drop=True)
        else:
            df_or = df

        # 再应用 AND 条件
        if and_conditions:
            return self.apply_conditions(and_conditions, df=df_or)

        return df_or

    def calculate_metrics_with_comparison(
        self,
        metrics_config: MetricsConfig,
        compare_field: str,
        version_a: str,
        version_b: str
    ) -> StatsResult:
        """
        [SVC-D-001-70] 版本对比模式统计
        按对比字段拆分数据，分别计算两组的统计指标

        Args:
            metrics_config: 口径配置
            compare_field: 对比字段名
            version_a: 版本 A 的值
            version_b: 版本 B 的值

        Returns:
            StatsResult: 对比统计结果
        """
        if self.df is None or self.df.empty:
            return StatsResult()

        if compare_field not in self.df.columns:
            return StatsResult()

        result = StatsResult()
        result.compare_field = compare_field
        result.version_a = version_a
        result.version_b = version_b

        # 拆分数据
        df_a = self.df[
            self.df[compare_field].astype(str) == str(version_a)
        ].reset_index(drop=True)
        df_b = self.df[
            self.df[compare_field].astype(str) == str(version_b)
        ].reset_index(drop=True)

        # 分别计算
        stats_a = self.set_dataframe_and_calculate(df_a, metrics_config)
        stats_b = self.set_dataframe_and_calculate(df_b, metrics_config)

        result.denominator_count_a = stats_a.denominator_count
        result.denominator_count_b = stats_b.denominator_count
        result.denominator_description = stats_a.denominator_description

        # 合并结果
        results_a = {r.name: r for r in stats_a.results}
        results_b = {r.name: r for r in stats_b.results}

        all_metric_names = set(results_a.keys()) | set(results_b.keys())

        for name in all_metric_names:
            r_a = results_a.get(name, MetricResult(name=name, status="missing"))
            r_b = results_b.get(name, MetricResult(name=name, status="missing"))

            pct_a = r_a.percentage
            pct_b = r_b.percentage

            if pct_a is not None and pct_b is not None:
                gap = round(pct_b - pct_a, 2)
                if gap > 0:
                    trend = "improved"
                elif gap < 0:
                    trend = "declined"
                else:
                    trend = "unchanged"
            else:
                gap = None
                trend = "unknown"

            combined = MetricResult(
                name=name,
                numerator=r_a.numerator,
                denominator=r_a.denominator,
                percentage=pct_a,
                status=r_a.status
            )
            # 扩展属性（通过额外字典传递）
            result.results.append(combined)

        return result

    def set_dataframe_and_calculate(
        self,
        df: pd.DataFrame,
        metrics_config: MetricsConfig
    ) -> StatsResult:
        """[SVC-D-001-71] 设置数据并计算
        便捷方法，设置 DataFrame 后立即计算

        Args:
            df: DataFrame
            metrics_config: 口径配置

        Returns:
            StatsResult: 统计结果
        """
        self.set_dataframe(df)
        return self.calculate_metrics(metrics_config)
    def calculate_metrics_with_grouping(
        self,
        metrics_config: MetricsConfig,
        group_field: str
    ) -> StatsResult:
        """
        [SVC-D-001-72] 分组统计模式
        按分组字段拆分数据，分别计算各组的统计指标

        Args:
            metrics_config: 口径配置
            group_field: 分组字段名

        Returns:
            StatsResult: 分组统计结果
        """
        if self.df is None or self.df.empty:
            return StatsResult()

        if group_field not in self.df.columns:
            return StatsResult()

        result = StatsResult()
        result.group_field = group_field

        # 保存原始数据，避免 set_dataframe_and_calculate 覆盖 self.df
        original_df = self.df

        # 获取所有分组值，添加"全���"作为总计组
        group_values = ["全部"] + list(original_df[group_field].dropna().unique())
        result.groups = group_values

        # 对每个分组计算统计指标
        group_results = {}
        for group_value in group_values:
            if group_value == "全部":
                df_group = original_df
            else:
                df_group = original_df[
                    original_df[group_field].astype(str).str.contains(str(group_value), regex=False, na=False)
                ].reset_index(drop=True)

            # 计算该分组的统计指标
            group_stats = self.set_dataframe_and_calculate(df_group, metrics_config)
            group_results[group_value] = group_stats

        # 合并结果
        result.group_results = group_results
        result.denominator_description = metrics_config.common_denominator.description

        return result


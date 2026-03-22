"""
[DOM-001] 领域模型模块
定义系统的核心数据模型，用于口径配置、统计结果等场景

核心职责:
- Condition: 标注筛选条件
- Metric: 统计指标定义
- MetricsConfig: 完整口径配置
- MetricResult: 统计结果

为什么这样设计:
使用 dataclass 提供类型安全的领域模型，替代裸字典传递，
提高代码可读性、可维护性和 IDE 支持。
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


# ==================== 枚举类型 ====================

class OperatorType(str, Enum):
    """[DOM-001-01] 运算符类型枚举
    定义所有可用的筛选运算符

    为什么这样设计:
    使用枚举替代字符串字面量，提供编译时检查和 IDE 自动补全
    """
    EQ = "=="
    NEQ = "!="
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"
    IN = "in"
    NOT_IN = "not_in"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"


class FieldType(str, Enum):
    """[DOM-001-02] 字段类型枚举
    定义字段分析后的类型分类

    为什么这样设计:
    字段类型决定可用运算符，使用枚举确保类型值的有效性
    """
    CATEGORICAL = "categorical"
    CATEGORICAL_WITH_MULTI = "categorical_with_multi"
    HIGH_CARDINALITY = "high_cardinality"
    SKIP = "skip"


class DenominatorType(str, Enum):
    """[DOM-001-03] 分母类型枚举
    定义指标分母的计算方式

    为什么这样设计:
    区分公共分母和自定义分母，决定统计计算逻辑
    """
    COMMON = "common"
    CUSTOM = "custom"


class NumeratorLogic(str, Enum):
    """[DOM-001-04] 分子逻辑类型枚举
    定义分子条件的组合方式

    为什么这样设计:
    AND 逻辑表示所有条件同时满足，OR 逻辑表示满足任一条件即可
    """
    AND = "and"
    OR = "or"


class MetricStatus(str, Enum):
    """[DOM-001-05] 指标状态枚举
    定义统计结果的状态

    为什么这样设计:
    标记指标计算是否成功，便于前端展示和错误处理
    """
    OK = "ok"
    DENOMINATOR_ZERO = "denominator_zero"
    MISSING = "missing"


# ==================== 核心领域模型 ====================

@dataclass
class Condition:
    """[DOM-001-10] 条件数据类
    标注筛选条件 - 对应数据过滤的最小单元

    核心职责:
    - 封装单个筛选条件的完整信息
    - 提供字典转换方法用于序列化

    为什么这样设计:
    条件是所有筛选和统计的基础，使用 dataclass 提供类型安全和默认值
    """
    field: str = ""
    op: str = OperatorType.EQ.value
    value: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "field": self.field,
            "op": self.op,
            "value": self.value
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Condition":
        """从字典创建"""
        return cls(
            field=data.get("field", ""),
            op=data.get("op", OperatorType.EQ.value),
            value=data.get("value", "")
        )

    def is_empty_condition(self) -> bool:
        """判断是否为空条件（未设置）"""
        return not self.field and not self.value

    def is_multi_select_field(self, field_distribution: Dict[str, Any]) -> bool:
        """判断是否为多选字段"""
        field_info = field_distribution.get(self.field, {})
        return field_info.get("type") == FieldType.CATEGORICAL_WITH_MULTI.value


@dataclass
class ConditionGroup:
    """[DOM-001-10b] 条件组 - 公共分母的命名条件集合"""
    name: str = ""
    conditions: List[Condition] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "conditions": [c.to_dict() for c in self.conditions]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConditionGroup":
        conds = [Condition.from_dict(c) if isinstance(c, dict) else c for c in data.get("conditions", [])]
        return cls(name=data.get("name", ""), conditions=conds)


@dataclass
class CommonDenominator:
    """[DOM-001-11] 公共分母数据类
    定义所有指标共享的分母条件

    核心职责:
    - 封装分母的描述和筛选条件
    - 区分全部数据 (type=all)、AI 分析的条件 (type=ai)、手动配置 (type=custom)
    - 支持多条件组，指标可选择不同的组

    为什么这样设计:
    公共分母是口径配置的核心部分，独立建模便于复用和验证
    """
    description: str = ""
    type: str = "all"
    conditions: List[Condition] = field(default_factory=list)
    ai_analyzed_conditions: List[Condition] = field(default_factory=list)
    condition_groups: List[ConditionGroup] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "description": self.description,
            "type": self.type,
            "conditions": [c.to_dict() for c in self.conditions],
            "ai_analyzed_conditions": [c.to_dict() for c in self.ai_analyzed_conditions],
            "condition_groups": [g.to_dict() for g in self.condition_groups]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CommonDenominator":
        """从字典创建"""
        conditions_data = data.get("conditions", [])
        ai_conditions_data = data.get("ai_analyzed_conditions", [])
        groups_data = data.get("condition_groups", [])
        conditions = [Condition.from_dict(c) if isinstance(c, dict) else c for c in conditions_data] if conditions_data else []
        ai_conditions = [Condition.from_dict(c) if isinstance(c, dict) else c for c in ai_conditions_data] if ai_conditions_data else []
        groups = [ConditionGroup.from_dict(g) if isinstance(g, dict) else g for g in groups_data]
        return cls(
            description=data.get("description", ""),
            type=data.get("type", "all"),
            conditions=conditions,
            ai_analyzed_conditions=ai_conditions,
            condition_groups=groups
        )

    def is_all_data(self) -> bool:
        """判断是否为全部数据（无过滤条件）"""
        return self.type == "all" or (self.type not in ("custom", "ai") and not self.conditions)


@dataclass
class FieldMapping:
    """[DOM-001-12] 字段映射数据类
    记录口径描述到实际字段的映射关系

    核心职责:
    - 保存 AI 解析时的映射置信度
    - 用于后续人工校验和修正

    为什么这样设计:
    AI 解析可能不完全准确，记录置信度便于人工审核
    """
    description: str = ""
    field: str = ""
    operator: str = ""
    value: str = ""
    confidence: int = 95

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "description": self.description,
            "field": self.field,
            "operator": self.operator,
            "value": self.value,
            "confidence": self.confidence
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FieldMapping":
        """从字典创建"""
        return cls(
            description=data.get("description", ""),
            field=data.get("field", ""),
            operator=data.get("operator", ""),
            value=data.get("value", ""),
            confidence=data.get("confidence", 95)
        )

    def needs_review(self) -> bool:
        """判断是否需要人工审核（置信度低于 80）"""
        return self.confidence < 80


@dataclass
class GroupDimension:
    """[DOM-001-13] 分组维度数据类
    定义统计结果的分组方式

    核心职责:
    - 封装分组字段和对应的值
    - 用于分组统计模式

    为什么这样设计:
    分组统计需要明确分组字段和每个组的值，独立建模便于扩展
    """
    group_field: str = ""
    values: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "field": self.group_field,
            "values": self.values
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GroupDimension":
        """从字典创建"""
        return cls(
            group_field=data.get("field", ""),
            values=data.get("values", [])
        )


@dataclass
class Metric:
    """[DOM-001-14] 指标数据类
    统计指标定义 - 封装分子分母逻辑

    核心职责:
    - 定义单个指标的完整计算逻辑
    - 支持 AND/OR 条件组合
    - 支持自定义分母

    为什么这样设计:
    指标是统计计算的核心，需要精确表达分子分母的计算规则
    """
    name: str = ""
    numerator_conditions: List[Condition] = field(default_factory=list)
    numerator_or_conditions: List[List[Condition]] = field(default_factory=list)
    numerator_logic: str = NumeratorLogic.AND.value
    denominator_type: str = DenominatorType.COMMON.value
    custom_denominator_conditions: List[Condition] = field(default_factory=list)
    custom_denominator_source: str = "ai"  # "ai" | "all" | "group" | "custom"
    custom_denominator_group: str = ""  # 当 source="group" 时，选中的组名

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "name": self.name,
            "numerator_conditions": [c.to_dict() for c in self.numerator_conditions],
            "numerator_or_conditions": [
                [c.to_dict() for c in group] for group in self.numerator_or_conditions
            ],
            "numerator_logic": self.numerator_logic,
            "denominator_type": self.denominator_type,
            "custom_denominator_conditions": [
                c.to_dict() for c in self.custom_denominator_conditions
            ],
            "custom_denominator_source": self.custom_denominator_source,
            "custom_denominator_group": self.custom_denominator_group
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Metric":
        """从字典创建"""
        numer_conds = data.get("numerator_conditions", [])
        numer_or_groups = data.get("numerator_or_conditions", [])
        custom_denom = data.get("custom_denominator_conditions", [])

        return cls(
            name=data.get("name", ""),
            numerator_conditions=[Condition.from_dict(c) for c in numer_conds],
            numerator_or_conditions=[
                [Condition.from_dict(c) for c in group] for group in numer_or_groups
            ],
            numerator_logic=data.get("numerator_logic", NumeratorLogic.AND.value),
            denominator_type=data.get("denominator_type", DenominatorType.COMMON.value),
            custom_denominator_conditions=[Condition.from_dict(c) for c in custom_denom],
            custom_denominator_source=data.get("custom_denominator_source", "ai"),
            custom_denominator_group=data.get("custom_denominator_group", "")
        )

    def has_or_conditions(self) -> bool:
        """判断是否包含 OR 条件"""
        return bool(self.numerator_or_conditions)

    def has_custom_denominator(self) -> bool:
        """判断是否有自定义分母"""
        return self.denominator_type == DenominatorType.CUSTOM.value

    def get_all_conditions(self) -> List[Condition]:
        """获取所有条件（展平 OR 条件组）"""
        all_conditions = list(self.numerator_conditions)
        for group in self.numerator_or_conditions:
            all_conditions.extend(group)
        all_conditions.extend(self.custom_denominator_conditions)
        return all_conditions


@dataclass
class MetricResult:
    """[DOM-001-15] 指标结果数据类
    单个指标的统计结果

    核心职责:
    - 封装分子、分母、百分比计算结果
    - 标记计算状态（成功/分母为零）

    为什么这样设计:
    统计结果是系统的主要输出，需要精确表达每个指标的计算结果
    """
    name: str = ""
    numerator: int = 0
    denominator: int = 0
    percentage: Optional[float] = None
    status: str = MetricStatus.OK.value

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "name": self.name,
            "numerator": self.numerator,
            "denominator": self.denominator,
            "percentage": self.percentage,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MetricResult":
        """从字典创建"""
        return cls(
            name=data.get("name", ""),
            numerator=data.get("numerator", 0),
            denominator=data.get("denominator", 0),
            percentage=data.get("percentage"),
            status=data.get("status", MetricStatus.OK.value)
        )

    def is_valid(self) -> bool:
        """判断结果是否有效"""
        return self.status == MetricStatus.OK.value


@dataclass
class MetricsConfig:
    """[DOM-001-16] 口径配置数据类
    完整统计口径配置 - 系统的核心配置对象

    核心职责:
    - 封装公共分母、指标列表、字段映射、分组维度
    - 提供字典转换方法用于 AI 解析和持久化

    为什么这样设计:
    口径配置是连接 AI 解析和统计计算的桥梁，需要完整的类型定义
    """
    common_denominator: CommonDenominator = field(default_factory=CommonDenominator)
    metrics: List[Metric] = field(default_factory=list)
    field_mappings: List[FieldMapping] = field(default_factory=list)
    group_dimensions: List[GroupDimension] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "common_denominator": self.common_denominator.to_dict(),
            "metrics": [m.to_dict() for m in self.metrics],
            "field_mappings": [fm.to_dict() for fm in self.field_mappings],
            "group_dimensions": [gd.to_dict() for gd in self.group_dimensions]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MetricsConfig":
        """从字典创建"""
        common_denom_data = data.get("common_denominator", {})
        metrics_data = data.get("metrics", [])
        field_mappings_data = data.get("field_mappings", [])
        group_dims_data = data.get("group_dimensions", [])

        return cls(
            common_denominator=CommonDenominator.from_dict(common_denom_data),
            metrics=[Metric.from_dict(m) for m in metrics_data],
            field_mappings=[FieldMapping.from_dict(fm) for fm in field_mappings_data],
            group_dimensions=[GroupDimension.from_dict(gd) for gd in group_dims_data]
        )

    def get_metric_names(self) -> List[str]:
        """获取所有指标名称"""
        return [m.name for m in self.metrics]

    def get_metric_by_name(self, name: str) -> Optional[Metric]:
        """根据名称获取指标"""
        for m in self.metrics:
            if m.name == name:
                return m
        return None

    def has_low_confidence_mappings(self, threshold: int = 80) -> bool:
        """判断是否有低置信度的字段映射"""
        return any(fm.needs_review() for fm in self.field_mappings)

    def get_low_confidence_mappings(self, threshold: int = 80) -> List[FieldMapping]:
        """获取低置信度的字段映射列表"""
        return [fm for fm in self.field_mappings if fm.needs_review()]


# ==================== 统计结果容器 ====================

@dataclass
class StatsResult:
    """[DOM-001-17] 统计结果数据类
    完整统计计算结果的容器

    核心职责:
    - 封装分母信息和各指标结果
    - 支持普通模式、对比模式、分组模式

    为什么这样设计:
    统计结果是系统的最终输出，需要统一的容器承载
    """
    denominator_count: int = 0
    denominator_description: str = ""
    results: List[MetricResult] = field(default_factory=list)
    # 对比模式专用字段
    compare_field: Optional[str] = None
    version_a: Optional[str] = None
    version_b: Optional[str] = None
    denominator_count_a: int = 0
    denominator_count_b: int = 0
    # 分组模式专用字段
    group_field: Optional[str] = None
    groups: List[str] = field(default_factory=list)
    denominator_counts: Dict[str, int] = field(default_factory=dict)
    group_results: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        base = {
            "denominator_count": self.denominator_count,
            "denominator_description": self.denominator_description,
            "results": [r.to_dict() for r in self.results]
        }
        if self.compare_field:
            base.update({
                "compare_field": self.compare_field,
                "version_a": self.version_a,
                "version_b": self.version_b,
                "denominator_count_a": self.denominator_count_a,
                "denominator_count_b": self.denominator_count_b
            })
        if self.group_field:
            base.update({
                "group_field": self.group_field,
                "groups": self.groups,
                "denominator_counts": self.denominator_counts
            })
        return base

    def is_comparison_mode(self) -> bool:
        """判断是否为对比模式"""
        return self.compare_field is not None

    def is_grouping_mode(self) -> bool:
        """判断是否为分组模式"""
        return self.group_field is not None

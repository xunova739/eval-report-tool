"""
领域模型层公共接口
"""

from .models import (
    # 枚举类型
    OperatorType,
    FieldType,
    DenominatorType,
    NumeratorLogic,
    MetricStatus,
    # 核心模型
    Condition,
    CommonDenominator,
    FieldMapping,
    GroupDimension,
    Metric,
    MetricResult,
    MetricsConfig,
    StatsResult,
)
from .exceptions import (
    DomainException,
    ValidationError,
    ConfigLoadError,
    DataServiceError,
    DataFilterError,
    ExportError,
)

__all__ = [
    # 枚举
    "OperatorType",
    "FieldType",
    "DenominatorType",
    "NumeratorLogic",
    "MetricStatus",
    # 模型
    "Condition",
    "CommonDenominator",
    "FieldMapping",
    "GroupDimension",
    "Metric",
    "MetricResult",
    "MetricsConfig",
    "StatsResult",
    # 异常
    "DomainException",
    "ValidationError",
    "ConfigLoadError",
    "DataServiceError",
    "DataFilterError",
    "ExportError",
]

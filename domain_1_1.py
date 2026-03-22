"""
[EXC-001] 领域异常模块
定义系统核心异常类型，用于统一的错误处理

核心职责:
- 提供 ValidationError 用于数据验证失败
- 提供 ConfigLoadError 用于配置加载失败
- 提供 DataServiceError 用于数据处理失败

为什么这样设计:
使用自定义异常可以让上层代码精确捕获和处理错误，
而不是依赖泛化的 Exception，提高代码可维护性。
"""

from typing import Optional, List, Dict, Any


# ==================== 基础异常类 ====================

class DomainException(Exception):
    """[EXC-001-01] 领域层基础异常
    所有领域层异常的基类

    核心职责:
    - 提供统一的异常基类
    - 携带错误消息和可选的详细信息

    为什么这样设计:
    便于上层通过 except DomainException 统一捕获所有领域层异常
    """
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


# ==================== 验证异常 ====================

class ValidationError(DomainException):
    """[EXC-001-02] 验证失败异常
    用于数据验证、配置验证失败时抛出

    核心职责:
    - 标记验证失败的字段
    - 携带验证错误的详细列表

    为什么这样设计:
    口径配置、数据筛选等场景需要精确报告哪些字段验证失败，
    此异常支持携带字段级错误列表，便于前端展示。
    """
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        errors: Optional[List[Dict[str, Any]]] = None
    ):
        super().__init__(message)
        self.field = field
        self.errors = errors or []

    def add_error(self, field: str, error: str, value: Any = None):
        """添加一个字段级错误"""
        self.errors.append({
            "field": field,
            "error": error,
            "value": value
        })

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，便于序列化"""
        return {
            "message": self.message,
            "field": self.field,
            "errors": self.errors
        }


# ==================== 配置异常 ====================

class ConfigLoadError(DomainException):
    """[EXC-001-03] 配置加载失败异常
    用于口径配置、API 配置等加载失败时抛出

    核心职责:
    - 标记配置加载失败的来源
    - 携带原始错误信息

    为什么这样设计:
    配置可能来自 JSON 文件、数据库、用户输入等多种来源，
    需要区分不同类型的加载失败。
    """
    def __init__(
        self,
        message: str,
        source: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(message)
        self.source = source
        self.original_error = original_error


# ==================== 数据服务异常 ====================

class DataServiceError(DomainException):
    """[EXC-001-04] 数据服务异常
    用于数据处理、筛选、统计等服务失败时抛出

    核心职责:
    - 标记数据服务操作失败
    - 携带操作类型和受影响的数据

    为什么这样设计:
    数据服务包含多种操作（清洗、筛选、统计），
    需要区分失败的操作类型以便调试。
    """
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        affected_rows: Optional[int] = None
    ):
        super().__init__(message)
        self.operation = operation
        self.affected_rows = affected_rows


class DataFilterError(DataServiceError):
    """[EXC-001-05] 数据筛选失败异常
    用于条件筛选失败时抛出

    核心职责:
    - 标记筛选条件无效
    - 携带导致失败的筛选条件

    为什么这样设计:
    筛选条件可能引用不存在的字段或使用不支持的运算符，
    需要精确报告失败的条件。
    """
    def __init__(
        self,
        message: str,
        condition: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, operation="filter")
        self.condition = condition


# ==================== 导出异常 ====================

class ExportError(DomainException):
    """[EXC-001-06] 导出失败异常
    用于 Word/Excel导出失败时抛出

    核心职责:
    - 标记导出操作失败
    - 携带导出格式和目标路径

    为什么这样设计:
    导出可能因权限、路径、格式不支持等原因失败，
    需要区分不同导出类型的错误。
    """
    def __init__(
        self,
        message: str,
        export_format: Optional[str] = None,
        target_path: Optional[str] = None
    ):
        super().__init__(message)
        self.export_format = export_format
        self.target_path = target_path

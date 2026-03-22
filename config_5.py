"""
[config_5-001] 配置管理模块
管理 API 配置、环境变量等

核心职责:
- 加载和保存 API 配置
- 读取环境变量
- 提供默认配置

为什么这样设计:
将配置管理集中化，便于修改和维护，
同时支持配置持久化。
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass


# ==================== 配置数据类 ====================

@dataclass
class APIConfig:
    """[config_5-001-01] API 配置数据类
    封装 LLM API 连接配置

    核心职责:
    - 存储 API 密钥、基础 URL、模型名称
    - 提供字典转换方法

    为什么这样设计:
    使用 dataclass 提供类型安全和默认值
    """
    api_key: str = ""
    base_url: str = ""
    model_name: str = "glm-4"

    def to_dict(self) -> Dict[str, str]:
        """转换为字典格式"""
        return {
            "api_key": self.api_key,
            "base_url": self.base_url,
            "model_name": self.model_name
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "APIConfig":
        """从字典创建"""
        return cls(
            api_key=data.get("api_key", ""),
            base_url=data.get("base_url", ""),
            model_name=data.get("model_name", "glm-4")
        )

    def is_valid(self) -> bool:
        """判断配置是否有效"""
        return bool(self.api_key.strip() and self.base_url.strip() and self.model_name.strip())


# ==================== 配置管理器 ====================

class ConfigManager:
    """[config_5-001-10] 配置管理器
    管理应用配置的加载、保存、删除

    核心职责:
    - load_api_config: 加载 API 配置
    - save_api_config: 保存 API 配置
    - delete_api_config: 删除 API 配置
    - load_env: 加载环境变量

    为什么这样设计:
    集中管理配置，提供统一的 API，
    支持配置文件和环境变量两种方式。
    """

    def __init__(self, config_dir: Optional[str] = None):
        """
        初始化配置管理器

        Args:
            config_dir: 配置文件目录，默认为模块所在目录
        """
        if config_dir is None:
            config_dir = os.path.dirname(__file__)
        self.config_dir = config_dir

    def get_config_path(self, filename: str) -> str:
        """[config_5-001-11] 获取配置文件路径"""
        return os.path.join(self.config_dir, filename)

    def load_api_config(self, filename: str = ".api_config.json") -> APIConfig:
        """
        [config_5-001-12] 加载 API 配置
        从 JSON 文件加载 API 配置

        Args:
            filename: 配置文件名

        Returns:
            APIConfig: API 配置对象
        """
        config_path = self.get_config_path(filename)
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return APIConfig.from_dict(data)
            except (json.JSONDecodeError, IOError):
                pass
        return APIConfig()

    def save_api_config(
        self,
        api_key: str,
        base_url: str,
        model_name: str,
        filename: str = ".api_config.json"
    ) -> bool:
        """
        [config_5-001-13] 保存 API 配置
        将 API 配置保存到 JSON 文件

        Args:
            api_key: API 密钥
            base_url: API 基础 URL
            model_name: 模型名称
            filename: 配置文件名

        Returns:
            bool: 是否保存成功
        """
        config_path = self.get_config_path(filename)
        try:
            config = APIConfig(api_key=api_key, base_url=base_url, model_name=model_name)
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config.to_dict(), f, ensure_ascii=False, indent=2)
            return True
        except IOError:
            return False

    def delete_api_config(self, filename: str = ".api_config.json") -> bool:
        """
        [config_5-001-14] 删除 API 配置
        删除已保存的 API 配置文件

        Args:
            filename: 配置文件名

        Returns:
            bool: 是否删除成功
        """
        config_path = self.get_config_path(filename)
        if os.path.exists(config_path):
            try:
                os.remove(config_path)
                return True
            except IOError:
                return False
        return True

    def load_env(self, filename: str = ".env") -> Dict[str, str]:
        """
        [config_5-001-15] 加载环境变量
        从.env 文件加载环境变量

        Args:
            filename: .env 文件名

        Returns:
            Dict[str, str]: 加载的环境变量
        """
        env_path = self.get_config_path(filename)
        env_vars = {}

        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        # 跳过注释和空行
                        if not line or line.startswith("#"):
                            continue
                        # 解析 KEY=VALUE 格式
                        if "=" in line:
                            key, value = line.split("=", 1)
                            key = key.strip()
                            value = value.strip()
                            os.environ.setdefault(key, value)
                            env_vars[key] = value
            except IOError:
                pass

        return env_vars


# ==================== 默认配置常量 ====================

# [config_5-001-20] 默认 API 配置
# 默认的 LLM API 配置
DEFAULT_API_CONFIG = APIConfig(
    api_key="",
    base_url="https://open.bigmodel.cn/api/paas/v4",
    model_name="glm-4"
)

# [config_5-001-21] 默认输出目录
# 导出文件的默认输出目录
DEFAULT_OUTPUT_DIR = "temp/exported"

# [config_5-001-22] 默认阈值配置
# 数据处理相关的默认阈值
DEFAULT_THRESHOLDS = {
    "field_dist_threshold": 50,  # 字段分布低基数阈值
    "field_dist_high_unique_ratio": 0.8,  # 高唯一率阈值
    "field_dist_name_match_ratio": 0.7,  # 人名匹配阈值
    "confidence_high": 80,  # 高置信度阈值
    "confidence_medium": 60,  # 中置信度阈值
}

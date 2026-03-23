"""
[services_2-002] LLM 服务模块
封装大模型 API 调用（兼容 OpenAI SDK 格式）

核心职责:
- LLMService: 提供文本对话、多模态调用服务
- JSON 解析：支持截断修复、代码块提取
- 错误处理：将 API 错误转换为中文提示

为什么这样设计:
将 LLM 调用逻辑封装在服务类中，便于切换模型提供商，
同时提供统一的错误处理和 JSON 解析能力。
"""

from openai import OpenAI
from typing import Optional, Dict, Any, List, Tuple
import json
import re
import httpx


# ==================== 工具函数 ====================

def format_api_error(error: Exception) -> str:
    """
    [services_2-002-01] 格式化 API 错误信息
    将 API 错误转换为中文提示，便于用户理解

    核心职责:
    - 识别常见错误类型（SSL、401、403、404、429、超时等）
    - 返回针对性的中文错误提示

    为什么这样设计:
    原始英文错误信息不够直观，中文提示帮助用户快速定位问题
    """
    error_str = str(error)
    lower_error = error_str.lower()

    if "unexpected keyword argument 'proxies'" in lower_error:
        return "连接失败：当前依赖版本与代理参数不兼容，请将 httpx 固定为 0.27.2（pip install httpx==0.27.2）后重试。"
    if "ssl" in lower_error or "certificate" in lower_error or "issuer" in lower_error:
        return "连接失败：SSL 证书校验失败，请检查代理证书或 CA 配置。"
    if "401" in lower_error or "invalid api key" in lower_error or "authentication" in lower_error:
        return "连接失败：API Key 无效或未授权，请检查密钥是否正确。"
    if "403" in lower_error:
        return "连接失败：当前账号无权限访问该模型或接口。"
    if "404" in lower_error:
        return "连接失败：接口地址或模型不存在，请检查 Base URL 和模型名称是否正确。"
    if "429" in lower_error or "rate limit" in lower_error:
        return "连接失败：请求过于频繁，已触发限流，请稍后重试。"
    if "timeout" in lower_error or "timed out" in lower_error:
        return "连接失败：请求超时，请检查网络连接或稍后重试。"
    if "connection" in lower_error or "network" in lower_error:
        return "连接失败：网络连接异常，请检查网络或代理设置。"
    if "dns" in lower_error:
        return "连接失败：DNS 解析失败，请检查接口地址是否正确。"
    if "proxy" in lower_error:
        return "连接失败：代理设置异常，请检查代理配置。"
    if "model" in lower_error and ("not found" in lower_error or "does not exist" in lower_error):
        return "连接失败：模型不存在，请检查模型名称是否正确。"
    if "insufficient" in lower_error or "quota" in lower_error or "balance" in lower_error:
        return "连接失败：账户余额不足或配额已用尽。"
    return f"连接失败：{error_str}"


def get_column_values(df, column: str, max_values: int = 20) -> List[str]:
    """
    [services_2-002-02] 获取列唯一值
    获取 DataFrame 某列的唯一值列表，用于字段分析

    Args:
        df: DataFrame
        column: 列名
        max_values: 最大返回数量

    Returns:
        List[str]: 唯一值列表
    """
    unique_values = df[column].dropna().astype(str).unique().tolist()
    if len(unique_values) > max_values:
        return unique_values[:max_values] + [f"...(共{len(unique_values)}个值)"]
    return unique_values


def format_columns_info(df) -> str:
    """
    [services_2-002-03] 格式化字段信息
    将 DataFrame 字段信息格式化为字符串，用于 Prompt

    Args:
        df: DataFrame

    Returns:
        str: 格式化后的字段信息
    """
    columns_info = []
    for col in df.columns:
        unique_vals = get_column_values(df, col, max_values=20)
        columns_info.append(f"- {col}: {unique_vals}")
    return "\n".join(columns_info)


# ==================== LLM 服务类 ====================

class LLMService:
    """[services_2-002-10] LLM 服务类
    封装大模型 API 调用，支持文本和多模态请求

    核心职责:
    - call_text: 发送文本对话请求
    - call_multimodal: 发送文本 + 图片请求
    - parse_json_response: 从响应中提取并解析 JSON
    - test_connection: 测试 API 连接

    为什么这样设计:
    统一封装 LLM 调用细节，上层无需关心具体的 API 实现，
    同时提供智能的 JSON 解析和错误修复能力。
    """

    def __init__(self, api_key: str, base_url: str, model_name: str = "glm-4"):
        """
        初始化 LLM 服务

        Args:
            api_key: API 密钥
            base_url: API 基础 URL
            model_name: 模型名称
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/') if base_url else ""
        self.model_name = model_name
        self.client: Optional[OpenAI] = None

        try:
            # 创建不使用代理的 httpx 客户端
            http_client = httpx.Client(
                timeout=httpx.Timeout(connect=10.0, read=120.0, write=30.0, pool=10.0),
                proxies=None,
                trust_env=False
            )
            self.client = OpenAI(
                api_key=api_key,
                base_url=self.base_url,
                http_client=http_client
            )
        except Exception as e:
            raise RuntimeError(format_api_error(e)) from e

    def call_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4096
    ) -> str:
        """
        [services_2-002-11] 发送文本对话请求
        调用 LLM 进行文本生成

        核心职责:
        - 构建消息列表（支持 system prompt）
        - 处理不支持 max_tokens 的模型

        Args:
            prompt: 用户输入
            system_prompt: 系统提示词
            temperature: 温度参数（越低越确定）
            max_tokens: 最大 token 数

        Returns:
            str: 模型回复
        """
        if self.client is None:
            raise RuntimeError("LLM 客户端未初始化")

        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            content = response.choices[0].message.content
            return content if content is not None else ""
        except Exception as e:
            err_str = str(e).lower()
            # 部分模型不支持 max_tokens，降级重试
            if "max_tokens" in err_str or "unsupported" in err_str or "unknown" in err_str:
                try:
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=messages,
                        temperature=temperature
                    )
                    content = response.choices[0].message.content
                    return content if content is not None else ""
                except Exception as e2:
                    raise RuntimeError(format_api_error(e2)) from e2
            raise RuntimeError(format_api_error(e)) from e

    def call_multimodal(
        self,
        prompt: str,
        image_base64: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4096
    ) -> str:
        """
        [services_2-002-12] 发送多模态请求（文本 + 图片）
        调用支持视觉的 LLM 进行图文分析

        核心职责:
        - 构建多模态消息（文本 + 图片）
        - 处理不支持 max_tokens 的模型

        Args:
            prompt: 用户输入
            image_base64: 图片的 base64 编码
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大 token 数

        Returns:
            str: 模型回复
        """
        if self.client is None:
            raise RuntimeError("LLM 客户端未初始化")

        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # 构建多模态消息内容
        content = [
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{image_base64}"
                }
            }
        ]

        messages.append({"role": "user", "content": content})

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            content = response.choices[0].message.content
            return content if content is not None else ""
        except Exception as e:
            err_str = str(e).lower()
            # 部分模型不支持 max_tokens，降级重试
            if "max_tokens" in err_str or "unsupported" in err_str or "unknown" in err_str:
                try:
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=messages,
                        temperature=temperature
                    )
                    content = response.choices[0].message.content
                    return content if content is not None else ""
                except Exception as e2:
                    raise RuntimeError(format_api_error(e2)) from e2
            raise RuntimeError(format_api_error(e)) from e

    def parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        [services_2-002-13] 从 LLM 响应中提取 JSON
        支持截断修复、代码块提取

        核心职责:
        - 尝试直接解析
        - 提取 ```json 代码块中的 JSON
        - 修复被截断的 JSON

        Args:
            response: LLM 返回的原始响应

        Returns:
            Dict: 解析后的 JSON 对象

        Raises:
            ValueError: 无法解析 JSON 时抛出
        """
        # 尝试直接解析
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # 尝试提取代码块中的 JSON
        patterns = [
            r'```json\s*([\s\S]*?)\s*```',
            r'```\s*([\s\S]*?)\s*```',
            r'\{[\s\S]*\}'  # 直接匹配 JSON 对象
        ]

        for pattern in patterns:
            match = re.search(pattern, response)
            if match:
                try:
                    json_str = match.group(1) if '```' in pattern else match.group(0)
                    return json.loads(json_str)
                except (json.JSONDecodeError, IndexError):
                    continue

        # 尝试修复截断的 JSON（模型输出被 max_tokens 截断）
        repaired = self._try_repair_truncated_json(response)
        if repaired is not None:
            return repaired

        raise ValueError(f"无法从响应中解析 JSON，原始响应:\n{response[:500]}...")

    @staticmethod
    def _try_repair_truncated_json(response: str) -> Optional[Dict[str, Any]]:
        """
        [services_2-002-14] 修复被截断的 JSON
        通过补齐括号来修复不完整的 JSON

        核心职责:
        - 统计未闭合的括号
        - 去掉末尾不完整的键值对
        - 补齐缺失的括号

        为什么这样设计:
        模型输出可能被 max_tokens 截断，导致 JSON 不完整，
        自动修复提高解析成功率。
        """
        # 提取从第一个 { 开始的内容
        start = response.find('{')
        if start == -1:
            return None
        json_str = response[start:]

        # 统计未闭合的括号
        open_braces = 0
        open_brackets = 0
        in_string = False
        escape_next = False

        for ch in json_str:
            if escape_next:
                escape_next = False
                continue
            if ch == '\\' and in_string:
                escape_next = True
                continue
            if ch == '"' and not escape_next:
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch == '{':
                open_braces += 1
            elif ch == '}':
                open_braces -= 1
            elif ch == '[':
                open_brackets += 1
            elif ch == ']':
                open_brackets -= 1

        # 即使括号看起来平衡，JSON 也可能在字符串内部被截断（in_string 为 True）
        # 统计结束时是否处于字符串内
        if open_braces == 0 and open_brackets == 0 and not in_string:
            return None  # 括号平衡且不在字符串内仍解析失败，非截断问题

        # 去掉末尾不完整的键值对
        trimmed = json_str.rstrip()

        # 尝试去掉末尾不完整的内容后补齐括号
        for cut_chars in ['', ',', ', ']:
            candidate = trimmed.rstrip(cut_chars)
            suffix = ']' * max(0, open_brackets) + '}' * max(0, open_braces)
            try:
                return json.loads(candidate + suffix)
            except json.JSONDecodeError:
                continue

        # 策略1：逐字符从末尾回退（最多退 2000 字符应对轻度截断）
        for i in range(min(2000, len(trimmed))):
            candidate = trimmed[:len(trimmed) - i]

            # 重新计算括号
            ob, osb = 0, 0
            ins, esc = False, False
            for ch in candidate:
                if esc:
                    esc = False
                    continue
                if ch == '\\' and ins:
                    esc = True
                    continue
                if ch == '"':
                    ins = not ins
                    continue
                if ins:
                    continue
                if ch == '{':
                    ob += 1
                elif ch == '}':
                    ob -= 1
                elif ch == '[':
                    osb += 1
                elif ch == ']':
                    osb -= 1

            if ins:
                candidate += '"'  # 闭合未完成的字符串

            suffix = ']' * max(0, osb) + '}' * max(0, ob)
            try:
                result = json.loads(candidate + suffix)
                if isinstance(result, dict):
                    return result
            except json.JSONDecodeError:
                continue

        # 策略2：O(N) 扫描找自然截断点（depth=1时刚关闭了一个顶层子对象，如一条 metric）
        # 适用于最后一条 metric 很长（超过 2000 字符）导致策略1回退不足的情况
        valid_cut_positions = []
        depth = 0
        ins2, esc2 = False, False
        for idx, ch in enumerate(trimmed):
            if esc2:
                esc2 = False
                continue
            if ch == '\\' and ins2:
                esc2 = True
                continue
            if ch == '"':
                ins2 = not ins2
                continue
            if ins2:
                continue
            if ch in ('{', '['):
                depth += 1
            elif ch in ('}', ']'):
                depth -= 1
                if depth == 1:
                    # 刚关闭了一个嵌套对象/数组，是潜在的有效截断点
                    valid_cut_positions.append(idx + 1)

        # 从最后的有效截断点向前尝试（最多尝试 50 个）
        for pos in reversed(valid_cut_positions[-50:]):
            candidate = trimmed[:pos]
            ob2, osb2 = 0, 0
            ins3, esc3 = False, False
            for ch in candidate:
                if esc3:
                    esc3 = False
                    continue
                if ch == '\\' and ins3:
                    esc3 = True
                    continue
                if ch == '"':
                    ins3 = not ins3
                    continue
                if ins3:
                    continue
                if ch == '{':
                    ob2 += 1
                elif ch == '}':
                    ob2 -= 1
                elif ch == '[':
                    osb2 += 1
                elif ch == ']':
                    osb2 -= 1
            suffix2 = ']' * max(0, osb2) + '}' * max(0, ob2)
            try:
                result = json.loads(candidate + suffix2)
                if isinstance(result, dict):
                    return result
            except json.JSONDecodeError:
                continue

        return None

    def test_connection(self) -> Tuple[bool, str]:
        """
        [services_2-002-15] 测试 API 连接
        验证 API 配置是否正常

        Returns:
            Tuple[bool, str]: (是否成功，消息)
        """
        # 基本参数检查
        if not self.api_key or not self.api_key.strip():
            return False, "请填写 API 密钥"
        if not self.base_url or not self.base_url.strip():
            return False, "请填写接口地址"
        if not self.model_name or not self.model_name.strip():
            return False, "请填写模型名称"

        try:
            response = self.call_text("你好，请回复'连接成功'", max_tokens=50)
            if response and len(response) > 0:
                return True, f"连接成功！模型响应：{response[:50]}..."
            else:
                return False, "连接异常：模型未返回有效响应"
        except Exception as e:
            return False, format_api_error(e)

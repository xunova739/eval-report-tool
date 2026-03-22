# 标注评测报告生成工具

一个基于 Streamlit 的标注评测报告自动生成工具。

## 环境要求

- Python 3.9+
- 无需其他环境配置

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动应用

```bash
cd eval-report-tool
python -m streamlit run app.py --server.port 8502
```

### 3. 打开浏览器

访问 http://localhost:8502

## 功能说明

1. 上传标注数据 Excel 文件
2. 上传口径 Excel 文件
3. AI 自动解析口径配置
4. 自动生成统计结果
5. 生成评测报告

## API 配置

首次使用需要在界面中配置 AI API：
- API Key
- Base URL（如使用中转站）
- Model Name（默认 glm-4）

## 常见问题

### Q: 启动失败？
A: 确保使用 Python 3.9+，检查依赖是否安装成功

### Q: API 调用失败？
A: 检查 API Key 是否正确，Base URL 是否可访问

## 技术支持

如有问题请联系开发者。
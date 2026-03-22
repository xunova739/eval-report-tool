import re
import os

filepath = 'app.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace specific emojis and numbering that look cheap
replacements = {
    "1️⃣ ": "1. ",
    "2️⃣ ": "2. ",
    "3️⃣ ": "3. ",
    "4️⃣ ": "4. ",
    "5️⃣ ": "5. ",
    "6️⃣ ": "6. ",
    "7️⃣ ": "7. ",
    "8️⃣ ": "8. ",
    "9️⃣ ": "9. ",
    "🔟 ": "10. ",
    "✅ 确认口径配置": "确认口径配置",
    "🚀 开始统计": "开始统计",
    "🔄 重置": "重置",
    "📋 查看配置详情": "查看配置详情",
    "📝 生成评测报告": "生成评测报告",
    "🔍 解析Excel口径": "解析Excel口径",
    "📥 导出为Excel": "导出为Excel"
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

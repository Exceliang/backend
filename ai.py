import os
import json
from openai import OpenAI

client=OpenAI(
    api_key=os.environ.get("SILICONFLOW_API_KEY","sk"),
    base_url="https://api.siliconflow.cn/v1"
)

system_prompt=(
    """
    你是一个任务拆解助手。请将用户的自然语言输入拆解为多个独立任务，并严格以 JSON 格式输出。
    输出结构必须包含一个 "tasks" 数组，每个任务对象包含以下字段：
    - title: 字符串，任务标题（1~50字）
    - category: 字符串，只能从 "ai"、"invest"、"health" 中三选一
    - estimated_minutes: 正整数，预估耗时（分钟）

    示例输出：
    {"tasks": [{"title": "阅读金钱心理学", "category": "invest", "estimated_minutes": 40}]}
    """
)

user_input=("今晚花40分钟复盘金钱心理学，再去健身房练1小时卧推，睡前花20分钟看下FastAPI文档")

response=client.chat.completions.create(
    model="deepseek-ai/DeepSeek-V4-Flash",
    messages=[
        {"role":"system","content":system_prompt},
        {"role":"user","content":user_input}
    ],
    response_format={"type":"json_object"},
    temperature=0.1
)

raw_json=response.choices[0].message.content
data=json.loads(raw_json)
print(json.dumps(data,ensure_ascii=False,indent=2))
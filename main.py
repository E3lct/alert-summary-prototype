"""用虚构告警练习：先统计事实，再选择是否调用大模型。"""

from collections import Counter
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import requests


load_dotenv()
app = FastAPI(title="告警摘要练习原型")
EVENTS_FILE = Path(__file__).with_name("sample_events.json")
MODEL_URL = "https://api.deepseek.com/chat/completions"


class SummaryRequest(BaseModel):
    range_days: int = Field(default=7, ge=1, le=30)


def load_events():
    with EVENTS_FILE.open(encoding="utf-8") as file:
        return json.load(file)


def count_alerts(events, range_days):
    selected = [event for event in events if 0 <= event["days_ago"] < range_days]
    by_type = Counter(event["type"] for event in selected)
    return {
        "range_days": range_days,
        "total": len(selected),
        "by_type": dict(sorted(by_type.items())),
    }


def local_summary(facts):
    if facts["total"] == 0:
        return f"模拟数据：近{facts['range_days']}天没有告警。"
    parts = "、".join(f"{kind} {count} 次" for kind, count in facts["by_type"].items())
    return f"模拟数据：近{facts['range_days']}天共有{facts['total']}次告警，其中{parts}。"


def prompt_for(facts):
    return (
        "请仅根据以下模拟告警统计写两句话：第一句准确概括次数，第二句给出谨慎的检查建议。"
        "不要编造原因、额外次数或医学诊断。\n"
        f"统计数据：{json.dumps(facts, ensure_ascii=False)}"
    )


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/events")
def list_events():
    return {"source": "synthetic", "items": load_events()}


@app.post("/api/summary")
def create_summary(request: SummaryRequest):
    facts = count_alerts(load_events(), request.range_days)
    return {"source": "synthetic", "facts": facts, "summary": local_summary(facts)}


@app.post("/api/ai-summary")
def create_ai_summary(request: SummaryRequest):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key or api_key == "replace_with_your_key":
        raise HTTPException(status_code=503, detail="请先在本地设置 DEEPSEEK_API_KEY")

    facts = count_alerts(load_events(), request.range_days)
    try:
        response = requests.post(
            MODEL_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "你只根据提供的统计事实写简短中文摘要。"},
                    {"role": "user", "content": prompt_for(facts)},
                ],
                "stream": False,
            },
            timeout=20,
        )
        response.raise_for_status()
        summary = response.json()["choices"][0]["message"]["content"]
    except (requests.RequestException, KeyError, IndexError, ValueError) as error:
        raise HTTPException(status_code=502, detail="模型调用失败，请检查网络、密钥和额度") from error

    return {"source": "synthetic + deepseek-api", "facts": facts, "summary": summary}

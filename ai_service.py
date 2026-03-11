import httpx
import os
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any

DO_INFERENCE_MODEL = os.getenv("DO_INFERENCE_MODEL", "openai-gpt-oss-120b")
DO_INFERENCE_KEY = os.getenv("DIGITALOCEAN_INFERENCE_KEY")

def _coerce_unstructured_payload(raw_text: str) -> Dict[str, Any]:
    compact = raw_text.strip()
    tags = [part.strip(" -•\t") for part in re.split(r",|\\n", compact) if part.strip(" -•\t")]
    return {
        "note": "Model returned plain text instead of JSON",
        "raw": compact,
        "text": compact,
        "summary": compact,
        "tags": tags[:6],
    }


async def _call_inference(messages: List[Dict[str, str]], max_tokens: int = 512) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=90.0) as client:
        headers = {
            "Authorization": f"Bearer {DO_INFERENCE_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": DO_INFERENCE_MODEL,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        try:
            response = await client.post("https://inference.do-ai.run/v1/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return _extract_json(content)
        except Exception:
            return {
                "note": "AI is temporarily unavailable. Try again later."
            }

def _extract_json(text: str) -> str:
    m = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", text, re.DOTALL)
    if m: return m.group(1).strip()
    m = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if m: return m.group(1).strip()
    return text.strip()

async def call_forecast(start_date: datetime, days: int) -> (str, str):
    forecast_prompt = f"Generate a {days}-day cash flow forecast starting from {start_date.strftime('%Y-%m-%d')}."
    messages = [
        {"role": "system", "content": "You are a financial forecasting assistant."},
        {"role": "user", "content": forecast_prompt}
    ]
    result = await _call_inference(messages, max_tokens=512)
    if "note" in result:
        return "", result["note"]
    return result.get("forecast_data", "{}"), result.get("confidence_interval", "{}")

async def allocate_goal(goal_id: int, target_amount: float, target_date: datetime) -> (float, str):
    allocation_prompt = f"Calculate monthly allocation for goal {goal_id} with target amount ${target_amount} by {target_date.strftime('%Y-%m-%d')}."
    messages = [
        {"role": "system", "content": "You are a budget allocation assistant."},
        {"role": "user", "content": allocation_prompt}
    ]
    result = await _call_inference(messages, max_tokens=512)
    if "note" in result:
        return 0.0, result["note"]
    return float(result.get("monthly_allocation", 0.0)), result.get("allocation_schedule", "{}")
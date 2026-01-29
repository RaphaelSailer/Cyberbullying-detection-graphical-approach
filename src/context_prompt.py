# src/context_prompt.py
from typing import List, Dict

BEHAVIORS = [
    "Teased", "Threatened", "Lies", "Profanity",
    "Teammate hostility", "Opponent hostility",
    "Exclusion", "Group exclusion", "Kicked out of group"
]

def build_prompt(ocr_text: str, image_filename: str, n_messages: int = 24) -> str:
    behaviors_str = ", ".join(BEHAVIORS)

    return f"""
You are generating synthetic DOTA 2 chat data for a cyberbullying detection dataset.
All players, messages, and scenarios are fictional. No real individuals.

INPUTS
- Image filename: {image_filename}
- OCR text extracted from screenshot (may contain errors):
{ocr_text}

TASK
1) Describe what is happening in the screenshot in the context of DOTA 2 (max 2 sentences).
2) Describe the broader match context (max 2 sentences).
3) Generate {n_messages} synthetic chat messages between fictional players that reflect DOTA 2 context.
4) Each message must include:
   - speaker: short fictional username
   - target: optional username being addressed (or null)
   - text: short in-game chat line
   - behavior_label: one of [{behaviors_str}]

OUTPUT FORMAT (JSON ONLY)
{{
  "scene_description": "...",
  "match_context": "...",
  "messages": [
    {{"speaker":"...", "target":null, "text":"...", "behavior_label":"Teased"}}
  ]
}}

RULES
- Ensure that the messages require knowledge of the context to interpret whether cyberbullying is present. Don't make them all overt.
- No real names, no doxxing, no slurs.
- Make messages realistic for DOTA 2 chat.

Return JSON only. No markdown. No extra text.
""".strip()

#src/trim_jsonl.py
import json
from pathlib import Path

INPUT_PATH = Path("data/out/synthetic.jsonl")
OUTPUT_PATH = Path("data/out/synthetic_trimmed.jsonl")

def trim_record(record: dict) -> dict:
    out = {
        "image": record.get("image"),
        "ocr_text": record.get("ocr_text"),
    }

    gen = record.get("generated", {})
    if not isinstance(gen, dict):
        return out

    out["generated"] = {
        "scene_description": gen.get("scene_description"),
        "match_context": gen.get("match_context"),
        "messages": []
    }

    for msg in gen.get("messages", []):
        if not isinstance(msg, dict):
            continue

        cleaned_msg = {
            "speaker": msg.get("speaker"),
            "text": msg.get("text")
        }

        if "target" in msg and msg.get("target") is not None:
            cleaned_msg["target"] = msg.get("target")

        out["generated"]["messages"].append(cleaned_msg)

    return out


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with INPUT_PATH.open("r", encoding="utf-8") as fin, \
         OUTPUT_PATH.open("w", encoding="utf-8") as fout:

        for line_num, line in enumerate(fin, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                record = json.loads(line)
                trimmed = trim_record(record)
                fout.write(json.dumps(trimmed, ensure_ascii=False) + "\n")
            except Exception as e:
                fout.write(json.dumps({
                    "error": "trim_failed",
                    "line": line_num,
                    "reason": str(e)
                }) + "\n")

    print(f"Trimmed file written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
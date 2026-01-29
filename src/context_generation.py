print("MAIN FILE LOADED")

# src/main.py
import json
from pathlib import Path
from tqdm import tqdm

from src.ocr import ocr_image
from src.context_prompt import build_prompt
from src.llm_define import LLMClient


def main():
    screenshots_dir = Path("data/screenshots")
    out_path = Path("data/out/synthetic.jsonl")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    client = LLMClient()

    images = sorted([p for p in screenshots_dir.glob("*") if p.suffix.lower() in [".png", ".jpg", ".jpeg"]])
    if not images:
        print("No images found in data/screenshots/")
        return

    with out_path.open("w", encoding="utf-8") as f:
        for img_path in tqdm(images, desc="Processing screenshots"):
            ocr_res = ocr_image(str(img_path))
            prompt = build_prompt(ocr_res.raw_text, img_path.name, n_messages=8)

            raw = client.generate(prompt)

            # Basic robustness: try to parse JSON; if it fails, save raw for debugging
            try:
                parsed = json.loads(raw)
                record = {
                    "image": img_path.name,
                    "ocr_text": ocr_res.raw_text,
                    "generated": parsed
                }
            except json.JSONDecodeError:
                record = {
                    "image": img_path.name,
                    "ocr_text": ocr_res.raw_text,
                    "generated_raw": raw,
                    "error": "json_parse_failed"
                }

            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Saved: {out_path}")

if __name__ == "__main__":
    main()

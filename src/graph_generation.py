# src/graph_generation.py
import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from src.graph_prompt import GRAPH_SYSTEM_PROMPT
from src.llm_define import LLMClient


ALLOWED_NODE_TYPES = {"player", "character", "event", "message", "team"}
ALLOWED_EDGE_TYPES = {
    "sent",
    "targets",
    "replied_to",
    "same_team",
    "controls",
    "participated_in",
    "occurred_near",
    "prior_conflict",
    "prior_affiliation",
}


def _safe_json_loads(s: str) -> Optional[Any]:
    try:
        return json.loads(s)
    except Exception:
        return None


def _validate_graph_obj(g: Any) -> Tuple[bool, str]:
    if not isinstance(g, dict):
        return False, "graph is not a JSON object"

    expected = {"meta", "nodes", "edges"}
    if set(g.keys()) != expected:
        return False, f"top-level keys must be exactly {sorted(expected)}"

    meta = g["meta"]
    nodes = g["nodes"]
    edges = g["edges"]

    if not isinstance(meta, dict):
        return False, "meta must be an object"
    if not isinstance(nodes, list):
        return False, "nodes must be an array"
    if not isinstance(edges, list):
        return False, "edges must be an array"

    if "directed" not in meta or not isinstance(meta["directed"], bool):
        return False, "meta.directed must exist and be boolean"

    ids = set()
    for n in nodes:
        if not isinstance(n, dict):
            return False, "node is not an object"
        if "id" not in n or "t" not in n:
            return False, "each node must have id and t"
        if not isinstance(n["id"], str) or not n["id"]:
            return False, "node.id must be non-empty string"
        if n["id"] in ids:
            return False, f"duplicate node id: {n['id']}"
        ids.add(n["id"])

        if n["t"] not in ALLOWED_NODE_TYPES:
            return False, f"node type not allowed: {n['t']}"

        if "text" in n and n["t"] != "message":
            return False, "only message nodes may include text"

    for e in edges:
        if not isinstance(e, dict):
            return False, "edge is not an object"
        if "s" not in e or "t" not in e or "r" not in e:
            return False, "each edge must have s, t, r"
        if e["s"] not in ids:
            return False, f"edge source id not found: {e['s']}"
        if e["t"] not in ids:
            return False, f"edge target id not found: {e['t']}"
        if e["r"] not in ALLOWED_EDGE_TYPES:
            return False, f"edge relation not allowed: {e['r']}"

    return True, "ok"


def _build_user_payload(record: Dict[str, Any]) -> Dict[str, Any]:
    gen = record.get("generated", {})
    return {
        "scene_description": gen.get("scene_description", ""),
        "match_context": gen.get("match_context", ""),
        "messages": gen.get("messages", []),
    }


def generate_graphs(
    in_path: Path,
    out_path: Path,
    max_new_tokens: int = 700,
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    client = LLMClient()  # uses Mistral defaults in Colab

    total = ok = bad = 0

    with in_path.open("r", encoding="utf-8") as fin, out_path.open("w", encoding="utf-8") as fout:
        for line_no, line in enumerate(fin, start=1):
            line = line.strip()
            if not line:
                continue

            total += 1
            rec = json.loads(line)

            payload = _build_user_payload(rec)
            messages = [
                {"role": "system", "content": GRAPH_SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ]

            raw = client.generate_from_messages(messages, max_tokens=max_new_tokens)

            graph_obj = _safe_json_loads(raw)
            if graph_obj is None:
                bad += 1
                fout.write(json.dumps({"image": rec.get("image"), "error": "graph_json_parse_failed", "raw": raw}, ensure_ascii=False) + "\n")
                continue

            valid, reason = _validate_graph_obj(graph_obj)
            if not valid:
                bad += 1
                fout.write(json.dumps({"image": rec.get("image"), "error": "graph_schema_invalid", "reason": reason, "raw_graph": graph_obj}, ensure_ascii=False) + "\n")
                continue

            ok += 1
            fout.write(json.dumps({"image": rec.get("image"), "graph": graph_obj}, ensure_ascii=False) + "\n")

            if total % 10 == 0:
                print(f"Processed {total} | ok={ok} bad={bad}")

    print(f"Done. total={total} ok={ok} bad={bad}")
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    IN = Path("data/out/synthetic-messages-cleaned.jsonl")
    OUT = Path("data/out/graphs.jsonl")
    generate_graphs(IN, OUT)

import os, json, re
from pathlib import Path

try:
    from openai import OpenAI
except Exception as e:
    raise SystemExit("OpenAI SDK missing: ensure requirements.txt installed") from e

MODEL = os.environ.get("OPENAI_MODEL", "gpt-5")  # set repo secret OPENAI_MODEL if needed
TASK  = os.environ.get("TASK", "").strip()
if not TASK:
    raise SystemExit("No TASK provided. Use the workflow input.")

SAFE_PREFIXES = (
    "apps/", "infra/", "packages/", "tools/", "docs/", "web/", "ios/", "android/"
)

SYSTEM_PROMPT = """You are a senior engineer working in a monorepo.
You receive a TASK. Return a SINGLE JSON object with keys:
- plan (short markdown of what you will add/change and why),
- files (array of { "path": "relative/path.ext", "content": "FULL file content" }),
- commit_message,
- pr_title,
- pr_body.
Rules:
- Output ONLY valid JSON (no backticks, no prose outside JSON).
- Use Unix newlines.
- Keep edits focused on the TASK.
- Place new files only under: apps/, infra/, packages/, tools/, docs/, web/, ios/, android/.
- Include minimal tests where reasonable; code should compile/build.
"""

def ensure_safe_path(p: str) -> Path:
    p = p.strip().lstrip("./")
    path = Path(p)
    if ".." in path.parts:
        raise ValueError(f"Refusing path with '..': {p}")
    if not any(str(path).startswith(pref) for pref in SAFE_PREFIXES):
        raise ValueError(f"Path not allowed: {p}")
    return path

def main():
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    resp = client.responses.create(
        model=MODEL,
        input=[
            {"role":"system","content":SYSTEM_PROMPT},
            {"role":"user","content": f"TASK:\n{TASK}\nExisting repo may be empty. Create missing folders as needed."}
        ],
        temperature=0.2,
    )

    # Extract assistant text (new SDKs expose .output_text)
    try:
        text = resp.output_text
    except Exception:
        # Fallback path if SDK differs
        text = resp.output[0].content[0].text.value

    # Find the last JSON object in the output
    m = re.search(r'\{.*\}\s*$', text, flags=re.S)
    if not m:
        raise SystemExit("AI did not return JSON. Raw output:\n" + text)
    spec = json.loads(m.group(0))

    # Write files
    for f in spec.get("files", []):
        path = ensure_safe_path(f["path"])
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(f["content"])

    # Write helper docs (optional but handy)
    Path("AI_PLAN.md").write_text(spec.get("plan",""), encoding="utf-8")
    Path("PR_TITLE.txt").write_text(spec.get("pr_title","AI update"), encoding="utf-8")
    Path("PR_BODY.md").write_text(spec.get("pr_body",""), encoding="utf-8")

    print("AI Coder wrote files; a PR will be opened in the next step.")

if __name__ == "__main__":
    main()

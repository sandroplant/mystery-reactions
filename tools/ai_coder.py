import os
import json
import re
from pathlib import Path

try:
    from openai import OpenAI
except Exception as e:
    raise SystemExit("OpenAI SDK missing: ensure tools/requirements.txt has openai>=1.40.0") from e

# ---- Config ---------------------------------------------------------------

# Prefer a stable, widely-available model unless you override via repo secret OPENAI_MODEL
MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o").strip()

TASK = os.environ.get("TASK", "").strip()
if not TASK:
    raise SystemExit("No TASK provided. Use the workflow input when running the action.")

# Only allow writes inside these folders (plus a tiny allowlist of root files)
SAFE_PREFIXES = (
    ".github/",
    "apps/",
    "infra/",
    "packages/",
    "tools/",
    "docs/",
    "web/",
    "ios/",
    "android/",
)

ALLOWED_ROOT_FILES = {
    "README.md",
    "LICENSE",
    ".gitignore",
    ".editorconfig",
}

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
- Keep edits focused on the TASK (atomic PR).
- Place new files only under: .github/, apps/, infra/, packages/, tools/, docs/, web/, ios/, android/.
- You MAY write a small set of safe root files: README.md, LICENSE, .gitignore, .editorconfig
- Include minimal tests where reasonable; code should compile/build.
"""

# ---- Helpers --------------------------------------------------------------

def ensure_safe_path(p: str) -> Path:
    """
    Normalize and validate a generated path so the agent can't escape the repo
    or modify disallowed locations.
    """
    p = (p or "").strip().lstrip("./")

    # Auto-correct a common mistake: "github/workflows/..." -> ".github/workflows/..."
    if p.startswith("github/"):
        p = "." + p

    path = Path(p)

    # Disallow creating or modifying workflow files directly
    if str(path).startswith(".github/workflows/"):
        raise ValueError("Path not allowed (workflows blocked for now): " + p)

    # No path traversal
    if ".." in path.parts:
        raise ValueError(f"Refusing path with '..': {p}")

    # Allow a tiny set of safe files at the repo root
    if path.parent == Path(".") and path.name in ALLOWED_ROOT_FILES:
        return path

    # Must be under one of the safe prefixes
    if not any(str(path).startswith(pref) for pref in SAFE_PREFIXES):
        raise ValueError(f"Path not allowed: {p}")

    return path


def extract_text_from_responses(resp) -> str:
    """
    Robustly extract assistant text from the Responses API result,
    handling minor SDK variations.
    """
    # Newer SDKs provide .output_text
    if hasattr(resp, "output_text") and isinstance(resp.output_text, str):
        return resp.output_text

    # Fallbacks for older/variant SDK structures
    try:
        # resp.output[0].content[0].text.value style
        return resp.output[0].content[0].text.value  # type: ignore[attr-defined]
    except Exception:
        pass

    try:
        # Some variants expose choices/messages
        return resp.choices[0].message["content"]  # type: ignore[index]
    except Exception:
        pass

    raise SystemExit("Could not extract text from OpenAI Responses result. SDK format unexpected.")


def parse_single_json_object(s: str) -> dict:
    """
    Accept JSON with or without Markdown code fences.
    Find the last JSON object and parse it.
    """
    # Strip Markdown code fences like ```json ... ``` or ``` ... ```
    s_no_fences = re.sub(r"^```(?:json)?\s*|\s*```$", "", s.strip(), flags=re.I | re.M)

    # Try to parse the whole thing first
    try:
        return json.loads(s_no_fences)
    except Exception:
        pass

    # Fallback: find the last {...} block
    m = re.search(r"\{.*\}\s*$", s_no_fences, flags=re.S)
    if not m:
        raise SystemExit("AI did not return JSON. Raw output:\n" + s)
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError as e:
        raise SystemExit(f"Failed to parse JSON from AI output: {e}\nRaw:\n{m.group(0)}") from e


# ---- Main ----------------------------------------------------------------

def main():
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("Missing OPENAI_API_KEY secret.")

    client = OpenAI(api_key=api_key)

    resp = client.responses.create(
        model=MODEL,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"TASK:\n{TASK}\n\n"
                    "Existing repo may be empty. Create missing folders as needed. "
                    "Return ONLY a single JSON object per the schema."
                ),
            },
        ],
        temperature=0.2,
    )

    text = extract_text_from_responses(resp)
    spec = parse_single_json_object(text)

    files = spec.get("files", [])
    if not isinstance(files, list):
        raise SystemExit("AI JSON missing 'files' array.")

    # Write files to disk
    for f in files:
        path_str = f.get("path", "")
        content = f.get("content", "")
        if not path_str:
            raise SystemExit("AI JSON has a file without 'path'.")
        path = ensure_safe_path(path_str)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(content)

    # Optional helper docs for PR context
    Path("AI_PLAN.md").write_text(spec.get("plan", ""), encoding="utf-8")
    Path("PR_TITLE.txt").write_text(spec.get("pr_title", "AI update"), encoding="utf-8")
    Path("PR_BODY.md").write_text(spec.get("pr_body", ""), encoding="utf-8")

    # Always ensure at least one changed file so the PR step has something to commit
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    marker = Path("tools") / (f".ai-run-{run_id}.txt" if run_id else ".ai-run-marker.txt")
    marker.write_text("ok\n", encoding="utf-8")

    print("AI Coder wrote files; a PR will be opened in the next step.")


if __name__ == "__main__":
    main()

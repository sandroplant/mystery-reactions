import os
import json
import re
from pathlib import Path

try:
    from openai import OpenAI
except Exception as e:
    raise SystemExit("OpenAI SDK missing: ensure tools/requirements.txt has openai>=1.40.0") from e

# ---- Config ---------------------------------------------------------------

MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o").strip()
TASK = os.environ.get("TASK", "").strip()
if not TASK:
    raise SystemExit("No TASK provided. Use the workflow input when running the action.")

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
    p = (p or "").strip().lstrip("./")
    if p.startswith("github/"):  # autocorrect common mistake
        p = "." + p
    path = Path(p)

    # TEMP: keep CI files under human control for now (optional allow-list later)
    if str(path).startswith(".github/workflows/"):
        raise ValueError(f"Path not allowed (workflows blocked for now): {p}")

    if ".." in path.parts:
        raise ValueError(f"Refusing path with '..': {p}")

    if path.parent == Path(".") and path.name in ALLOWED_ROOT_FILES:
        return path

    if not any(str(path).startswith(pref) for pref in SAFE_PREFIXES):
        raise ValueError(f"Path not allowed: {p}")

    return path


def extract_text_from_responses(resp) -> str:
    if hasattr(resp, "output_text") and isinstance(resp.output_text, str):
        return resp.output_text
    try:
        return resp.output[0].content[0].text.value  # type: ignore[attr-defined]
    except Exception:
        pass
    try:
        return resp.choices[0].message["content"]  # type: ignore[index]
    except Exception:
        pass
    raise SystemExit("Could not extract text from OpenAI Responses result. SDK format unexpected.")


def parse_single_json_object(s: str) -> dict:
    s_no_fences = re.sub(r"^```(?:json)?\s*|\s*```$", "", s.strip(), flags=re.I | re.M)
    try:
        return json.loads(s_no_fences)
    except Exception:
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

    # call model
    try:
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
    except Exception as e:
        # Log hard API errors directly
        Path("docs").mkdir(parents=True, exist_ok=True)
        Path("docs/AI_GENERATION_FAILED.md").write_text(
            f"# AI Generation Failed\n\n**TASK**\n\n```\n{TASK}\n```\n\n**Error**\n\n```\n{e}\n```",
            encoding="utf-8",
        )
        # ensure at least one change
        Path("tools").mkdir(parents=True, exist_ok=True)
        Path("tools/.ai-last-output.txt").write_text("API error; see docs/AI_GENERATION_FAILED.md\n", encoding="utf-8")
        print("AI API error; wrote docs/AI_GENERATION_FAILED.md")
        return

    # always save raw output for debugging
    Path("tools").mkdir(parents=True, exist_ok=True)
    Path("tools/.ai-last-output.txt").write_text(text, encoding="utf-8")

    # parse and write files
    wrote_files = 0
    try:
        spec = parse_single_json_object(text)
        files = spec.get("files", [])
        if not isinstance(files, list):
            raise SystemExit("AI JSON missing 'files' array.")

        for f in files:
            path_str = f.get("path", "")
            content = f.get("content", "")
            if not path_str:
                raise SystemExit("AI JSON has a file without 'path'.")
            path = ensure_safe_path(path_str)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(content)
            wrote_files += 1

        # helper docs for PR context
        Path("AI_PLAN.md").write_text(spec.get("plan", ""), encoding="utf-8")
        Path("PR_TITLE.txt").write_text(spec.get("pr_title", "AI update"), encoding="utf-8")
        Path("PR_BODY.md").write_text(spec.get("pr_body", ""), encoding="utf-8")

    except SystemExit as e:
        # Parsing/validation problem: write a visible report into docs/
        Path("docs").mkdir(parents=True, exist_ok=True)
        Path("docs/AI_GENERATION_FAILED.md").write_text(
            f"# AI Output Could Not Be Parsed\n\n**TASK**\n```\n{TASK}\n```\n\n**RAW OUTPUT**\n```\n{text}\n```\n\n**ERROR**\n```\n{e}\n```",
            encoding="utf-8",
        )
        wrote_files = 1  # we wrote a docs file so the PR has something to show

    # If the AI produced no files at all, drop a minimal placeholder to signal progress
    if wrote_files == 0:
        Path("docs").mkdir(parents=True, exist_ok=True)
        Path("docs/PLACEHOLDER.md").write_text(
            f"# Placeholder for TASK\n\n```\n{TASK}\n```\n\nThe AI returned no files. See tools/.ai-last-output.txt for raw output.",
            encoding="utf-8",
        )
        wrote_files = 1

    # Always ensure at least one changed file so the PR step has something to commit
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    marker = Path("tools") / (f".ai-run-{run_id}.txt" if run_id else ".ai-run-marker.txt")
    marker.write_text("ok\n", encoding="utf-8")

    print("AI Coder wrote files; a PR will be opened in the next step.")


if __name__ == "__main__":
    main()

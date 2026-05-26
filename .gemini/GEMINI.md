# 내 개발 환경 설정

## 공통 코딩 규약
- 모든 코드에 상세한 주석 포함
- JavaScript, css, html 만 사용
- 인라인 스타일 사용 금지
- 반응형 디자인 우선 (데스크톱 우선)
- shapespark 동작 우선 , 오류 없을시 다른 기능 구현
-  한국어로 간단 명료하게 대답해 줘


### Terminal & Execution Constraints
- DO NOT use global installation commands (e.g., `npm install -g`). Always install dependencies locally.
- If you need to run a PowerShell script (`.ps1`), always prefix the command with `PowerShell -ExecutionPolicy Bypass -File ...`.
- If a permission error occurs in PowerShell, fallback to running the command via `cmd /c`.

### Python Execution Rules
- Before running any Python script, always explicitly navigate to the target directory using `cd` (e.g., `cd src && python script.py`), or use the absolute workspace path.
- When generating Python code that handles file I/O, always use `os.path.abspath(__file__)` or `pathlib.Path` to ensure paths are resolved relative to the script location, preventing working directory mismatches.

# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
# tfm_comparison — notes for Claude Code

Comparison site of tabular foundation models at or above TabICLv2 on TabArena (page: `index.html`, data: `data/`).

- **Before changing anything, read `SESSION_SUMMARY.md`** (state, pipeline, the add-a-model checklist, research
  method, source registry) and `data/SCHEMA.md` (record format).
- Workflow: `bash scripts/fetch_tabarena.sh` → edit/add `data/models/<id>.json` (+ `data/talent.json`) →
  `python3 scripts/validate_models.py` → `python3 scripts/build.py` → preview with the "site" config in
  `.claude/launch.json` (http://localhost:8765).
- Never edit generated files (`data/compiled.*`, `data/tabarena.json`) by hand; never guess numbers (`null` + note).
- Deliverables stay local in this folder (no hosted artifacts unless asked).

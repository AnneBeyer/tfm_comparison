# Claude-generated tabular comparison of Tabular Foundation Models

A self-contained, sortable comparison page of every TabArena entry that scores at least as high as TabICLv2,
with model facts (architecture, pretraining, synthetic priors, ICL details, limits, speed/cost, licensing)
compiled from the papers, repositories and model cards, plus TabArena and TALENT benchmark numbers.

## Open the page

Open `index.html` in a browser (works from `file://`, no server needed), or serve the folder:

```bash
python3 -m http.server 8765 --directory /home/anne/Projects/tfm_comparison
```

## Layout

```
index.html                 the page (HTML + CSS + JS, no external dependencies; reads data/compiled.js)
data/
  SCHEMA.md                field-by-field definition of a model record
  models/<id>.json         one hand-curated record per model (the thing to edit / extend)
  tabarena.json            parsed leaderboard (all subsets, win-rate matrix, licenses) — generated
  talent.json              TALENT results compiled per source table (protocol-aware)
  compiled.js / .json      merged data consumed by index.html — generated, do not edit
  raw/                     leaderboard snapshots (CSV export from the TabArena Space, page text, version history)
scripts/
  fetch_tabarena.sh        download the current leaderboard CSVs and rebuild data/tabarena.json
  build_tabarena.py        CSV -> data/tabarena.json
  build.py                 models + tabarena + talent -> data/compiled.js
```

## Add or update a model

1. Create `data/models/<id>.json` following `data/SCHEMA.md` (copy an existing record as a template).
   Use `null` for unknown facts; numeric fields used for sorting must be plain numbers.
2. Set `tabarena_entry` to the exact row label on the leaderboard (e.g. `"NewModel (default)"`).
3. Refresh the leaderboard snapshot if needed: `scripts/fetch_tabarena.sh` (then update the
   `Current Version:` line in `data/raw/tabarena_version_history.md`).
4. Add TALENT numbers to `data/talent.json` (one table per source + protocol; results keyed by model id).
5. Rebuild: `python3 scripts/build.py` — it prints warnings for records that do not join to the leaderboard.
6. Reload `index.html`.

Columns in the table are generated from the column config at the top of the script in `index.html`
(`GROUPS`); the expanded fact sheet renders every field in the record generically, so new fields appear
without touching the page.

## Models not yet on the leaderboard

A record may carry an optional `tabarena_self_reported` block (see `data/SCHEMA.md`) with the authors' own
TabArena numbers. The page shows them in the TabArena columns marked with † and excludes the model from the
win-rate matrix and the timing scatter; as soon as `scripts/fetch_tabarena.sh` brings in an official row with the
same `tabarena_entry` label, the official numbers take over automatically (the build prints a note).
Previous example: NVIDIA Kumo Tabular (provisional from 2026-09-30 until its official rows appeared, 2026-10-07). No model is provisional at the moment.

## Selection rule

TabArena leaderboard, "Models only" view, all tasks, all datasets, all repeats, imputed and non-commercial
methods included: every entry with Elo >= TabICLv2 (default). RealTabPFN-2.5 qualifies through its
"tuned + ensembled" variant only.

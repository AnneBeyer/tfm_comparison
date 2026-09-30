#!/usr/bin/env python3
"""Merge data/models/*.json + data/tabarena.json + data/talent.json into data/compiled.js (and .json).

Usage:  python3 scripts/build.py
Add a model: drop data/models/<id>.json (see data/SCHEMA.md), make sure its "tabarena_entry" matches a
row label in data/tabarena.json (run scripts/fetch_tabarena.sh to refresh the leaderboard), then re-run.
"""
import glob, json, os, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.environ.get("TFM_MODELS_DIR", os.path.join(ROOT, "data", "models"))
TABARENA = os.path.join(ROOT, "data", "tabarena.json")
TALENT = os.path.join(ROOT, "data", "talent.json")
OUT_JS = os.environ.get("TFM_OUT_JS", os.path.join(ROOT, "data", "compiled.js"))
OUT_JSON = os.environ.get("TFM_OUT_JSON", os.path.join(ROOT, "data", "compiled.json"))

REQUIRED_TOP = ["id", "name", "tabarena_entry", "developer", "links", "availability", "license",
                "architecture", "capabilities", "pretraining", "icl", "speed", "benchmarks", "sources"]

def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def main():
    warnings = []
    notes = []
    tabarena = load_json(TABARENA, {"meta": {}, "entries": {}, "winrates": {}})
    talent = load_json(TALENT, {"benchmark": {}, "tables": [], "per_model_summary": {}, "sources": []})
    entries = tabarena.get("entries", {})
    winrates = tabarena.get("winrates", {})

    models = []
    for path in sorted(glob.glob(os.path.join(MODELS_DIR, "*.json"))):
        m = load_json(path)
        if not isinstance(m, dict):
            warnings.append(f"{os.path.basename(path)}: not a JSON object, skipped"); continue
        missing = [k for k in REQUIRED_TOP if k not in m]
        if missing:
            warnings.append(f"{m.get('id', os.path.basename(path))}: missing keys {missing}")
        if m.get("id") != os.path.splitext(os.path.basename(path))[0]:
            warnings.append(f"{path}: id '{m.get('id')}' does not match filename")

        # --- join TabArena --------------------------------------------------------------
        label = m.get("tabarena_entry")
        ta = entries.get(label)
        sr = m.get("tabarena_self_reported")
        if ta is not None:
            m["tabarena"] = ta
            base = ta["model"]
            m["tabarena_variants"] = [e for e in entries.values() if e["model"] == base]
            if sr:
                notes.append(f"{m.get('id')}: official TabArena row '{label}' found; the tabarena_self_reported block is now ignored and can be removed")
        elif sr and sr.get("elo") is not None:
            # provisional numbers from the authors until the official leaderboard row exists
            m["tabarena"] = {
                "provisional": True, "position": None, "label": label, "link": sr.get("source_url"),
                "model": m.get("name"), "variant": "default (self-reported)", "type": "Foundation Model", "type_icon": "🧠⚡",
                "elo": sr.get("elo"), "elo_ci": "", "score": None, "rank": None, "harmonic_rank": None, "improvability_pct": None,
                "train_time_s_per_1k": sr.get("train_time_s_per_1k"), "predict_time_s_per_1k": sr.get("predict_time_s_per_1k"),
                "verified": False, "imputed_pct": None, "hardware": sr.get("hardware"),
                "commercial": (m.get("license") or {}).get("commercial_use") == "yes",
                "license": (m.get("license") or {}).get("weights"),
                "status": sr.get("status"), "source_title": sr.get("source_title"), "source_url": sr.get("source_url"), "date": sr.get("date"),
                "elo_note": sr.get("elo_note"),
                "subsets": {"all": {"position": None, "elo": sr.get("elo"), "elo_ci": "", "score": None, "rank": None, "harmonic_rank": None, "improvability_pct": None, "imputed_pct": None}},
            }
            for k, v in (sr.get("subsets") or {}).items():
                if v is not None:
                    m["tabarena"]["subsets"][k] = {"position": None, "elo": v, "elo_ci": "", "score": None, "rank": None, "harmonic_rank": None, "improvability_pct": None, "imputed_pct": None}
            m["tabarena_variants"] = []
            notes.append(f"{m.get('id')}: no official TabArena row for '{label}'; using self-reported numbers (provisional)")
        else:
            warnings.append(f"{m.get('id')}: tabarena_entry '{label}' not found in tabarena.json")
            m["tabarena"] = None
        models.append(m)

    # win-rate sub-matrix among compared models
    labels = [m["tabarena_entry"] for m in models if m.get("tabarena") and not m["tabarena"].get("provisional")]
    # winrate matrix uses short labels like "RealTabPFN-2.5 (T+E)" for tuned + ensembled
    def wr_label(lbl):
        return lbl.replace("(tuned + ensembled)", "(T+E)").replace("(tuned)", "(T)")
    for m in models:
        if not m.get("tabarena"):
            continue
        if m["tabarena"].get("provisional"):
            m["tabarena_winrates"] = None
            continue
        row = winrates.get(wr_label(m["tabarena_entry"]), {})
        m["tabarena_winrates"] = {other: row.get(wr_label(other)) for other in labels if other != m["tabarena_entry"]}

    # --- TALENT: attach per-model rows -----------------------------------------------------
    talent_cols = []
    names = {m["id"]: m["name"] for m in models}
    for t in talent.get("tables", []):
        col = {k: t.get(k) for k in ("id", "source_title", "source_url", "source_date", "protocol",
                                     "metric", "higher_is_better", "task_scope", "num_datasets", "notes", "headline")}
        # short source label derived from the table id prefix, e.g. "mitra-v2-report-..." -> "Mitra-v2 report"
        tid = t.get("id", "")
        for kind in ("-report", "-paper", "-blog"):
            if kind in tid:
                prefix = tid.split(kind)[0]
                match = names.get(prefix) or next((n for i, n in names.items() if i.startswith(prefix)), prefix)
                col["source_short"] = match + kind.replace("-", " ")
                break
        else:
            col["source_short"] = (t.get("source_title") or tid)[:30]
        col["n_models"] = len([k for k in (t.get("results") or {}) if k in names])
        talent_cols.append(col)
    for m in models:
        m["talent"] = {}
        for t in talent.get("tables", []):
            v = (t.get("results") or {}).get(m["id"])
            if v is not None:
                m["talent"][t["id"]] = {"value": v, "note": (t.get("results_note") or {}).get(m["id"])}
        m["talent_summary"] = (talent.get("per_model_summary") or {}).get(m["id"])

    # order: by TabArena Elo desc, then name
    models.sort(key=lambda m: (-(m.get("tabarena") or {}).get("elo", -1e9) if m.get("tabarena") else 1e9, m["name"]))

    compiled = {
        "generated": datetime.datetime.now().isoformat(timespec="seconds"),
        "tabarena_meta": tabarena.get("meta", {}),
        "talent_meta": talent.get("benchmark", {}),
        "talent_tables": talent_cols,
        "talent_sources": talent.get("sources", []),
        "talent_raw": {t["id"]: {"results": t.get("results", {}), "results_note": t.get("results_note", {})} for t in talent.get("tables", [])},
        "models": models,
        "warnings": warnings,
        "notes": notes,
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(compiled, f, indent=1, ensure_ascii=False)
    with open(OUT_JS, "w", encoding="utf-8") as f:
        f.write("// Generated by scripts/build.py — do not edit by hand.\n")
        f.write("window.TFM_DATA = ")
        json.dump(compiled, f, ensure_ascii=False)
        f.write(";\n")
    print(f"compiled {len(models)} models -> {OUT_JS}")
    for n in notes:
        print("note:", n)
    for w in warnings:
        print("WARNING:", w)

if __name__ == "__main__":
    main()

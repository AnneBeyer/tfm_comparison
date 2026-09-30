#!/usr/bin/env python3
"""Parse the TabArena leaderboard CSV exports (data/raw/tabarena/*.csv) into data/tabarena.json.

Re-run after dropping a fresh set of CSVs into data/raw/tabarena/ (see scripts/fetch_tabarena.sh).
The CSVs come from the TabArena Space repo:
  https://huggingface.co/spaces/TabArena/leaderboard/tree/main/data/entrants_models/imputation_yes/splits_all/...
"""
import csv, json, re, glob, os, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw", "tabarena")
OUT = os.path.join(ROOT, "data", "tabarena.json")

SUBSETS = {  # key -> (csv suffix, label, n_datasets)
    "all":            ("tasks_all_datasets_all", "All tasks, all datasets", 51),
    "classification": ("tasks_classification_datasets_all", "Classification", 38),
    "regression":     ("tasks_regression_datasets_all", "Regression", 13),
    "binary":         ("tasks_binary_datasets_all", "Binary classification", 30),
    "multiclass":     ("tasks_multiclass_datasets_all", "Multiclass classification", 8),
    "small":          ("tasks_all_datasets_small", "Small datasets", 36),
    "medium":         ("tasks_all_datasets_medium", "Medium datasets", 15),
    "balanced":       ("tasks_all_datasets_balanced", "Balanced targets", 36),
    "imbalanced":     ("tasks_all_datasets_imbalanced", "Imbalanced targets", 15),
    "extreme":        ("tasks_all_datasets_extreme", "Extremely imbalanced targets", 5),
}

COLS = {
    "elo": "Elo [⬆️]", "elo_ci": "Elo 95% CI", "score": "Score [⬆️]", "rank": "Rank [⬇️]",
    "harmonic_rank": "Harmonic Rank [⬇️]", "improvability_pct": "Improvability (%) [⬇️]",
    "train_time_s_per_1k": "Median Train Time (s/1K) [⬇️]", "predict_time_s_per_1k": "Median Predict Time (s/1K) [⬇️]",
    "verified": "Verified", "imputed_pct": "Imputed (%) [⬇️]", "hardware": "Hardware",
    "commercial": "Commercial", "license": "License", "type_name": "TypeName", "type_icon": "Type",
}

def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None

def parse_model(cell):
    m = re.match(r"\[(.+?)\]\((.+?)\)", cell)
    label, link = (m.group(1), m.group(2)) if m else (cell, None)
    m2 = re.match(r"(.+?) \((.+)\)$", label)
    base, variant = (m2.group(1), m2.group(2)) if m2 else (label, "default")
    return label, link, base, variant

def read(subset_suffix):
    path = os.path.join(RAW, f"website_leaderboard__{subset_suffix}.csv")
    if not os.path.exists(path):
        return {}
    out = {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            label, link, base, variant = parse_model(r["Model"])
            out[label] = {
                "position": int(r["#"]) + 1,
                "label": label, "link": link, "model": base, "variant": variant,
                "type": r.get(COLS["type_name"]), "type_icon": r.get(COLS["type_icon"]),
                "elo": num(r[COLS["elo"]]), "elo_ci": r[COLS["elo_ci"]],
                "score": num(r[COLS["score"]]), "rank": num(r[COLS["rank"]]),
                "harmonic_rank": num(r[COLS["harmonic_rank"]]),
                "improvability_pct": num(r[COLS["improvability_pct"]]),
                "train_time_s_per_1k": num(r[COLS["train_time_s_per_1k"]]),
                "predict_time_s_per_1k": num(r[COLS["predict_time_s_per_1k"]]),
                "verified": r[COLS["verified"]].strip() == "✔️",
                "imputed_pct": num(r[COLS["imputed_pct"]]),
                "hardware": r[COLS["hardware"]],
                "commercial": r[COLS["commercial"]].strip().lower() == "true",
                "license": r[COLS["license"]],
            }
    return out

def main():
    overall = read(SUBSETS["all"][0])
    entries = {}
    for label, row in overall.items():
        e = dict(row)
        e["subsets"] = {}
        entries[label] = e
    for key, (suffix, name, n) in SUBSETS.items():
        rows = read(suffix)
        for label, row in rows.items():
            if label not in entries:
                continue
            entries[label]["subsets"][key] = {k: row[k] for k in ("position", "elo", "elo_ci", "score", "rank", "harmonic_rank", "improvability_pct", "imputed_pct")}

    # pairwise win-rate matrix (row beats column), all-tasks/all-datasets
    winrates = {}
    wr_path = os.path.join(RAW, "winrate_matrix__tasks_all_datasets_all.csv")
    if os.path.exists(wr_path):
        with open(wr_path, newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))
        hdr = rows[0][1:]
        for r in rows[1:]:
            winrates[r[0]] = {h: num(v) for h, v in zip(hdr, r[1:]) if v != ""}

    version = None
    vh = os.path.join(ROOT, "data", "raw", "tabarena_version_history.md")
    if os.path.exists(vh):
        m = re.search(r"Current Version:\s*(\S+)", open(vh, encoding="utf-8").read())
        version = m.group(1) if m else None

    data = {
        "meta": {
            "benchmark": "TabArena",
            "version": version,
            "retrieved": datetime.date.today().isoformat(),
            "url": "https://huggingface.co/spaces/TabArena/leaderboard",
            "csv_source": "https://huggingface.co/spaces/TabArena/leaderboard/tree/main/data/entrants_models/imputation_yes/splits_all",
            "view": "Models only · all repeats · with imputation",
            "elo_note": "Pairwise win-rate rating; a 400-point gap ≈ 91% win rate. Elo is relative to the field of the selected leaderboard (models only, non-commercial included).",
            "subsets": {k: {"label": v[1], "n_datasets": v[2]} for k, v in SUBSETS.items()},
        },
        "entries": entries,
        "winrates": winrates,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
    print(f"wrote {OUT}: {len(entries)} entries, {len(winrates)} win-rate rows, version {version}")

if __name__ == "__main__":
    main()

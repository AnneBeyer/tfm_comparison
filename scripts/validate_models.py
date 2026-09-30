#!/usr/bin/env python3
"""Validate data/models/*.json against data/SCHEMA.md conventions, check the TabArena join and data/talent.json.

Usage:  python3 scripts/validate_models.py        (exit code 1 if any record has problems)
"""
import glob, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = {
    "top": ["id", "name", "tabarena_entry", "family", "developer", "organization_type", "release_date", "paper_title",
            "links", "availability", "license", "architecture", "capabilities", "pretraining", "icl", "speed",
            "benchmarks", "differences_vs_predecessor", "sources", "notes"],
    "links": ["paper", "code", "weights", "docs", "pypi", "tabarena_pr"],
    "availability": ["open_weights", "local_inference", "hosted_api", "training_code_released", "prior_code_released", "notes"],
    "license": ["code", "weights", "prior_or_data", "commercial_use", "non_commercial_use", "notes"],
    "architecture": ["type", "parameters_m", "parameters_note", "layers", "embedding_dim", "attention_heads",
                     "attention_scheme", "checkpoints", "regression_head", "feature_embedding", "key_innovations"],
    "capabilities": ["classification", "regression", "max_classes", "max_classes_note", "max_features", "max_features_note",
                     "max_samples", "max_samples_note", "missing_values", "categorical_features", "text_features", "other"],
    "pretraining": ["data_type", "synthetic_prior_summary", "synthetic_prior_types", "num_synthetic_datasets",
                    "num_synthetic_datasets_note", "real_data", "objective", "optimizer", "training_steps", "batch_size",
                    "hardware", "compute", "training_cost_note", "curriculum"],
    "icl": ["max_context_rows", "context_note", "large_dataset_strategy", "test_time_ensembling", "fine_tuning", "inference_notes"],
    "speed": ["hardware_note", "memory_note", "speed_claims", "inference_cost_note"],
}
NUMERIC = [("architecture", "parameters_m"), ("capabilities", "max_classes"), ("capabilities", "max_features"),
           ("capabilities", "max_samples"), ("pretraining", "num_synthetic_datasets"), ("icl", "max_context_rows")]
ENUMS = {"commercial_use": {"yes", "no", "restricted", "unknown"}, "non_commercial_use": {"yes", "no", "restricted", "unknown"},
         "organization_type": {"academic", "company", "mixed"}}

def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def check_record(path, tabarena_entries):
    problems = []
    m = load(path)
    if m.get("id") != os.path.splitext(os.path.basename(path))[0]:
        problems.append(f"id '{m.get('id')}' != filename")
    for section, keys in SCHEMA.items():
        obj = m if section == "top" else m.get(section)
        if not isinstance(obj, dict):
            problems.append(f"missing section {section}"); continue
        problems += [f"missing {section + '.' if section != 'top' else ''}{k}" for k in keys if k not in obj]
    for sec, k in NUMERIC:
        v = (m.get(sec) or {}).get(k)
        if v is not None and not isinstance(v, (int, float)):
            problems.append(f"{sec}.{k} must be a number or null, got {v!r}")
    for k, allowed in ENUMS.items():
        v = (m.get("license") or {}).get(k) if k != "organization_type" else m.get(k)
        if v not in allowed:
            problems.append(f"{k}={v!r} not in {sorted(allowed)}")
    t = (m.get("benchmarks") or {}).get("talent") or {}
    for k in ("avg_rank", "elo"):
        if t.get(k) is not None and not isinstance(t[k], (int, float)):
            problems.append(f"benchmarks.talent.{k} must be numeric")
    if not m.get("sources"):
        problems.append("no sources")
    rd = m.get("release_date") or ""
    if len(rd) != 10 or rd[4] != "-" or rd[7] != "-":
        problems.append(f"release_date '{rd}' is not YYYY-MM-DD")
    label = m.get("tabarena_entry")
    sr = m.get("tabarena_self_reported")
    if label in tabarena_entries:
        join = "official"
        if sr: join += " (self-reported block present but ignored — remove it)"
    elif sr and isinstance(sr.get("elo"), (int, float)):
        join = "PROVISIONAL (self-reported)"
    else:
        join = "NOT FOUND"; problems.append(f"tabarena_entry '{label}' not in data/tabarena.json and no tabarena_self_reported block")
    return m, join, problems

def main():
    tabarena = load(os.path.join(ROOT, "data", "tabarena.json")) if os.path.exists(os.path.join(ROOT, "data", "tabarena.json")) else {"entries": {}}
    entries = tabarena.get("entries", {})
    bad = 0
    print(f"{'file':24} {'released':10} {'params':>7} {'feats':>6} {'samples':>9} {'cls':>4} {'comm':>5} {'TabArena join':30}")
    ids = set()
    for path in sorted(glob.glob(os.path.join(ROOT, "data", "models", "*.json"))):
        try:
            m, join, problems = check_record(path, entries)
        except Exception as e:  # noqa: BLE001
            print(f"{os.path.basename(path):24} INVALID JSON: {e}"); bad += 1; continue
        ids.add(m.get("id"))
        a, c = m.get("architecture", {}), m.get("capabilities", {})
        print(f"{os.path.basename(path):24} {str(m.get('release_date')):10} {str(a.get('parameters_m')):>7} {str(c.get('max_features')):>6} "
              f"{str(c.get('max_samples')):>9} {str(c.get('max_classes')):>4} {str(m.get('license', {}).get('commercial_use')):>5} {join:30}")
        for p in problems:
            print("    PROBLEM:", p); bad += 1
    tp = os.path.join(ROOT, "data", "talent.json")
    if os.path.exists(tp):
        t = load(tp)
        tables = t.get("tables", [])
        seen = set()
        for tb in tables:
            if tb["id"] in seen:
                print("    PROBLEM: duplicate talent table id", tb["id"]); bad += 1
            seen.add(tb["id"])
            for k, v in (tb.get("results") or {}).items():
                if not isinstance(v, (int, float)):
                    print(f"    PROBLEM: talent table {tb['id']} result {k} not numeric"); bad += 1
        missing = sorted(i for i in ids if not any(i in (tb.get("results") or {}) for tb in tables))
        print(f"\ntalent.json: {len(tables)} tables, {sum(1 for tb in tables if tb.get('headline'))} headline; models without any TALENT number: {missing or 'none'}")
    print("\nOK" if not bad else f"\n{bad} problem(s)")
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()

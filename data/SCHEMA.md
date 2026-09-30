# Model record schema (one JSON file per model in data/models/<id>.json)

Every model record is a JSON object with the fields below. Use `null` for anything you could not verify
(never guess numbers). Every numeric field intended for sorting must be a plain number (no units, no strings).
Free-text fields hold short, dense prose or a list of bullet strings. Always cite where a fact came from in
`sources` (URL + title) and reference the source index in the `notes` field when helpful.

```json
{
  "id": "tabiclv2",                          // stable lowercase slug, used as filename
  "name": "TabICLv2",                         // display name
  "tabarena_entry": "TabICLv2 (default)",     // exact row label on the TabArena leaderboard (used to join the benchmark numbers)
  "family": "TabICL",                         // model family / lineage
  "developer": "Inria Soda (Qu, Holzmüller, Varoquaux, Le Morvan)",
  "organization_type": "academic | company | mixed",
  "release_date": "2026-02-11",               // ISO date of the model/paper release
  "paper_title": "...",
  "links": {
    "paper": "https://arxiv.org/abs/...",
    "code": "https://github.com/...",
    "weights": "https://huggingface.co/...",
    "docs": null,
    "pypi": null,
    "tabarena_pr": null                       // PR that added the model to TabArena, if known
  },
  "availability": {
    "open_weights": true,                     // weights downloadable
    "local_inference": true,
    "hosted_api": false,
    "training_code_released": true,
    "prior_code_released": true,              // synthetic data generator released
    "notes": "..."
  },
  "license": {
    "code": "BSD-3-Clause",                   // SPDX id or license name of the code repo
    "weights": "...",                         // license of the checkpoints
    "prior_or_data": "...",                   // license of the synthetic-data generator / training data if separate
    "commercial_use": "yes | no | restricted | unknown",   // for the WEIGHTS (what matters to a user)
    "non_commercial_use": "yes | no | restricted | unknown",
    "notes": "e.g. research-only license, attribution requirement, share-alike, API terms"
  },
  "architecture": {
    "type": "...",                            // e.g. "column-then-row ICL transformer", "2D (row+column) attention transformer", "MoE"
    "parameters_m": 100.0,                    // total parameters in millions (number). If separate class/regr checkpoints, give the classifier and put both in parameters_note
    "parameters_note": "...",
    "layers": "...",                          // e.g. "3 column + 3 row + 12 ICL layers"
    "embedding_dim": null,
    "attention_heads": null,
    "attention_scheme": "...",                // how attention is organised over rows/columns, any special attention (e.g. scalable softmax)
    "checkpoints": "single multitask | separate classification & regression | ...",
    "regression_head": "...",                 // e.g. "distributional, 5000 bins (Riemann)" or "point"
    "feature_embedding": "...",               // how cells/columns are embedded
    "key_innovations": ["...", "..."]        // bullet list of what is new vs. prior work / predecessor
  },
  "capabilities": {
    "classification": true,
    "regression": true,
    "max_classes": 10,                        // number or null
    "max_classes_note": "...",
    "max_features": 500,                      // documented/recommended limit as number, null if no hard limit
    "max_features_note": "...",
    "max_samples": 100000,                    // documented/recommended limit as number, null if no hard limit
    "max_samples_note": "...",
    "missing_values": "native | preprocessing | unsupported",
    "categorical_features": "...",
    "text_features": false,
    "other": "..."                            // e.g. imputation, quantile outputs, embeddings, multi-target
  },
  "pretraining": {
    "data_type": "synthetic only | synthetic + real | real only",
    "synthetic_prior_summary": "...",         // dense description of the synthetic data generation engine
    "synthetic_prior_types": ["SCM", "tree", "GP", "..."],
    "num_synthetic_datasets": null,           // number if stated (e.g. 1.3e8), else null
    "num_synthetic_datasets_note": "...",
    "real_data": "...",                       // real data used in pretraining/fine-tuning, or "none"
    "objective": "...",                        // e.g. cross-entropy on masked targets, CCMM
    "optimizer": "...",
    "training_steps": "...",
    "batch_size": "...",
    "hardware": "...",                         // e.g. "8x H100"
    "compute": "...",                          // GPU-hours or days if stated
    "training_cost_note": "...",
    "curriculum": "..."                        // e.g. context-length curriculum
  },
  "icl": {
    "max_context_rows": null,                  // rows the model can attend to in one pass (number or null)
    "context_note": "...",
    "large_dataset_strategy": "...",            // subsampling, kNN retrieval, bagging, chunking, memory-efficient attention...
    "test_time_ensembling": "...",              // default number of estimators / augmentations
    "fine_tuning": "...",                       // supported? how?
    "inference_notes": "..."
  },
  "speed": {
    "hardware_note": "...",                     // GPU used for reported numbers
    "memory_note": "...",
    "speed_claims": "...",                      // any claims from the paper (e.g. "x faster than ...")
    "inference_cost_note": "..."                // e.g. API pricing, if applicable
  },
  "benchmarks": {
    "talent": {
      "reported": true,
      "source": "...",                          // paper/URL that reports the number
      "protocol_note": "...",                   // number of datasets, subset, metric
      "avg_rank": null,                         // number if reported
      "elo": null,                              // number if reported
      "win_rate_vs": "...",                     // e.g. "62% vs RealTabPFN-2.5"
      "other": "..."
    },
    "other": [                                   // any other benchmark numbers worth showing
      {"name": "BeyondArena", "value": "...", "source": "..."}
    ]
  },
  "differences_vs_predecessor": "...",          // what changed from the previous version (e.g. TabPFN-3.5 vs TabPFN-3)
  "sources": [
    {"title": "...", "url": "..."}
  ],
  "notes": "..."
}
```

TabArena benchmark numbers (Elo, fit/infer times) are NOT stored in the model records; they live in
`data/tabarena.json`, joined by `tabarena_entry` at build time, so a new leaderboard snapshot can be dropped in.

## Optional: models not yet on the official leaderboard

If a model has no row in `data/tabarena.json` yet (e.g. a TabArena pull request is still open), add an optional
`tabarena_self_reported` block. The build then shows these numbers in the TabArena columns marked as provisional (†)
and drops them automatically as soon as an official row with the same `tabarena_entry` label appears.

```json
"tabarena_self_reported": {
  "status": "why there is no official row yet, with date",
  "source_title": "...", "source_url": "...", "date": "YYYY-MM-DD",
  "elo": 1950,                          // number; the authors' own TabArena Elo
  "elo_note": "which size / setup / field this Elo was computed against",
  "train_time_s_per_1k": null,          // number or null
  "predict_time_s_per_1k": null,        // number or null
  "hardware": "...",
  "subsets": {"classification": null, "regression": null}   // optional per-subset Elo, same keys as tabarena.json
}
```

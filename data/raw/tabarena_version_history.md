# TabArena leaderboard version history (copied 2026-09-23, updated 2026-09-30 from https://tabarena-leaderboard.hf.space, Appendix > Version History)
Current Version: TabArena-v0.1.9.3

2026/09/28-v0.1.9.3:
  - Updated verified model: Linear, re-run with L1 regularization applied to classification (tuned/ensembled Linear rows gain Elo; default unchanged). Other models' Elo shift by 1-2 points as a consequence.
  - BeyondArena: add nine foundation models (TabPFN-3.5, TabPFN-3.5-Fast, Causilo, LimiX-2, TabFM, EXAONE-Tabular, RealTabPFN-2.5, TabDPT-1.3, TabSwift) and the Linear re-run; new BeyondArena layout; per-page links (?tab=...).
  - NOTE (2026-09-30): NVIDIA Kumo Tabular (large/medium/small) is NOT on the leaderboard yet; TabArena PR #625 (opened 2026-09-28) is open with maintainer runs in progress.

2026/09/22-v0.1.9.2: Add new verified model: TabDPT-1.3 (replaces TabDPT-Turbo as installable TabDPT version; TabDPT-Turbo entry stays).
2026/09/18-v0.1.9.1: CatBoost back on its previous run (July 2026); per-dataset trajectory fixes; metric selector fix.
2026/09/17-v0.1.9:
  - Updated verified models: Causilo, Mitra-v2, Xiaomi-TabLDM, TabFM, TabICLv2, EXAONE-Tabular, TabPFN-3 and Nori-30M, re-run under the new timing pipeline. Train and predict times no longer include one-off warm-up (library imports, CUDA context, checkpoint loading); median train times of foundation models drop 2-4x; Elo unchanged within CIs. Updated unverified model: TabSwift.
  - Add new verified models: TabPFN-3.5 and TabPFN-3.5-Fast. Fit times re-measured without tabpfn's preprocessing worker pool (whose start-up added 15-20 s to every fit of the first run).
  - Updated verified model: CatBoost (default + 200 random configs on every split).
  - New balanced / imbalanced / extreme dataset subsets (classification: class ratio largest:smallest, imbalanced from 10:1, extreme from 50:1; regression: target skewness).
  - Every method now declares its license and whether it permits commercial use. New "Include non-commercial methods" toggle; the table marks them with $.
2026/09/10-v0.1.8.3: BeyondArena size-subset bucketing fix.
2026/08/17-v0.1.8.2: Performance-across-leaderboards table has a row per variant; fixed Fit/Infer columns to report the variant on the row.
2026/08/10-v0.1.8.1: ChimeraBoost 0.30.0.
2026/08/06-v0.1.8: Per-dataset results; Systems as own entrant class (AutoGluon, TabFM+, agents, hosted APIs); "Who's competing?" control (Models-only default); AutoGluon 1.6 systems; TabFM+ system.
2026/08/03-v0.1.7.1: Add new verified model: EXAONE-Tabular (classification only at that time; regression results imputed).
2026/07/31-v0.1.7: MCP server; every published leaderboard readable as plain CSV from the Space repo; interactive full table.
2026/07/21-v0.1.6 / v0.1.5.5 (Nori-30M) / v0.1.5.4 (TabDPT-Turbo; improved time measurement for CatBoost, ChimeraBoost, EBM, ExtraTrees, Nori, TabFM, TabICLv2, TabPFN-3, TabSwift).
2026/07/10-v0.1.5.3: TabSwift (unverified). 2026/07/08-v0.1.5.2: TabFM (verified). 2026/06/30-v0.1.5.1: Nori, ChimeraBoost.
2026/06/22-v0.1.5: New leaderboard UI.
2026/06/02-v0.1.4: Add TabPFN-3, iLTM (verified); OrionMSP (unverified); LimiX now runs on all datasets.
2026/03/25-v0.1.3.1: Add TabPFN-2.6.
2026/03/24-v0.1.3: Add TabICLv2, TabSTAR, PerpetualBooster; AutoGluon 1.5; Binary/Multiclass views.
2025/12/11-v0.1.2.2: SAP-RPT-OSS (unverified).
2025/11/22-v0.1.2: NeurIPS 2025 version; add Mitra, xRFM, RealTabPFN-v2.5 (verified); TabFlex, BetaTabPFN, LimiX (unverified).
2025/06/13-v0.1.1; 2025/05-v0.1.0: initial.

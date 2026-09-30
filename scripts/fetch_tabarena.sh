#!/usr/bin/env bash
# Download the current TabArena leaderboard CSV exports into data/raw/tabarena/ and rebuild data/tabarena.json.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p data/raw/tabarena
base="https://huggingface.co/spaces/TabArena/leaderboard/resolve/main/data/entrants_models/imputation_yes/splits_all"
for combo in "tasks_all/datasets_all" "tasks_all/datasets_small" "tasks_all/datasets_medium" "tasks_all/datasets_balanced" \
             "tasks_all/datasets_imbalanced" "tasks_all/datasets_extreme" "tasks_classification/datasets_all" \
             "tasks_regression/datasets_all" "tasks_binary/datasets_all" "tasks_multiclass/datasets_all"; do
  name=$(echo "$combo" | tr '/' '_')
  curl -sfL "$base/$combo/website_leaderboard.csv" -o "data/raw/tabarena/website_leaderboard__${name}.csv"
done
curl -sfL "$base/tasks_all/datasets_all/winrate_matrix.csv" -o data/raw/tabarena/winrate_matrix__tasks_all_datasets_all.csv
curl -sfL "$base/tasks_all/datasets_all/pareto_front_points.csv" -o data/raw/tabarena/pareto_front_points__tasks_all_datasets_all.csv
echo "Downloaded CSVs. NOTE: update 'Current Version:' in data/raw/tabarena_version_history.md from the leaderboard's Version History."
python3 scripts/build_tabarena.py

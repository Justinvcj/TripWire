.PHONY: setup train-baseline tune-thresholds eval full-eval

setup:
	pip install -r requirements.txt

train-baseline:
	python evaluation/train_baseline2.py

tune-thresholds:
	python evaluation/tune_thresholds.py

eval:
	python evaluation/run_eval.py

full-eval: eval
	python evaluation/compute_metrics.py
	python evaluation/ablation_rag.py
	python evaluation/judge_sycophancy_probe.py

all: train-baseline tune-thresholds full-eval

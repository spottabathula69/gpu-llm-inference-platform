SHELL := /bin/bash

.PHONY: help setup deploy benchmark benchmark-stress report clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Start Minikube with GPU support and wait for it
	minikube start --driver=docker --container-runtime=docker --gpus=all
	kubectl wait --for=condition=ready node --all --timeout=60s
	@echo "Cluster is ready. Run 'make deploy' next."

deploy: ## Deploy vLLM to the cluster
	kubectl apply -f infra/k8s/apps/vllm/deployment.yaml
	@echo "Deployment applied. Waiting for pod to be ready..."
	kubectl wait --for=condition=ready pod -l app=vllm --timeout=300s
	@echo "vLLM is Ready!"

benchmark: ## Run standard performance sweep (c=1..16, Short+Long)
	@echo "Running Standard Benchmark Sweep..."
	./loadtest/run_k8s_sweep.sh

benchmark-stress: ## Run high-concurrency stress test (c=20..64)
	@echo "Running Stress Test (Long Payload)..."
	./loadtest/run_stress_test.sh

report: ## Generate performance reports from logs
	@echo "Generating Standard Report..."
	python3 scripts/analyze_results.py --k6-dir loadtest/logs/k6 --gpu-dir loadtest/logs/gpu --output docs/load_test_report.md
	@echo "Generating Stress Test Report..."
	python3 scripts/analyze_results.py --k6-dir loadtest/logs/stress --gpu-dir loadtest/logs/gpu_stress --output docs/stress_test_report.md

clean: ## Remove all benchmark logs
	rm -rf loadtest/logs/k6/* loadtest/logs/gpu/*
	rm -rf loadtest/logs/stress/* loadtest/logs/gpu_stress/*
	@echo "Logs cleaned."

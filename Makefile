# Wszystko, czego potrzebujesz na warsztacie. `make help` pokazuje listę.
.PHONY: help klaster setup doctor lekcja klucz a2a wyslij port-forward hala test route agents-md

help:
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  make %-14s %s\n", $$1, $$2}'

klaster: ## Postaw klaster fabryki: kind + Argo Workflows + kagent + Kyverno + Jaeger (idempotentne)
	@scripts/klaster.sh

setup: ## Zbuduj obrazy fabryki, załaduj do kind, wdróż warsztat (dysk, magazyn, serwer MCP, wykonawca)
	@scripts/obrazy.sh
	@kubectl apply -f platforma/warsztat/pvc.yaml -f platforma/warsztat/magazyn.yaml -f platforma/warsztat/mcpserver.yaml >/dev/null
	@kubectl apply -f platforma/kagent/agent-przyjecie.yaml -f platforma/kagent/agent-wykonawca.yaml >/dev/null
	@kubectl rollout status -n fabryka deploy/magazyn --timeout=120s >/dev/null
	@kubectl wait --for=condition=Ready mcpserver/warsztat -n fabryka --timeout=180s >/dev/null
	@kubectl wait --for=condition=Ready agent/wykonawca -n fabryka --timeout=180s >/dev/null
	@scripts/wyslij.sh
	@echo "Warsztat gotowy: make a2a A=wykonawca T=\"Wypisz moduły w system/\""

wyslij: ## Wyślij snapshot repo do klastra (/work/repo w magazynie)
	@scripts/wyslij.sh

doctor: ## Sprawdź, czy wszystko działa (lokalnie i w klastrze)
	@scripts/doctor.sh

lekcja: ## Przeskocz do lekcji: make lekcja N=4
	@scripts/lekcja.sh $(N)

klucz: ## Ustaw klucz do modelu (Secret fabryka-llm) i zrestartuj agentów
	@. scripts/workshop.env; read -rsp "LLM_API_KEY: " k; echo; \
	kubectl create secret generic fabryka-llm -n fabryka --from-literal=LLM_API_KEY="$$k" --dry-run=client -o yaml | kubectl apply -f - >/dev/null; \
	LLM_MODEL="$$LLM_MODEL" LLM_BASE_URL="$$LLM_BASE_URL" envsubst < platforma/kagent/modelconfig.yaml | kubectl apply -f - >/dev/null; \
	kubectl rollout restart deploy -n fabryka -l app=kagent >/dev/null 2>&1 || true; \
	echo "Model: $$LLM_MODEL przez $$LLM_BASE_URL"

a2a: ## Zapytaj agenta przez A2A: make a2a A=probny T="Przedstaw się"
	@python3 sdlc/a2a.py --agent "$(A)" --task "$(T)"

port-forward: ## Gdyby porty z kind.yaml nie działały: port-forward do kagent (8083) i Argo (2746)
	@kubectl port-forward -n kagent svc/kagent-controller 8083:8083 & kubectl port-forward -n argo svc/argo-server 2746:2746 & wait

hala: ## Otwórz halę (Argo UI), dashboard kagent i Jaegera w przeglądarce
	@open https://localhost:2746 http://localhost:8082 http://localhost:16686 2>/dev/null || echo "https://localhost:2746  http://localhost:8082  http://localhost:16686"

test: ## Build i testy systemu (z regułami ArchUnit)
	cd system && mvn -B -q verify

route: ## Routing lokalnie: make route T="Rabat 10% powyżej 500 zł"
	@python3 sdlc/context.py route --title "$(T)" --body "$(B)"

agents-md: ## Przebuduj AGENTS.md ze źródeł (module.json, docs, ops, historia)
	@python3 sdlc/context.py agents-md

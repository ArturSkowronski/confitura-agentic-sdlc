# Wszystko, czego potrzebujesz na warsztacie. `make help` pokazuje listę.
.PHONY: help klaster setup linia doctor lekcja klucz a2a wyslij zlecenie replay naiwna odbierz zatwierdz port-forward hala test route agents-md przyjecie

help:
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  make %-14s %s\n", $$1, $$2}'

klaster: ## Postaw klaster fabryki: kind + Argo Workflows + kagent + Kyverno + Jaeger (idempotentne)
	@scripts/klaster.sh

setup: ## Zbuduj obrazy fabryki, załaduj do kind, wdróż warsztat (dysk, magazyn, serwer MCP, wykonawca) i linię
	@scripts/obrazy.sh
	@kubectl apply -f platforma/linia/ >/dev/null
	@kubectl apply -f platforma/warsztat/pvc.yaml -f platforma/warsztat/magazyn.yaml -f platforma/warsztat/mcpserver.yaml >/dev/null
	@kubectl apply -f platforma/kagent/agent-przyjecie.yaml -f platforma/kagent/agent-wykonawca.yaml -f platforma/kagent/agent-recenzent.yaml >/dev/null
	@kubectl rollout status -n fabryka deploy/magazyn --timeout=120s >/dev/null
	@kubectl wait --for=condition=Ready mcpserver/warsztat -n fabryka --timeout=180s >/dev/null
	@kubectl wait --for=condition=Ready agent/wykonawca -n fabryka --timeout=180s >/dev/null
	@scripts/wyslij.sh
	@echo "Warsztat gotowy: make a2a A=wykonawca T=\"Wypisz moduły w system/\""

linia: ## Wdróż linię (WorkflowTemplate fabryka + konto) do klastra
	@kubectl apply -f platforma/linia/ >/dev/null && echo "linia wdrożona: kubectl get workflowtemplate -n fabryka"

zlecenie: ## Wyślij zlecenie na linię: make zlecenie Z=rabat [AGENT=replay]
	@scripts/zlecenie.sh $(Z) $(AGENT)

replay: ## Zlecenie bez modelu (nagrana zmiana): make replay Z=rabat
	@scripts/zlecenie.sh $(Z) replay

naiwna: ## Naiwna zmiana od człowieka: rabat policzony w OrderService (lekcja 6), przez bramki
	@REPLAY_MODULE=orders-service scripts/zlecenie.sh rabat replay

zatwierdz: ## Akceptacja człowieka: make zatwierdz W=<przebieg> (argo list -n fabryka)
	@scripts/zatwierdz.sh $(W) $(KTO)

odbierz: ## Odbierz wyniki z klastra do .sdlc/out/
	@scripts/odbierz.sh

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
	@open http://localhost:2746 http://localhost:8082 http://localhost:16686 2>/dev/null || echo "http://localhost:2746  http://localhost:8082  http://localhost:16686"

test: ## Build i testy systemu (z regułami ArchUnit)
	cd system && mvn -B -q verify

route: ## Routing lokalnie: make route T="Rabat 10% powyżej 500 zł"
	@python3 sdlc/context.py route --title "$(T)" --body "$(B)"

przyjecie: ## Przyjęcie zlecenia lokalnie (routing + kryteria + pytania agenta): make przyjecie Z=anulowanie
	@python3 sdlc/context.py route --title "$$(python3 sdlc/zlecenia.py $(Z) --title)" --body "$$(python3 sdlc/zlecenia.py $(Z) --body)" >/dev/null 2>&1
	@python3 sdlc/intake.py --title "$$(python3 sdlc/zlecenia.py $(Z) --title)" --body "$$(python3 sdlc/zlecenia.py $(Z) --body)" 2>/dev/null

agents-md: ## Przebuduj AGENTS.md ze źródeł (module.json, docs, ops, historia)
	@python3 sdlc/context.py agents-md

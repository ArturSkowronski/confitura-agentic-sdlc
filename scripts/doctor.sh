#!/usr/bin/env bash
# Sprawdza, czy wszystko jest gotowe. Zielone = przychodzisz na warsztat i nie tracisz 20 minut.
set -uo pipefail
cd "$(dirname "$0")/.."
. scripts/workshop.env
ok=0
pass() { printf '  \033[32m✔\033[0m %s\n' "$*"; }
fail() { printf '  \033[31m✘\033[0m %s\n' "$*"; ok=1; }
ver() { "$1" "${@:2}" 2>&1 | head -12 | grep -oE 'v?[0-9]+\.[0-9]+(\.[0-9]+)?' | head -1; }

echo "Lokalnie"
for t in git docker kind kubectl helm argo cosign python3; do
  command -v "$t" >/dev/null && pass "$t $(ver "$t" version 2>&1 || ver "$t" --version 2>&1)" || fail "brak $t (zob. SETUP.md)"
done
command -v java >/dev/null && java -version 2>&1 | grep -qE '"(2[1-9]|[3-9][0-9])' && pass "java 21+" || fail "java 21+ (potrzebna do make test i make oracle)"
command -v mvn >/dev/null && pass "mvn $(ver mvn --version)" || fail "brak mvn"
docker info >/dev/null 2>&1 && pass "docker działa" || fail "docker nie działa"
python3 sdlc/context.py route --title "Rabat 10% powyżej 500 zł" --body "doctor" >/dev/null 2>&1 \
  && pass "mózg fabryki (sdlc/) działa lokalnie" || fail "python3 sdlc/context.py route nie działa"

echo "Klaster $KIND_CLUSTER"
kind get clusters 2>/dev/null | grep -qx "$KIND_CLUSTER" && pass "kind: klaster istnieje" || { fail "brak klastra: make klaster"; exit 1; }
kubectl config use-context "kind-$KIND_CLUSTER" >/dev/null 2>&1
kubectl get crd workflows.argoproj.io >/dev/null 2>&1 && pass "Argo Workflows: CRD" || fail "brak CRD Argo: make klaster"
kubectl get deploy -n argo workflow-controller -o jsonpath='{.status.readyReplicas}' 2>/dev/null | grep -q 1 && pass "Argo Workflows: kontroler" || fail "Argo: kontroler nie działa"
kubectl get crd agents.kagent.dev >/dev/null 2>&1 && pass "kagent: CRD" || fail "brak CRD kagent: make klaster"
kubectl get deploy -n kagent kagent-controller -o jsonpath='{.status.readyReplicas}' 2>/dev/null | grep -q 1 && pass "kagent: kontroler" || fail "kagent: kontroler nie działa"
kubectl get crd mcpservers.kagent.dev >/dev/null 2>&1 && pass "kmcp: CRD MCPServer" || fail "brak CRD MCPServer"
kubectl get modelconfig fabryka-model -n fabryka -o jsonpath='{.status.conditions[?(@.type=="Accepted")].status}' 2>/dev/null | grep -q True && pass "ModelConfig fabryka-model" || fail "ModelConfig fabryka-model nie jest zaakceptowany"
key=$(kubectl get secret fabryka-llm -n fabryka -o jsonpath='{.data.LLM_API_KEY}' 2>/dev/null | base64 -d)
model=$(kubectl get modelconfig fabryka-model -n fabryka -o jsonpath='{.spec.model}' 2>/dev/null)
if [ "$key" = "brak" ] || [ -z "$key" ]; then pass "klucz do modelu: brak (tryb replay; klucz dostaniesz na miejscu: make klucz)"; else pass "klucz do modelu ustawiony (model: $model)"; fi
kubectl get agent probny -n fabryka -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null | grep -q True && pass "agent probny gotowy" || fail "agent probny nie jest gotowy"
kubectl get deploy -n kyverno kyverno-admission-controller -o jsonpath='{.status.readyReplicas}' 2>/dev/null | grep -q 1 && pass "Kyverno" || fail "Kyverno nie działa"
kubectl get deploy -n fabryka jaeger -o jsonpath='{.status.readyReplicas}' 2>/dev/null | grep -q 1 && pass "Jaeger" || fail "Jaeger nie działa"
curl -fsS -m 5 "http://localhost:8083/api/a2a/fabryka/probny/.well-known/agent-card.json" >/dev/null 2>&1 \
  && pass "A2A agenta probny pod http://localhost:8083" || fail "A2A nie odpowiada na localhost:8083 (kind.yaml, nodeports.yaml)"
for extra in scripts/doctor.d/*.sh; do [ -f "$extra" ] && . "$extra"; done

[ $ok -eq 0 ] && printf '\n\033[32mWszystko gotowe. Do zobaczenia na Confiturze!\033[0m\n' || printf '\n\033[31mPopraw czerwone pozycje. Jeśli utkniesz, odpisz na maila.\033[0m\n'
exit $ok

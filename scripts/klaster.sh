#!/usr/bin/env bash
# Stawia klaster fabryki od zera albo dociąga brakujące części. Idempotentne: możesz uruchamiać wiele razy.
#   kind (klaster) → Argo Workflows (linia) → kagent (agenci) → Kyverno (polityka) → Jaeger (ślady)
set -euo pipefail
cd "$(dirname "$0")/.."
. scripts/workshop.env

KAGENT_VERSION=0.10.1
ARGO_VERSION=v4.1.4
KYVERNO_CHART=3.9.1

step() { printf '\n\033[1m== %s\033[0m\n' "$*"; }

step "kind: klaster $KIND_CLUSTER"
if ! kind get clusters 2>/dev/null | grep -qx "$KIND_CLUSTER"; then
  kind create cluster --config platforma/kind.yaml --wait 120s
else
  echo "klaster już jest"
fi
kubectl config use-context "kind-$KIND_CLUSTER" >/dev/null
kubectl create namespace fabryka --dry-run=client -o yaml | kubectl apply -f - >/dev/null
kubectl create namespace argo --dry-run=client -o yaml | kubectl apply -f - >/dev/null
kubectl create namespace kagent --dry-run=client -o yaml | kubectl apply -f - >/dev/null

step "Argo Workflows $ARGO_VERSION (linia)"
# CRD Argo mają adnotacje > 256 KiB, więc apply musi być server-side.
kubectl apply --server-side -n argo \
  -f "https://github.com/argoproj/argo-workflows/releases/download/$ARGO_VERSION/quick-start-minimal.yaml" >/dev/null

step "kagent $KAGENT_VERSION (agenci)"
# Sekret z kluczem musi istnieć, zanim wstaną agenci; bez klucza dostają wartość „brak” i linia działa w trybie replay.
kubectl get secret fabryka-llm -n fabryka >/dev/null 2>&1 || \
  kubectl create secret generic fabryka-llm -n fabryka --from-literal=LLM_API_KEY=brak >/dev/null
kubectl get secret kagent-openai -n kagent >/dev/null 2>&1 || \
  kubectl create secret generic kagent-openai -n kagent --from-literal=OPENAI_API_KEY=brak >/dev/null
CHART_CRDS=${KAGENT_CHART_CRDS:-oci://ghcr.io/kagent-dev/kagent/helm/kagent-crds}
CHART=${KAGENT_CHART:-oci://ghcr.io/kagent-dev/kagent/helm/kagent}
helm upgrade --install kagent-crds "$CHART_CRDS" --version "$KAGENT_VERSION" -n kagent >/dev/null
helm upgrade --install kagent "$CHART" --version "$KAGENT_VERSION" -n kagent -f platforma/kagent/values.yaml >/dev/null
LLM_MODEL="$LLM_MODEL" LLM_BASE_URL="$LLM_BASE_URL" envsubst < platforma/kagent/modelconfig.yaml | kubectl apply -f - >/dev/null
kubectl apply -f platforma/kagent/agent-probny.yaml >/dev/null

step "Kyverno $KYVERNO_CHART (polityka, tylko admission)"
helm repo add kyverno https://kyverno.github.io/kyverno/ >/dev/null 2>&1 || true
helm repo update kyverno >/dev/null 2>&1
helm upgrade --install kyverno kyverno/kyverno --version "$KYVERNO_CHART" -n kyverno --create-namespace \
  --set admissionController.replicas=1 --set backgroundController.enabled=false \
  --set cleanupController.enabled=false --set reportsController.enabled=false >/dev/null

step "Jaeger (ślady OpenTelemetry)"
kubectl apply -f platforma/otel/jaeger.yaml >/dev/null
kubectl apply -f platforma/nodeports.yaml >/dev/null

step "Czekam na pody"
kubectl rollout status -n argo deploy/argo-server --timeout=180s >/dev/null
kubectl rollout status -n kagent deploy/kagent-controller --timeout=300s >/dev/null
kubectl rollout status -n kagent deploy/kagent-ui --timeout=180s >/dev/null
kubectl rollout status -n kyverno deploy/kyverno-admission-controller --timeout=180s >/dev/null
kubectl rollout status -n fabryka deploy/jaeger --timeout=180s >/dev/null
kubectl wait --for=condition=Ready agent/probny -n fabryka --timeout=180s >/dev/null

cat <<MSG

Klaster stoi. Adresy na localhost:
  hala (Argo Workflows)   https://localhost:2746
  kagent dashboard        http://localhost:8082
  kagent API / A2A        http://localhost:8083
  Jaeger (ślady)          http://localhost:16686
Sprawdź: make doctor
MSG

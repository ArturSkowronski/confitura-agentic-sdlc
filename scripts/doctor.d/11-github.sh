# Finał: fork na GitHubie, gh i (po make github) Secret i poller w klastrze.
echo "GitHub (finał)"
command -v gh >/dev/null && gh auth status >/dev/null 2>&1 && pass "gh zalogowany" || fail "gh: brew install gh && gh auth login"
origin=$(git remote get-url origin 2>/dev/null || true)
case "$origin" in
  *github.com*ArturSkowronski/confitura-agentic-sdlc*) fail "origin to repo prowadzącego: zrób fork i git remote set-url origin <Twój fork>" ;;
  *github.com*) pass "origin: $origin" ;;
  *) fail "origin nie wskazuje forka na GitHubie (zob. SETUP.md)" ;;
esac
if kubectl get secret fabryka-github -n fabryka >/dev/null 2>&1; then
  pass "Secret fabryka-github ($(kubectl get secret fabryka-github -n fabryka -o jsonpath='{.data.GH_REPO}' | base64 -d))"
  kubectl get cronworkflow fabryka-ciagnie -n fabryka >/dev/null 2>&1 && pass "poller fabryka-ciagnie" || fail "brak pollera: make github"
else
  pass "fork jeszcze niepodłączony do klastra (make github na finale)"
fi
kubectl get deploy workflow-controller -n argo -o jsonpath='{.spec.template.spec.containers[0].env}' 2>/dev/null | grep -q OTEL_EXPORTER_OTLP_ENDPOINT \
  && pass "Argo wysyła ślady przebiegów do Jaegera" || fail "Argo bez śladów: make klaster (idempotentne)"

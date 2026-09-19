# Lekcja 2: obrazy, dysk, magazyn, serwer MCP i wykonawca.
echo "Warsztat (lekcja 2)"
for img in fabryka-toolbox fabryka-warsztat; do
  docker image inspect "$img:$IMAGE_TAG" >/dev/null 2>&1 && pass "obraz $img:$IMAGE_TAG" || fail "brak obrazu $img: make setup"
done
kubectl get pvc warsztat -n fabryka -o jsonpath='{.status.phase}' 2>/dev/null | grep -q Bound && pass "dysk /work" || fail "PVC warsztat nie jest Bound"
kubectl get deploy magazyn -n fabryka -o jsonpath='{.status.readyReplicas}' 2>/dev/null | grep -q 1 && pass "magazyn" || fail "magazyn nie działa (make setup)"
kubectl get mcpserver warsztat -n fabryka -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null | grep -q True && pass "serwer MCP warsztat" || fail "MCPServer warsztat nie jest Ready"
kubectl get agent wykonawca -n fabryka -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null | grep -q True && pass "agent wykonawca gotowy" || fail "agent wykonawca nie jest gotowy"
kubectl exec -n fabryka deploy/magazyn -- test -d /work/repo/system >/dev/null 2>&1 && pass "snapshot repo w klastrze" || fail "brak snapshotu: make wyslij"

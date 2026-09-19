# Lekcja 10: klucz do podpisu księgi i ślady.
echo "Ślad (lekcja 10)"
kubectl get secret fabryka-cosign -n fabryka >/dev/null 2>&1 && pass "klucz cosign w klastrze" || fail "brak klucza cosign: make klucze-cosign"
[ -f platforma/linia/cosign/cosign.pub ] && pass "klucz publiczny do weryfikacji" || fail "brak platforma/linia/cosign/cosign.pub: make klucze-cosign"
curl -fsS -m 5 "http://localhost:16686/api/services" 2>/dev/null | grep -q '"data"' && pass "Jaeger odpowiada (http://localhost:16686)" || fail "Jaeger nie odpowiada na localhost:16686"

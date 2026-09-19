# Lekcja 1: Klaster i pierwszy agent (12 min)

**Teza.** Agent to zasób w klastrze, a nie skrypt na laptopie. Ma manifest, wersję, właściciela,
limity i adres. Kontroler kagent zamienia manifest `Agent` w Deployment, Service i endpoint
A2A (Agent2Agent, protokół Linux Foundation). Ten sam mechanizm, którym od lat wdrażasz serwisy,
wdraża teraz agentów.

Stack, na którym stoi fabryka (wszystko Linux Foundation):

| Warstwa | Projekt | Fundacja |
|---|---|---|
| Klaster | kind, Kubernetes | CNCF |
| Agenci | kagent 0.10.1 | CNCF Sandbox |
| Protokoły agentów | MCP, A2A | Agentic AI Foundation (LF) |
| Linia | Argo Workflows | CNCF Graduated |
| Polityka | Kyverno | CNCF Incubating |
| Ślady | OpenTelemetry, Jaeger | CNCF |
| Podpis | Sigstore cosign | OpenSSF Graduated |

## Co masz po `make klaster`

1. Otwórz dashboard kagent: `make hala` (http://localhost:8082).
2. Zobacz agenta jako zasób: `kubectl get agent -n fabryka`.
3. Zobacz, co kontroler z niego zrobił: `kubectl get deploy,svc -n fabryka -l kagent=probny`.
4. Zapytaj agenta przez A2A: `make a2a A=probny T="Przedstaw się"`.
5. Zobacz kartę agenta: `python3 sdlc/a2a.py --agent probny --card`.

Karta agenta to `/.well-known/agent-card.json`. Tak inne agenty i linia dowiadują się, co
umie ten agent i pod jakim adresem go wołać. Adres w klastrze:
`http://kagent-controller.kagent.svc:8083/api/a2a/fabryka/probny/`.

## Ćwiczenie: agent „przyjęcie” (8 min)

Fabryka nie przyjmie zlecenia bez kryteriów akceptacji. Do pytania autora o brakujące kryteria
użyje osobnego agenta. Ten agent nie ma narzędzi. Ma tylko dobrą instrukcję.

1. Otwórz `platforma/kagent/agent-przyjecie.yaml`.
2. Zamień `TODO` w `systemMessage` na instrukcję. Instrukcje dla modeli piszemy po angielsku,
   odpowiedzi mają być po polsku. Agent ma dostać tytuł i opis zlecenia. Ma zadać dwa do czterech
   pytań, bez których nie da się napisać testu akceptacyjnego. Ma odpowiedzieć listą punktowaną, bez wstępu.
3. Wdróż agenta: `kubectl apply -f platforma/kagent/agent-przyjecie.yaml`.
4. Poczekaj na gotowość: `kubectl wait --for=condition=Ready agent/przyjecie -n fabryka`.
5. Sprawdź: `make a2a A=przyjecie T="Anulowanie zamówienia. Klient może anulować zamówienie, dopóki nie jest opłacone."`

Dobra instrukcja daje pytania o stan zamówienia po anulowaniu, o zwrot pieniędzy przy
częściowej płatności i o to, kto może anulować. Zła instrukcja daje wypracowanie.

## Do dyskusji

- Manifest agenta przechodzi ten sam review co kod. Kto w Twojej organizacji zatwierdza dziś
  zmianę promptu?
- Port 8083 nie ma uwierzytelniania: tożsamość to nagłówek `X-User-Id`. W produkcji przed
  agentami staje brama (agentgateway, też LF). Na warsztacie zostajemy w klastrze.
- Bez klucza do modelu agent wstaje, ale nie odpowiada. Fabryka ma na to tryb replay (lekcja 5).

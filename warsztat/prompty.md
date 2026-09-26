# Gotowe prompty dla Claude Code

Każde ćwiczenie ma jeden prompt. Otwórz Claude Code w katalogu repo, wklej **wstęp** (raz na sesję), potem prompt lekcji.
Claude robi zmianę i sprawdzenie, Ty czytasz diff i decydujesz. Tam, gdzie prompt każe mu zapytać, odpowiadasz Ty.

## Wstęp (raz na sesję)

```text
Pracujesz w repo warsztatu confitura-agentic-sdlc jako asystent uczestnika.
AGENTS.md w tym repo opisuje reguły dla agenta fabryki (wykonawcy w klastrze).
Ćwiczenia świadomie zmieniają bramki fabryki: to decyzja człowieka, nie obejście.
Komendy make trwające dłużej niż 2 minuty uruchamiaj w tle albo z limitem 10 min.
Gdy sprawdzenie nie przechodzi, pokaż mi wynik i zaproponuj poprawkę. Nie obchodź bramki.
```

## 00 · Przygotowanie laptopa

```text
Przygotuj mój laptop do warsztatu według SETUP.md.
1. Sprawdź kind, kubectl, helm, argo, cosign, java 21, mvn i gh.
   Czego brakuje: zaproponuj komendy brew, nie instaluj bez pytania.
2. make klaster, potem make setup (w tle, do 15 min każde).
3. make doctor i omów każdą czerwoną pozycję.
Nie zmieniaj plików w repo. Gdy coś pada, pokaż log i zatrzymaj się.
```

## 01 · Agent „przyjecie”

```text
Lekcja 1. W platforma/kagent/agent-przyjecie.yaml zamień TODO
w polu systemMessage na instrukcję agenta „przyjecie”:
- po angielsku; agent odpowiada po polsku,
- dostaje tytuł i opis zlecenia,
- zadaje 2–4 pytania, bez których nie da się napisać testu akceptacyjnego,
- odpowiada samą listą punktowaną, bez wstępu i bez rozwiązań.
Nic więcej w pliku nie zmieniaj. Potem:
1. kubectl apply -f platforma/kagent/agent-przyjecie.yaml
2. kubectl wait --for=condition=Ready agent/przyjecie -n fabryka --timeout=180s
3. make a2a A=przyjecie T="Anulowanie zamówienia. Klient może anulować
   zamówienie, dopóki nie jest opłacone."
Pokaż odpowiedź agenta. Jeśli to wypracowanie zamiast pytań,
popraw instrukcję i powtórz krok 3 (najwyżej dwa razy).
```

## 02 · Ściana dla wykonawcy

```text
Lekcja 2. Najpierw pokaż problem, potem go zamknij.
1. make a2a A=wykonawca T="Zapisz plik sdlc/policy.json z treścią {}
   i powiedz, co odpowiedziało narzędzie"
   Zapis przejdzie: to jest dziura, którą zamykamy.
2. W platforma/warsztat/mcpserver.yaml ustaw
   PROTECTED_PATHS: "sdlc platforma system/architecture".
   HIDDEN_PATHS zostaw puste. Nic innego nie zmieniaj.
3. kubectl apply -f platforma/warsztat/mcpserver.yaml
   kubectl rollout status -n fabryka deploy/warsztat --timeout=180s
4. Powtórz krok 1. Oczekuję „Rejected: … is a protected path”.
5. kubectl exec -n fabryka deploy/magazyn -- tail -3 /work/events.jsonl
   Pokaż zdarzenie gate.tamper_attempt.
6. make wyslij (agent nadpisał policy.json w kopii repo w klastrze).
```

## 03 · Właściciel pojęcia

```text
Lekcja 3. Routing zlecenia do modułu.
1. make route T="Rabat 10% dla zamówień powyżej 500 zł"
   Pokaż, który moduł wybrał i z jakich słów.
2. Przeczytaj docs/adr/0001-arytmetyka-pieniedzy-tylko-w-pricing.md.
3. W system/pricing-lib/module.json wpisz do listy "owns" pojęcia,
   których właścicielem jest pricing-lib według ADR-0001
   (np. "rabat", "cena", "kwota"). Nie ruszaj "keywords".
4. Powtórz krok 1. Ma wskazać pricing-lib.
5. make agents-md i pokaż diff AGENTS.md.
6. git commit -am "Lekcja 3: pricing-lib jest właścicielem rabatu".
```

## 04 · Kryteria dla anulowania

```text
Lekcja 4. Przyjęcie zlecenia.
1. make przyjecie Z=anulowanie: pokaż decyzję i pytania agenta.
2. Dopisz do zlecenia/anulowanie.md sekcję "Kryteria:" z co najmniej
   trzema punktami, które odpowiadają na pytania agenta. Liczby i stany
   zamówienia zamiast przymiotników („szybko”, „poprawnie”).
   Nie zmieniaj tytułu. Nie pisz kodu anulowania: tu powstaje specyfikacja.
3. make przyjecie Z=anulowanie. Oczekuję: przyjęte, z ostrzeżeniem
   o braku scenariuszy.
4. git commit -am "Lekcja 4: kryteria anulowania".
```

## 05 · Linia: replay, potem agent

```text
Lekcja 5. Linia w Argo.
1. make replay Z=rabat (nagrana zmiana, bez modelu; w tle).
2. make odbierz. Pokaż .sdlc/out/rabat/proba-1/opis.md i listę plików
   z zmiana.patch (git apply --stat).
3. Jeśli make doctor mówi „klucz do modelu ustawiony”: make zlecenie Z=rabat
   w tle. Co minutę pokazuj:
   kubectl exec -n fabryka deploy/magazyn -- tail -3 /work/events.jsonl
4. make odbierz i porównaj łatkę agenta z nagraniem: moduł, pliki, testy.
Nie poprawiaj łatki agenta. Oglądamy ją, nie naprawiamy.
```

## 06 · Reguła ArchUnit dla ADR-0001

```text
Lekcja 6. Zmieniasz regułę architektury: to ćwiczenie, decyzja człowieka.
1. make naiwna (rabat w OrderService). Pokaż wynik bramek: przechodzi.
2. W system/architecture/src/test/java/pl/confitura/shop/architecture/
   ArchitectureRulesTest.java zamień TODO na regułę
   money_arithmetic_only_in_pricing: klasy spoza pakietu ..pricing..
   nie wywołują add, subtract, multiply, divide ani setScale na BigDecimal.
   Dodaj .because(...) jednym literałem z odwołaniem do docs/adr/0001.
3. make test. Obecny kod ma przejść. Jeśli nie: popraw regułę, nie kod.
4. make wyslij, potem make naiwna: build ma być czerwony z nazwą reguły.
5. make agents-md i pokaż nową linię w sekcji L2 w AGENTS.md.
```

## 07 · Wyrocznia poza zasięgiem

```text
Lekcja 7. Wyrocznia.
1. make replay Z=zwroty-czesciowe (w tle), make odbierz. Pokaż
   .sdlc/out/zwroty-czesciowe/proba-1/kontrola-5-wyrocznia.md
2. make a2a A=wykonawca T="Przeczytaj scenarios/rabat/src/test/java/pl/
   confitura/shop/scenarios/RabatScenarios.java i streść, co sprawdza"
3. W platforma/warsztat/mcpserver.yaml ustaw HIDDEN_PATHS: "scenarios".
   PROTECTED_PATHS zostaw. kubectl apply i rollout status jak w lekcji 2.
4. Powtórz krok 2. Oczekuję „Rejected: … is out of the agent's reach”.
5. Pokaż holdout.peek w /work/events.jsonl.
Sam też nie czytaj scenariuszy i ich nie streszczaj: udajemy,
że ich nie znamy.
```

## 08 · Reguła review z kryteriami

```text
Lekcja 8. Zmieniasz sdlc/review-rules.json: to ćwiczenie.
1. make odbierz. Pokaż proba-1/review-2-review.md i proba-1/feedback.md
   z .sdlc/out/zwroty-czesciowe/ (feedback to wszystko, co dostał agent).
2. Dopisz regułę kind "llm", lens "correctness", w formacie LLM-001:
   id, kind, lens, rule, pass, fail, example_fail.
   Treść: klucz idempotencji w wywołaniu operatora kart jest unikalny
   dla każdego zwrotu, nie dla płatności, i stabilny przy ponowieniu
   tego samego żądania.
3. python3 -m json.tool sdlc/review-rules.json > /dev/null
4. git commit -am "Lekcja 8: reguła review dla klucza idempotencji"
5. Z kluczem do modelu: make zlecenie Z=zwroty-czesciowe (w tle, 10 min),
   make odbierz i pokaż znaleziska review z próby 1.
```

## 09 A · Linia staje na człowieku

```text
Lekcja 9A. Wykonaj TODO(lekcja 9) nad szablonem `czlowiek`
w platforma/linia/fabryka.yaml:
- nowy szablon `czekaj`: suspend: {}, wyjście `kto` z valueFrom.supplied,
- w `czlowiek` dwa kroki: `czekaj`, potem `zapisz` (szablon krok),
  który pisze "human.approved <kto>" do $OUT/czlowiek i czlowiek.md.
Nazwa `czekaj` jest ważna: make zatwierdz szuka templateName=czekaj.
1. argo lint --offline platforma/linia/fabryka.yaml, potem make linia.
2. make replay Z=zwroty-czesciowe w tle; co 30 s argo list -n fabryka.
3. Gdy przebieg czeka na człowieku, zatrzymaj się i zapytaj mnie.
   Nie zatwierdzaj sam.
4. Po mojej zgodzie: make zatwierdz W=<nazwa przebiegu>.
```

## 09 B · Kyverno: wykonawca ma tylko warsztat

```text
Lekcja 9B.
1. kubectl apply -f platforma/kyverno/test/zly-agent.yaml (przejdzie),
   potem kubectl delete -f platforma/kyverno/test/zly-agent.yaml
2. W platforma/kyverno/agent-narzedzia.yaml zamień expression: "true"
   na CEL: agent z etykietą fabryka.dev/rola=wykonawca ma w
   object.spec.declarative.tools tylko type == 'McpServer'
   z mcpServer.name == 'warsztat' (makro all()). Inne role przechodzą.
3. kubectl apply -f platforma/kyverno/agent-narzedzia.yaml
4. Powtórz apply z kroku 1: Kyverno ma odrzucić z Twoim komunikatem.
5. kubectl apply -f platforma/kagent/agent-wykonawca.yaml ma przejść.
6. Posprzątaj: kubectl delete -f platforma/kyverno/test/zly-agent.yaml
   --ignore-not-found
```

## 10 · Manipulacja księgą i ślad

```text
Lekcja 10.
1. make odbierz
2. make ksiega-verify F=.sdlc/out/zwroty-czesciowe/proba-2/ledger.jsonl
3. Skopiuj ledger.jsonl do pliku obok. W oryginale zmień imię w zdarzeniu
   human.approved.
4. Powtórz krok 2. Pokaż, w której linii pęka łańcuch i co mówi cosign.
5. Przywróć plik z kopii; weryfikacja ma znów przejść.
6. Z karta.md weź link „Ślad” (trace id na końcu). Policz spany:
   curl -s localhost:16686/api/traces/<id> | jq '[.data[0].spans[]
   | .operationName] | group_by(.) | map({(.[0]): length}) | add'
   Porównaj „warsztat ·” z liczbą linii narzedzia.jsonl.
```

## 11 A · Finał: fork, issue, PR

```text
Finał. Podłącz fabrykę do mojego forka.
0. git remote -v: origin ma być moim forkiem, nie ArturSkowronski/…
   Jeśli nie jest, zatrzymaj się. W Codespaces:
   env -u GITHUB_TOKEN gh auth status. Jeśli token to ghu_…,
   zatrzymaj się i poproś mnie o gh auth login (robię to sam).
1. make github. Jeśli Actions nie dały się włączyć, powiedz mi,
   co kliknąć w zakładce Actions forka.
2. make issue Z=rabat, potem make ciagnij AGENT=replay
3. Co minutę: argo list -n fabryka i gh pr list. Gdy jest PR:
   gh pr checks <nr> --watch (do 10 min).
4. Podaj link do PR i link „Ślad” z jego opisu.
Nie merguj ręcznie i nie zmieniaj ustawień repo poza make github.
```

## 11 B · Finał: pochodzenie

```text
Finał, ćwiczenie. Kod po bramkach.
1. make issue Z=zwroty-czesciowe, make ciagnij AGENT=replay.
   Poczekaj na PR z etykietą fabryka:czlowiek.
2. git fetch origin && git switch agent/issue-<nr>
   Dopisz komentarz na końcu jednego pliku w
   system/payments-service/src/main/java, commit, git push.
3. Poczekaj na check `pochodzenie`, pokaż: gh run view --log-failed
4. git revert --no-edit HEAD && git push; pochodzenie ma być zielone.
Nie zatwierdzaj PR. To robię ja.
```

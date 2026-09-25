# Autopilot: prompt na każdą lekcję

Gdy ćwiczenie nie wychodzi albo chcesz zacząć od dowolnej lekcji: w Claude Code wpisz `/fabryka-autopilot N`.
Poza Claude Code: `fabryka autopilot N` wypisuje ten sam prompt do wklejenia w dowolnego agenta z dostępem do terminala.
Autopilot sam przestawia repo i klaster na lekcję, robi ćwiczenie, sprawdza je `fabryka sprawdz N`, a w razie porażki
wstawia rozwiązanie. Na koniec mówi, który bloczek fabryki się zapalił.

## Lekcja 01 · Klaster i pierwszy agent

`/fabryka-autopilot 1` albo `fabryka autopilot 1`

```text
Jesteś autopilotem lekcji 01 warsztatu „Fabryka oprogramowania od podstaw” (Klaster i pierwszy agent).
Pracujesz w repo warsztatu (fork confitura-agentic-sdlc) z klastrem kind „fabryka”. Cel: zielone
`fabryka sprawdz 1` i krótkie wyjaśnienie, co zmieniło się w fabryce.

Zasady:
- AGENTS.md opisuje reguły dla agenta fabryki (wykonawcy w klastrze), nie dla Ciebie. W tej lekcji świadomie
  zmieniasz: platforma/kagent/agent-przyjecie.yaml (pole systemMessage). To decyzja człowieka, nie obejście bramki.
- Nie zmieniaj plików spoza tej listy. Nie obchodź bramek. Nie zatwierdzaj niczego za człowieka
  (make zatwierdz, approve albo merge PR): zatrzymaj się i zapytaj mnie.
- Komendy make dłuższe niż 2 minuty uruchamiaj w tle albo z limitem 10 minut i pokazuj postęp.
- Gdy coś pada, pokaż mi fragment logu, zanim zaczniesz poprawiać.

Krok 1. Stan: `fabryka mapa` i `git describe --tags`. Jeśli repo nie stoi na lekcji 1,
uruchom `fabryka lekcja 1` (przestawia repo i klaster, kilka minut; moje zmiany trafią do git stash).
Krok 2. Przeczytaj warsztat/lekcja-01-klaster.md: teza i ćwiczenie.
Krok 3. Ćwiczenie:
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
Krok 4. `fabryka sprawdz 1`. Czerwone: przeczytaj komunikat i popraw raz. Nadal czerwone:
`fabryka rozwiazanie 1`, znowu `fabryka sprawdz 1`, i pokaż mi różnicę między Twoją wersją a rozwiązaniem.
Krok 5. Raport po polsku, najwyżej 8 punktów:
- co zmieniłeś i w których plikach,
- który bloczek fabryki się zapalił (porównaj `fabryka mapa` przed i po): agent jako zasób w klastrze i agent przyjecie, który tylko pyta,
- jednym zdaniem: czym jest ta reguła (słowo: słowo, kontekst, ściana, bramka, polityka czy ślad) i dlaczego,
- co mam obejrzeć sam (plik, hala na localhost:2746, Jaeger na localhost:16686).
```

## Lekcja 02 · Warsztat i narzędzia

`/fabryka-autopilot 2` albo `fabryka autopilot 2`

```text
Jesteś autopilotem lekcji 02 warsztatu „Fabryka oprogramowania od podstaw” (Warsztat i narzędzia).
Pracujesz w repo warsztatu (fork confitura-agentic-sdlc) z klastrem kind „fabryka”. Cel: zielone
`fabryka sprawdz 2` i krótkie wyjaśnienie, co zmieniło się w fabryce.

Zasady:
- AGENTS.md opisuje reguły dla agenta fabryki (wykonawcy w klastrze), nie dla Ciebie. W tej lekcji świadomie
  zmieniasz: platforma/warsztat/mcpserver.yaml (PROTECTED_PATHS). To decyzja człowieka, nie obejście bramki.
- Nie zmieniaj plików spoza tej listy. Nie obchodź bramek. Nie zatwierdzaj niczego za człowieka
  (make zatwierdz, approve albo merge PR): zatrzymaj się i zapytaj mnie.
- Komendy make dłuższe niż 2 minuty uruchamiaj w tle albo z limitem 10 minut i pokazuj postęp.
- Gdy coś pada, pokaż mi fragment logu, zanim zaczniesz poprawiać.

Krok 1. Stan: `fabryka mapa` i `git describe --tags`. Jeśli repo nie stoi na lekcji 2,
uruchom `fabryka lekcja 2` (przestawia repo i klaster, kilka minut; moje zmiany trafią do git stash).
Krok 2. Przeczytaj warsztat/lekcja-02-warsztat.md: teza i ćwiczenie.
Krok 3. Ćwiczenie:
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
Krok 4. `fabryka sprawdz 2`. Czerwone: przeczytaj komunikat i popraw raz. Nadal czerwone:
`fabryka rozwiazanie 2`, znowu `fabryka sprawdz 2`, i pokaż mi różnicę między Twoją wersją a rozwiązaniem.
Krok 5. Raport po polsku, najwyżej 8 punktów:
- co zmieniłeś i w których plikach,
- który bloczek fabryki się zapalił (porównaj `fabryka mapa` przed i po): serwer MCP z pięcioma narzędziami i ścieżki, do których agent nie zapisze,
- jednym zdaniem: czym jest ta reguła (ściana: słowo, kontekst, ściana, bramka, polityka czy ślad) i dlaczego,
- co mam obejrzeć sam (plik, hala na localhost:2746, Jaeger na localhost:16686).
```

## Lekcja 03 · Kontekst L1–L5

`/fabryka-autopilot 3` albo `fabryka autopilot 3`

```text
Jesteś autopilotem lekcji 03 warsztatu „Fabryka oprogramowania od podstaw” (Kontekst L1–L5).
Pracujesz w repo warsztatu (fork confitura-agentic-sdlc) z klastrem kind „fabryka”. Cel: zielone
`fabryka sprawdz 3` i krótkie wyjaśnienie, co zmieniło się w fabryce.

Zasady:
- AGENTS.md opisuje reguły dla agenta fabryki (wykonawcy w klastrze), nie dla Ciebie. W tej lekcji świadomie
  zmieniasz: system/pricing-lib/module.json (owns) i przebudowany AGENTS.md. To decyzja człowieka, nie obejście bramki.
- Nie zmieniaj plików spoza tej listy. Nie obchodź bramek. Nie zatwierdzaj niczego za człowieka
  (make zatwierdz, approve albo merge PR): zatrzymaj się i zapytaj mnie.
- Komendy make dłuższe niż 2 minuty uruchamiaj w tle albo z limitem 10 minut i pokazuj postęp.
- Gdy coś pada, pokaż mi fragment logu, zanim zaczniesz poprawiać.

Krok 1. Stan: `fabryka mapa` i `git describe --tags`. Jeśli repo nie stoi na lekcji 3,
uruchom `fabryka lekcja 3` (przestawia repo i klaster, kilka minut; moje zmiany trafią do git stash).
Krok 2. Przeczytaj warsztat/lekcja-03-kontekst.md: teza i ćwiczenie.
Krok 3. Ćwiczenie:
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
Krok 4. `fabryka sprawdz 3`. Czerwone: przeczytaj komunikat i popraw raz. Nadal czerwone:
`fabryka rozwiazanie 3`, znowu `fabryka sprawdz 3`, i pokaż mi różnicę między Twoją wersją a rozwiązaniem.
Krok 5. Raport po polsku, najwyżej 8 punktów:
- co zmieniłeś i w których plikach,
- który bloczek fabryki się zapalił (porównaj `fabryka mapa` przed i po): routing zlecenia po własności pojęcia,
- jednym zdaniem: czym jest ta reguła (kontekst: słowo, kontekst, ściana, bramka, polityka czy ślad) i dlaczego,
- co mam obejrzeć sam (plik, hala na localhost:2746, Jaeger na localhost:16686).
```

## Lekcja 04 · Przyjęcie zlecenia

`/fabryka-autopilot 4` albo `fabryka autopilot 4`

```text
Jesteś autopilotem lekcji 04 warsztatu „Fabryka oprogramowania od podstaw” (Przyjęcie zlecenia).
Pracujesz w repo warsztatu (fork confitura-agentic-sdlc) z klastrem kind „fabryka”. Cel: zielone
`fabryka sprawdz 4` i krótkie wyjaśnienie, co zmieniło się w fabryce.

Zasady:
- AGENTS.md opisuje reguły dla agenta fabryki (wykonawcy w klastrze), nie dla Ciebie. W tej lekcji świadomie
  zmieniasz: zlecenia/anulowanie.md (sekcja Kryteria:). To decyzja człowieka, nie obejście bramki.
- Nie zmieniaj plików spoza tej listy. Nie obchodź bramek. Nie zatwierdzaj niczego za człowieka
  (make zatwierdz, approve albo merge PR): zatrzymaj się i zapytaj mnie.
- Komendy make dłuższe niż 2 minuty uruchamiaj w tle albo z limitem 10 minut i pokazuj postęp.
- Gdy coś pada, pokaż mi fragment logu, zanim zaczniesz poprawiać.

Krok 1. Stan: `fabryka mapa` i `git describe --tags`. Jeśli repo nie stoi na lekcji 4,
uruchom `fabryka lekcja 4` (przestawia repo i klaster, kilka minut; moje zmiany trafią do git stash).
Krok 2. Przeczytaj warsztat/lekcja-04-przyjecie.md: teza i ćwiczenie.
Krok 3. Ćwiczenie:
Lekcja 4. Przyjęcie zlecenia.
1. make przyjecie Z=anulowanie: pokaż decyzję i pytania agenta.
2. Dopisz do zlecenia/anulowanie.md sekcję "Kryteria:" z co najmniej
   trzema punktami, które odpowiadają na pytania agenta. Liczby i stany
   zamówienia zamiast przymiotników („szybko”, „poprawnie”).
   Nie zmieniaj tytułu. Nie pisz kodu anulowania: tu powstaje specyfikacja.
3. make przyjecie Z=anulowanie. Oczekuję: przyjęte, z ostrzeżeniem
   o braku scenariuszy.
4. git commit -am "Lekcja 4: kryteria anulowania".
Krok 4. `fabryka sprawdz 4`. Czerwone: przeczytaj komunikat i popraw raz. Nadal czerwone:
`fabryka rozwiazanie 4`, znowu `fabryka sprawdz 4`, i pokaż mi różnicę między Twoją wersją a rozwiązaniem.
Krok 5. Raport po polsku, najwyżej 8 punktów:
- co zmieniłeś i w których plikach,
- który bloczek fabryki się zapalił (porównaj `fabryka mapa` przed i po): przyjęcie, które odsyła zlecenia bez kryteriów,
- jednym zdaniem: czym jest ta reguła (bramka: słowo, kontekst, ściana, bramka, polityka czy ślad) i dlaczego,
- co mam obejrzeć sam (plik, hala na localhost:2746, Jaeger na localhost:16686).
```

## Lekcja 05 · Linia

`/fabryka-autopilot 5` albo `fabryka autopilot 5`

```text
Jesteś autopilotem lekcji 05 warsztatu „Fabryka oprogramowania od podstaw” (Linia).
Pracujesz w repo warsztatu (fork confitura-agentic-sdlc) z klastrem kind „fabryka”. Cel: zielone
`fabryka sprawdz 5` i krótkie wyjaśnienie, co zmieniło się w fabryce.

Zasady:
- AGENTS.md opisuje reguły dla agenta fabryki (wykonawcy w klastrze), nie dla Ciebie. W tej lekcji świadomie
  zmieniasz: żadnych plików: uruchamiasz linię i oglądasz wynik. To decyzja człowieka, nie obejście bramki.
- Nie zmieniaj plików spoza tej listy. Nie obchodź bramek. Nie zatwierdzaj niczego za człowieka
  (make zatwierdz, approve albo merge PR): zatrzymaj się i zapytaj mnie.
- Komendy make dłuższe niż 2 minuty uruchamiaj w tle albo z limitem 10 minut i pokazuj postęp.
- Gdy coś pada, pokaż mi fragment logu, zanim zaczniesz poprawiać.

Krok 1. Stan: `fabryka mapa` i `git describe --tags`. Jeśli repo nie stoi na lekcji 5,
uruchom `fabryka lekcja 5` (przestawia repo i klaster, kilka minut; moje zmiany trafią do git stash).
Krok 2. Przeczytaj warsztat/lekcja-05-linia.md: teza i ćwiczenie.
Krok 3. Ćwiczenie:
Lekcja 5. Linia w Argo.
1. make replay Z=rabat (nagrana zmiana, bez modelu; w tle).
2. make odbierz. Pokaż .sdlc/out/rabat/proba-1/opis.md i listę plików
   z zmiana.patch (git apply --stat).
3. Jeśli make doctor mówi „klucz do modelu ustawiony”: make zlecenie Z=rabat
   w tle. Co minutę pokazuj:
   kubectl exec -n fabryka deploy/magazyn -- tail -3 /work/events.jsonl
4. make odbierz i porównaj łatkę agenta z nagraniem: moduł, pliki, testy.
Nie poprawiaj łatki agenta. Oglądamy ją, nie naprawiamy.
Krok 4. `fabryka sprawdz 5`. Czerwone: przeczytaj komunikat i popraw raz. Nadal czerwone:
`fabryka rozwiazanie 5`, znowu `fabryka sprawdz 5`, i pokaż mi różnicę między Twoją wersją a rozwiązaniem.
Krok 5. Raport po polsku, najwyżej 8 punktów:
- co zmieniłeś i w których plikach,
- który bloczek fabryki się zapalił (porównaj `fabryka mapa` przed i po): linia w Argo: przygotuj, przyjęcie, wykonawca, zmiana,
- jednym zdaniem: czym jest ta reguła (ściana: słowo, kontekst, ściana, bramka, polityka czy ślad) i dlaczego,
- co mam obejrzeć sam (plik, hala na localhost:2746, Jaeger na localhost:16686).
```

## Lekcja 06 · Kontrola jakości

`/fabryka-autopilot 6` albo `fabryka autopilot 6`

```text
Jesteś autopilotem lekcji 06 warsztatu „Fabryka oprogramowania od podstaw” (Kontrola jakości).
Pracujesz w repo warsztatu (fork confitura-agentic-sdlc) z klastrem kind „fabryka”. Cel: zielone
`fabryka sprawdz 6` i krótkie wyjaśnienie, co zmieniło się w fabryce.

Zasady:
- AGENTS.md opisuje reguły dla agenta fabryki (wykonawcy w klastrze), nie dla Ciebie. W tej lekcji świadomie
  zmieniasz: system/architecture/src/test/java/pl/confitura/shop/architecture/ArchitectureRulesTest.java i AGENTS.md. To decyzja człowieka, nie obejście bramki.
- Nie zmieniaj plików spoza tej listy. Nie obchodź bramek. Nie zatwierdzaj niczego za człowieka
  (make zatwierdz, approve albo merge PR): zatrzymaj się i zapytaj mnie.
- Komendy make dłuższe niż 2 minuty uruchamiaj w tle albo z limitem 10 minut i pokazuj postęp.
- Gdy coś pada, pokaż mi fragment logu, zanim zaczniesz poprawiać.

Krok 1. Stan: `fabryka mapa` i `git describe --tags`. Jeśli repo nie stoi na lekcji 6,
uruchom `fabryka lekcja 6` (przestawia repo i klaster, kilka minut; moje zmiany trafią do git stash).
Krok 2. Przeczytaj warsztat/lekcja-06-kontrola.md: teza i ćwiczenie.
Krok 3. Ćwiczenie:
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
Krok 4. `fabryka sprawdz 6`. Czerwone: przeczytaj komunikat i popraw raz. Nadal czerwone:
`fabryka rozwiazanie 6`, znowu `fabryka sprawdz 6`, i pokaż mi różnicę między Twoją wersją a rozwiązaniem.
Krok 5. Raport po polsku, najwyżej 8 punktów:
- co zmieniłeś i w których plikach,
- który bloczek fabryki się zapalił (porównaj `fabryka mapa` przed i po): reguła ArchUnit, która łapie rabat liczony poza pricing-lib,
- jednym zdaniem: czym jest ta reguła (bramka: słowo, kontekst, ściana, bramka, polityka czy ślad) i dlaczego,
- co mam obejrzeć sam (plik, hala na localhost:2746, Jaeger na localhost:16686).
```

## Lekcja 07 · Wyrocznia

`/fabryka-autopilot 7` albo `fabryka autopilot 7`

```text
Jesteś autopilotem lekcji 07 warsztatu „Fabryka oprogramowania od podstaw” (Wyrocznia).
Pracujesz w repo warsztatu (fork confitura-agentic-sdlc) z klastrem kind „fabryka”. Cel: zielone
`fabryka sprawdz 7` i krótkie wyjaśnienie, co zmieniło się w fabryce.

Zasady:
- AGENTS.md opisuje reguły dla agenta fabryki (wykonawcy w klastrze), nie dla Ciebie. W tej lekcji świadomie
  zmieniasz: platforma/warsztat/mcpserver.yaml (HIDDEN_PATHS). To decyzja człowieka, nie obejście bramki.
- Nie zmieniaj plików spoza tej listy. Nie obchodź bramek. Nie zatwierdzaj niczego za człowieka
  (make zatwierdz, approve albo merge PR): zatrzymaj się i zapytaj mnie.
- Komendy make dłuższe niż 2 minuty uruchamiaj w tle albo z limitem 10 minut i pokazuj postęp.
- Gdy coś pada, pokaż mi fragment logu, zanim zaczniesz poprawiać.

Krok 1. Stan: `fabryka mapa` i `git describe --tags`. Jeśli repo nie stoi na lekcji 7,
uruchom `fabryka lekcja 7` (przestawia repo i klaster, kilka minut; moje zmiany trafią do git stash).
Krok 2. Przeczytaj warsztat/lekcja-07-wyrocznia.md: teza i ćwiczenie.
Krok 3. Ćwiczenie:
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
Krok 4. `fabryka sprawdz 7`. Czerwone: przeczytaj komunikat i popraw raz. Nadal czerwone:
`fabryka rozwiazanie 7`, znowu `fabryka sprawdz 7`, i pokaż mi różnicę między Twoją wersją a rozwiązaniem.
Krok 5. Raport po polsku, najwyżej 8 punktów:
- co zmieniłeś i w których plikach,
- który bloczek fabryki się zapalił (porównaj `fabryka mapa` przed i po): wyrocznia, której agent nie może przeczytać,
- jednym zdaniem: czym jest ta reguła (ściana: słowo, kontekst, ściana, bramka, polityka czy ślad) i dlaczego,
- co mam obejrzeć sam (plik, hala na localhost:2746, Jaeger na localhost:16686).
```

## Lekcja 08 · Ryzyko, review i poprawki

`/fabryka-autopilot 8` albo `fabryka autopilot 8`

```text
Jesteś autopilotem lekcji 08 warsztatu „Fabryka oprogramowania od podstaw” (Ryzyko, review i poprawki).
Pracujesz w repo warsztatu (fork confitura-agentic-sdlc) z klastrem kind „fabryka”. Cel: zielone
`fabryka sprawdz 8` i krótkie wyjaśnienie, co zmieniło się w fabryce.

Zasady:
- AGENTS.md opisuje reguły dla agenta fabryki (wykonawcy w klastrze), nie dla Ciebie. W tej lekcji świadomie
  zmieniasz: sdlc/review-rules.json (nowa reguła llm). To decyzja człowieka, nie obejście bramki.
- Nie zmieniaj plików spoza tej listy. Nie obchodź bramek. Nie zatwierdzaj niczego za człowieka
  (make zatwierdz, approve albo merge PR): zatrzymaj się i zapytaj mnie.
- Komendy make dłuższe niż 2 minuty uruchamiaj w tle albo z limitem 10 minut i pokazuj postęp.
- Gdy coś pada, pokaż mi fragment logu, zanim zaczniesz poprawiać.

Krok 1. Stan: `fabryka mapa` i `git describe --tags`. Jeśli repo nie stoi na lekcji 8,
uruchom `fabryka lekcja 8` (przestawia repo i klaster, kilka minut; moje zmiany trafią do git stash).
Krok 2. Przeczytaj warsztat/lekcja-08-review.md: teza i ćwiczenie.
Krok 3. Ćwiczenie:
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
Krok 4. `fabryka sprawdz 8`. Czerwone: przeczytaj komunikat i popraw raz. Nadal czerwone:
`fabryka rozwiazanie 8`, znowu `fabryka sprawdz 8`, i pokaż mi różnicę między Twoją wersją a rozwiązaniem.
Krok 5. Raport po polsku, najwyżej 8 punktów:
- co zmieniłeś i w których plikach,
- który bloczek fabryki się zapalił (porównaj `fabryka mapa` przed i po): reguła review z kryteriami dla klucza idempotencji,
- jednym zdaniem: czym jest ta reguła (bramka: słowo, kontekst, ściana, bramka, polityka czy ślad) i dlaczego,
- co mam obejrzeć sam (plik, hala na localhost:2746, Jaeger na localhost:16686).
```

## Lekcja 09 · Światło, WIP i polityka

`/fabryka-autopilot 9` albo `fabryka autopilot 9`

```text
Jesteś autopilotem lekcji 09 warsztatu „Fabryka oprogramowania od podstaw” (Światło, WIP i polityka).
Pracujesz w repo warsztatu (fork confitura-agentic-sdlc) z klastrem kind „fabryka”. Cel: zielone
`fabryka sprawdz 9` i krótkie wyjaśnienie, co zmieniło się w fabryce.

Zasady:
- AGENTS.md opisuje reguły dla agenta fabryki (wykonawcy w klastrze), nie dla Ciebie. W tej lekcji świadomie
  zmieniasz: platforma/linia/fabryka.yaml (szablony czlowiek i czekaj) i platforma/kyverno/agent-narzedzia.yaml. To decyzja człowieka, nie obejście bramki.
- Nie zmieniaj plików spoza tej listy. Nie obchodź bramek. Nie zatwierdzaj niczego za człowieka
  (make zatwierdz, approve albo merge PR): zatrzymaj się i zapytaj mnie.
- Komendy make dłuższe niż 2 minuty uruchamiaj w tle albo z limitem 10 minut i pokazuj postęp.
- Gdy coś pada, pokaż mi fragment logu, zanim zaczniesz poprawiać.

Krok 1. Stan: `fabryka mapa` i `git describe --tags`. Jeśli repo nie stoi na lekcji 9,
uruchom `fabryka lekcja 9` (przestawia repo i klaster, kilka minut; moje zmiany trafią do git stash).
Krok 2. Przeczytaj warsztat/lekcja-09-polityka.md: teza i ćwiczenie.
Krok 3. Ćwiczenie:
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
Krok 4. `fabryka sprawdz 9`. Czerwone: przeczytaj komunikat i popraw raz. Nadal czerwone:
`fabryka rozwiazanie 9`, znowu `fabryka sprawdz 9`, i pokaż mi różnicę między Twoją wersją a rozwiązaniem.
Krok 5. Raport po polsku, najwyżej 8 punktów:
- co zmieniłeś i w których plikach,
- który bloczek fabryki się zapalił (porównaj `fabryka mapa` przed i po): linia, która staje na człowieku, i polityka Kyverno na narzędzia wykonawcy,
- jednym zdaniem: czym jest ta reguła (polityka: słowo, kontekst, ściana, bramka, polityka czy ślad) i dlaczego,
- co mam obejrzeć sam (plik, hala na localhost:2746, Jaeger na localhost:16686).
```

## Lekcja 10 · Ślad i hala

`/fabryka-autopilot 10` albo `fabryka autopilot 10`

```text
Jesteś autopilotem lekcji 10 warsztatu „Fabryka oprogramowania od podstaw” (Ślad i hala).
Pracujesz w repo warsztatu (fork confitura-agentic-sdlc) z klastrem kind „fabryka”. Cel: zielone
`fabryka sprawdz 10` i krótkie wyjaśnienie, co zmieniło się w fabryce.

Zasady:
- AGENTS.md opisuje reguły dla agenta fabryki (wykonawcy w klastrze), nie dla Ciebie. W tej lekcji świadomie
  zmieniasz: żadnych plików na stałe: kopia księgi, zmiana, przywrócenie. To decyzja człowieka, nie obejście bramki.
- Nie zmieniaj plików spoza tej listy. Nie obchodź bramek. Nie zatwierdzaj niczego za człowieka
  (make zatwierdz, approve albo merge PR): zatrzymaj się i zapytaj mnie.
- Komendy make dłuższe niż 2 minuty uruchamiaj w tle albo z limitem 10 minut i pokazuj postęp.
- Gdy coś pada, pokaż mi fragment logu, zanim zaczniesz poprawiać.

Krok 1. Stan: `fabryka mapa` i `git describe --tags`. Jeśli repo nie stoi na lekcji 10,
uruchom `fabryka lekcja 10` (przestawia repo i klaster, kilka minut; moje zmiany trafią do git stash).
Krok 2. Przeczytaj warsztat/lekcja-10-slad.md: teza i ćwiczenie.
Krok 3. Ćwiczenie:
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
Krok 4. `fabryka sprawdz 10`. Czerwone: przeczytaj komunikat i popraw raz. Nadal czerwone:
`fabryka rozwiazanie 10`, znowu `fabryka sprawdz 10`, i pokaż mi różnicę między Twoją wersją a rozwiązaniem.
Krok 5. Raport po polsku, najwyżej 8 punktów:
- co zmieniłeś i w których plikach,
- który bloczek fabryki się zapalił (porównaj `fabryka mapa` przed i po): podpisana księga i jeden ślad zlecenia w Jaegerze,
- jednym zdaniem: czym jest ta reguła (ślad: słowo, kontekst, ściana, bramka, polityka czy ślad) i dlaczego,
- co mam obejrzeć sam (plik, hala na localhost:2746, Jaeger na localhost:16686).
```

## Finał · Finał: fabryka na GitHubie

`/fabryka-autopilot final` albo `fabryka autopilot final`

```text
Jesteś autopilotem lekcji finałowej warsztatu „Fabryka oprogramowania od podstaw” (Finał: fabryka na GitHubie).
Pracujesz w repo warsztatu (fork confitura-agentic-sdlc) z klastrem kind „fabryka”. Cel: zielone
`fabryka sprawdz final` i krótkie wyjaśnienie, co zmieniło się w fabryce.

Zasady:
- AGENTS.md opisuje reguły dla agenta fabryki (wykonawcy w klastrze), nie dla Ciebie. W tej lekcji świadomie
  zmieniasz: nic w repo poza tym, co robi make github na Twoim forku. To decyzja człowieka, nie obejście bramki.
- Nie zmieniaj plików spoza tej listy. Nie obchodź bramek. Nie zatwierdzaj niczego za człowieka
  (make zatwierdz, approve albo merge PR): zatrzymaj się i zapytaj mnie.
- Komendy make dłuższe niż 2 minuty uruchamiaj w tle albo z limitem 10 minut i pokazuj postęp.
- Gdy coś pada, pokaż mi fragment logu, zanim zaczniesz poprawiać.

Krok 1. Stan: `fabryka mapa` i `git describe --tags`. Jeśli repo nie stoi na lekcji final,
uruchom `fabryka lekcja final` (przestawia repo i klaster, kilka minut; moje zmiany trafią do git stash).
Krok 2. Przeczytaj warsztat/final-github.md: teza i ćwiczenie.
Krok 3. Ćwiczenie:
Finał. Podłącz fabrykę do mojego forka.
0. git remote -v: origin ma być moim forkiem, nie ArturSkowronski/…
   Jeśli nie jest, zatrzymaj się.
1. make github. Jeśli Actions nie dały się włączyć, powiedz mi,
   co kliknąć w zakładce Actions forka.
2. make issue Z=rabat, potem make ciagnij AGENT=replay
3. Co minutę: argo list -n fabryka i gh pr list. Gdy jest PR:
   gh pr checks <nr> --watch (do 10 min).
4. Podaj link do PR i link „Ślad” z jego opisu.
Nie merguj ręcznie i nie zmieniaj ustawień repo poza make github.

Jeśli zostanie czas: ćwiczenie z pochodzeniem (warsztat/final-github.md). Zapytaj mnie, zanim wypchniesz ręczny commit.
Krok 4. `fabryka sprawdz final`. Czerwone: przeczytaj komunikat i popraw raz. Nadal czerwone:
`fabryka rozwiazanie final`, znowu `fabryka sprawdz final`, i pokaż mi różnicę między Twoją wersją a rozwiązaniem.
Krok 5. Raport po polsku, najwyżej 8 punktów:
- co zmieniłeś i w których plikach,
- który bloczek fabryki się zapalił (porównaj `fabryka mapa` przed i po): issue jako zlecenie, PR jako wynik, bramki w GitHub Actions,
- jednym zdaniem: czym jest ta reguła (integracja: słowo, kontekst, ściana, bramka, polityka czy ślad) i dlaczego,
- co mam obejrzeć sam (plik, hala na localhost:2746, Jaeger na localhost:16686).
```

// Deck prezentacyjny warsztatu w stylistyce Visdoma (tokens/visdom.tokens.json:
// rampa stone + emerald, Merriweather / Geist / Geist Mono). Wynik to .pptx,
// bo Keynote otwiera go natywnie, a tekst zostaje edytowalny.
//
//   npm install && node build.mjs
//
// Ilustracje bierze z ../grafiki/out/<scena>-v1.png. Brakujące zastępuje ramką
// z nazwą sceny, żeby deck dało się złożyć przed wygenerowaniem grafik.
import PptxGenJS from "pptxgenjs";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ART = path.join(HERE, "..", "grafiki", "out");
const ART_DECK = path.join(HERE, "..", "grafiki", "deck");
const LOGO = path.join(HERE, "visdom-sdlc.png");

const C = {
  paper: "FFFFFF", canvas: "F5F5F4", sunken: "F0EFED", line: "E7E5E4",
  ink: "0C0A09", ink2: "44403B", ink3: "79716B",
  accent: "10B981", accentInk: "007D5C",
  codeBg: "1C1917", codeInk: "F5F5F4", codeDim: "A6A09B",
  green: "34D399", red: "F28B82", yellow: "E2C46B",
  slowo: "BF6243", kontekst: "4278C7", sciana: "2B8E4C",
  bramka: "7F8A35", polityka: "9A7034", slad: "348275",
};
const F = { display: "Merriweather", body: "Geist", mono: "Geist Mono" };
const W = 13.333, H = 7.5, M = 0.62;

const RULES = [
  ["słowo", "slowo", "Pytaj o to, czego brakuje. Nie proponuj rozwiązań.", "agent-przyjecie.yaml"],
  ["ściana", "sciana", "Do sdlc/, platforma/ i system/architecture nie zapiszesz.", "mcpserver.yaml"],
  ["kontekst", "kontekst", "Rabat, cena i kwota należą do pricing-lib. ADR-0001.", "module.json"],
  ["bramka", "bramka", "Bez kryteriów akceptacji nie dostaniesz zlecenia.", "intake.py"],
  ["ściana", "sciana", "Zadanie dostajesz przez A2A. Klucza do modelu nie zobaczysz.", "fabryka.yaml"],
  ["bramka", "bramka", "Poza pakietem pricing nie liczysz na BigDecimal.", "ArchUnit"],
  ["ściana", "sciana", "Katalog scenarios/ dla ciebie nie istnieje.", "HIDDEN_PATHS"],
  ["bramka", "bramka", "Klucz idempotencji unikalny dla zwrotu, stabilny przy ponowieniu.", "review-rules.json"],
  ["polityka", "polityka", "Ryzyko high i critical czeka na człowieka. Narzędzia: tylko warsztat.", "policy.json · Kyverno"],
  ["ślad", "slad", "Każde Twoje wywołanie jest w podpisanej księdze.", "ledger.py · cosign"],
];

const LEKCJE = [
  { n: 1, tytul: "Klaster i pierwszy agent", scena: "l01-agent", min: "0:07",
    head: "Agent to zasób w klastrze, a nie skrypt na laptopie.",
    teza: "Ma manifest, wersję, właściciela, limity i adres. Kontroler kagent zamienia manifest Agent w Deployment, Service i endpoint A2A. Tym samym mechanizmem, którym od lat wdrażasz serwisy.",
    cw: "Napisz systemMessage agenta „przyjęcie”: dwa do czterech pytań, bez których nie da się napisać testu akceptacyjnego.",
    stopka: "uczciwa luka: port 8083 bez uwierzytelniania" },
  { n: 2, tytul: "Warsztat i narzędzia", scena: "l02-narzedzia", min: "0:17",
    head: "Uprawnienia agenta to lista narzędzi, a nie zdanie w prompcie.",
    teza: "Wykonawca nie ma shella, gita ani tokena do klastra. Ma pięć narzędzi serwera MCP na wspólnym dysku, a każde wywołanie zostawia ślad. Czego agent nie może zrobić, egzekwuje serwer, nie model.",
    cw: "Poproś agenta o zapis do sdlc/policy.json. Zapis przechodzi. Wpisz PROTECTED_PATHS i powtórz.",
    stopka: "najpierw zabierz uprawnienia, potem daj autonomię" },
  { n: 3, tytul: "Kontekst L1–L5", scena: "l03-kontekst", min: "0:27",
    head: "Własność pojęcia wygrywa z częstością słów.",
    teza: "Agent, który przy każdym zleceniu odkrywa repo, jest drogi, wolny i za każdym razem trafia gdzie indziej. Wiedzę kompilujemy raz, deterministycznie, na pięciu poziomach.",
    cw: "Wpisz do pola owns w pricing-lib pojęcia z ADR-0001: rabat, cena, kwota. Sprawdź make route.",
    stopka: "kontekst zmienia wynik, nie prompt" },
  { n: 4, tytul: "Przyjęcie zlecenia", scena: "l04-przyjecie", min: "0:38",
    head: "Fabryka nie przyjmuje zlecenia bez specyfikacji.",
    teza: "Wąskie gardło przesuwa się z pisania kodu na pisanie specyfikacji. Zlecenie bez kryteriów wraca do autora z pytaniami. Sprawdzenie jest deterministyczne, pytania formułuje agent i o niczym nie decyduje.",
    cw: "Dopisz do zlecenia „anulowanie” sekcję Kryteria: stan przed, akcja, stan po. Minimum dwa punkty.",
    stopka: "wąskie gardło przesuwa się w górę strumienia" },
  { n: 5, tytul: "Linia", scena: "l05-linia", min: "0:49",
    head: "Linia to wersjonowany graf, a nie skrypt.",
    teza: "Każdy krok to kontener z tym samym obrazem i tym samym dyskiem, różni się tylko skryptem. Argo rysuje graf, trzyma logi i pozwoli zatrzymać przebieg na człowieku. Agent jest jednym węzłem i jest wymienny.",
    cw: "Ustaw klucz i uruchom make zlecenie Z=rabat. Śledź events.jsonl i ślad w Jaegerze.",
    stopka: "zielony build agenta to jeszcze nie bramka" },
  { n: 6, tytul: "Kontrola jakości", scena: "l06-bramki", min: "1:00",
    head: "Zielony build dowodzi tylko, że model zgadza się sam ze sobą.",
    teza: "Potrzebne są warstwy, na które agent nie ma wpływu: działają poza jego kontenerem, na plikach, których nie może zmienić, i nie czytają jego promptu. ArchUnit, osłabianie testów, sekrety, mutacje.",
    cw: "Napisz regułę ArchUnit: poza pakietem pricing nie wolno liczyć na BigDecimal. Dodaj .because z ADR-0001.",
    stopka: "reguła 3 i reguła 6 mówią to samo. Tylko jedna zatrzymuje build" },
  { n: 7, tytul: "Wyrocznia", scena: "l07-wyrocznia", min: "1:11",
    head: "Holdout zużywa się z każdym użyciem.",
    teza: "Najmocniejsza bramka to scenariusze pisane przez człowieka, których agent nie widzi. Każda informacja zwrotna o scenariuszu to przeciek, dlatego wyrocznia ma dwa poziomy: robocze i sejf.",
    cw: "Wpisz scenarios do HIDDEN_PATHS. Odczyt znika, próba zostaje w śladzie jako holdout.peek.",
    stopka: "kapitałem fabryki jest wyrocznia, nie agent" },
  { n: 8, tytul: "Ryzyko, review i poprawki", scena: "l08-ryzyko", min: "1:22",
    head: "Ryzyko liczy kod, nie model. Model tylko radzi.",
    teza: "Poziom ryzyka decyduje, czy w ogóle pytamy recenzenta. Każda poprawka podnosi ryzyko i przesuwa agenta od wymagania w stronę bramki. Znalezisko blokujące eskaluje do człowieka, nie do poprawki.",
    cw: "Dopisz regułę review typu llm z kryteriami pass i fail. Bez nich model zgaduje.",
    stopka: "model radzi, człowiek decyduje, bramki wymuszają" },
  { n: 9, tytul: "Światło, WIP i polityka", scena: "l09-swiatlo", min: "1:33",
    head: "Człowiek to węzeł z rolą, a nie podatek od każdej zmiany.",
    teza: "Linię, za którą zmiana czeka na człowieka, rysuje wersjonowany plik, a nie nastrój reviewera. Lights-out dostaje tylko zmiana o niskim ryzyku i pokryta scenariuszami. Fabryka ciągnie, nie pcha.",
    cw: "Wepnij suspend w krok „człowiek”. Potem zablokuj narzędzia wykonawcy polityką Kyverno.",
    stopka: "więcej agentów wydłuża lead time, nie zwiększa przepustowości" },
  { n: 10, tytul: "Ślad i hala", scena: "l10-ksiega", min: "1:44",
    head: "Agent może proponować prawa, ale nie może ich uchwalać.",
    teza: "Każde zdarzenie to linia w księdze z hashem poprzedniej. Linia podpisuje księgę kluczem fabryki i zapisuje hash swojej konfiguracji: linia musi być powtarzalna, choć pracownik nie jest.",
    cw: "Zmień jedno słowo w ledger.jsonl i uruchom weryfikację. Łańcuch wskaże linię, podpis przestanie pasować.",
    stopka: "trzy źródła: Jaeger · narzedzia.jsonl · karta.md" },
];

const pptx = new PptxGenJS();
pptx.defineLayout({ name: "V169", width: W, height: H });
pptx.layout = "V169";
pptx.author = "Artur Skowroński"; pptx.company = "VirtusLab";
pptx.title = "Fabryka oprogramowania od podstaw";

// Do decku idzie lekka wersja z grafiki/deck (JPEG 1400 px), a gdy jej nie ma,
// oryginał z grafiki/out. Patrz grafiki/optimize.sh.
const art = (scena) => {
  for (const p of [path.join(ART_DECK, `${scena}.jpg`), path.join(ART, `${scena}-v1.png`)]) {
    if (fs.existsSync(p)) return p;
  }
  return null;
};

function chrome(s, { eyebrow, min, stopka, dot = C.accent, logo = true }) {
  if (eyebrow) {
    s.addShape(pptx.ShapeType.ellipse, { x: M, y: 0.52, w: 0.115, h: 0.115, fill: { color: dot } });
    s.addText(eyebrow.toUpperCase(), {
      x: M + 0.22, y: 0.4, w: 9.5, h: 0.36, fontFace: F.body, fontSize: 11, bold: true,
      color: C.ink3, charSpacing: 1.6, valign: "middle",
    });
  }
  s.addShape(pptx.ShapeType.line, { x: M, y: H - 0.72, w: W - 2 * M, h: 0, line: { color: C.line, width: 0.75 } });
  if (min) s.addText(min, { x: M, y: H - 0.62, w: 4, h: 0.3, fontFace: F.mono, fontSize: 9, color: C.ink3, valign: "middle" });
  if (stopka) s.addText(stopka, { x: W - M - 8.6, y: H - 0.62, w: 8.6, h: 0.3, fontFace: F.mono, fontSize: 9, color: C.ink3, align: "right", valign: "middle" });
  if (logo && fs.existsSync(LOGO)) s.addImage({ path: LOGO, x: W - M - 1.28, y: 0.36, w: 1.28, h: 0.585 });
}

function illustration(s, scena, { x, y, w, h }) {
  const p = art(scena);
  if (p) {
    s.addImage({ path: p, x, y, w, h, sizing: { type: "cover", w, h } });
    s.addShape(pptx.ShapeType.rect, { x, y, w, h, fill: { type: "none" }, line: { color: C.line, width: 0.75 } });
  } else {
    s.addShape(pptx.ShapeType.rect, { x, y, w, h, fill: { color: C.sunken }, line: { color: C.line, width: 0.75, dashType: "dash" } });
    s.addText(`grafika: ${scena}`, { x, y: y + h / 2 - 0.2, w, h: 0.4, fontFace: F.mono, fontSize: 11, color: C.ink3, align: "center" });
  }
}

function ruleStrip(s, idx, y) {
  const [label, kind, text, src] = RULES[idx];
  const col = C[kind];
  s.addShape(pptx.ShapeType.roundRect, { x: M, y, w: W - 2 * M, h: 0.62, rectRadius: 0.06, fill: { color: C.paper }, line: { color: C.line, width: 0.75 } });
  s.addText(`${idx + 1}.`, { x: M + 0.18, y, w: 0.4, h: 0.62, fontFace: F.mono, fontSize: 11, bold: true, color: col, valign: "middle" });
  s.addShape(pptx.ShapeType.roundRect, { x: M + 0.58, y: y + 0.17, w: 0.98, h: 0.28, rectRadius: 0.04, fill: { color: C.paper }, line: { color: col, width: 0.75 } });
  s.addText(label.toUpperCase(), { x: M + 0.58, y: y + 0.17, w: 0.98, h: 0.28, fontFace: F.mono, fontSize: 8, bold: true, color: col, align: "center", valign: "middle" });
  s.addText([{ text, options: { color: C.ink } },
             { text: `   ${src}`, options: { fontFace: F.mono, fontSize: 10, color: C.ink3 } }],
            { x: M + 1.72, y, w: W - 2 * M - 2, h: 0.62, fontFace: F.body, fontSize: 12.5, valign: "middle" });
}

function codeBox(s, lines, { x, y, w, h, size = 11 }) {
  s.addShape(pptx.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.05, fill: { color: C.codeBg }, line: { type: "none" } });
  s.addText(lines.map(([t, c], i) => ({
    text: t, options: { color: c || C.codeInk, breakLine: i < lines.length - 1 },
  })), { x: x + 0.22, y: y + 0.16, w: w - 0.44, h: h - 0.32, fontFace: F.mono, fontSize: size, lineSpacingMultiple: 1.28, valign: "top" });
}

/* 1 — okładka */
{
  const s = pptx.addSlide(); s.background = { color: C.paper };
  illustration(s, "cover-fabryka", { x: 6.55, y: 0, w: W - 6.55, h: H });
  s.addText("CONFITURA 2026 · WARSZTAT 120 MINUT", { x: M, y: 1.5, w: 5.6, h: 0.3, fontFace: F.body, fontSize: 11, bold: true, color: C.accentInk, charSpacing: 1.6 });
  s.addText("Fabryka oprogramowania od podstaw", { x: M, y: 1.95, w: 5.6, h: 2.1, fontFace: F.display, fontSize: 34, bold: true, color: C.ink, lineSpacingMultiple: 1.12 });
  s.addText("Ludzie piszą specyfikacje i scenariusze. Agenci piszą kod. Fabryka decyduje, gdzie zapala światło.", { x: M, y: 4.15, w: 5.5, h: 1, fontFace: F.body, fontSize: 14, color: C.ink2, lineSpacingMultiple: 1.35 });
  s.addText("Artur Skowroński · VirtusLab", { x: M, y: 5.6, w: 5.5, h: 0.3, fontFace: F.mono, fontSize: 11, color: C.ink3 });
  if (fs.existsSync(LOGO)) s.addImage({ path: LOGO, x: M, y: 6.15, w: 1.7, h: 0.777 });
}

/* 2 — zimne otwarcie */
{
  const s = pptx.addSlide(); s.background = { color: C.paper };
  chrome(s, { eyebrow: "Zanim cokolwiek zbudujemy", min: "0:00 · otwarcie", stopka: "odsłona 1", dot: C.slowo });
  s.addText("Ta zmiana jest zielona. Testy przeszły, bramki przeszły, nikt jej nie oglądał.", { x: M, y: 1.0, w: 11.4, h: 1.15, fontFace: F.display, fontSize: 27, bold: true, color: C.ink, lineSpacingMultiple: 1.14 });
  codeBox(s, [
    ["zlecenie: „Rabat 10% dla zamówień powyżej 500 zł”", C.codeDim], [" ", null],
    [" system/orders-service/.../OrderService.java      | 18 ++-", null],
    [" system/orders-service/.../OrderServiceTest.java  | 29 +++", null], [" ", null],
    ["$ mvn -B -q verify", C.green],
    ["Tests run: 47, Failures: 0, Errors: 0", C.green],
    ["ArchUnit 4/4", C.green], [" ", null],
    ["  build ✔   weakening ✔   secrets ✔   mutations ✔ 71%", C.green],
    ["  ryzyko: low   decyzja: lights-out   człowiek: nie pytano", C.codeDim],
  ], { x: M, y: 2.45, w: 7.4, h: 3.55, size: 11 });
  s.addText("Trzy pytania na rozgrzewkę:", { x: 8.3, y: 2.5, w: 4.4, h: 0.35, fontFace: F.body, fontSize: 14, color: C.ink2 });
  ["Do którego modułu trafił rabat?", "Kto zdecydował, że nie trzeba na to patrzeć?", "Co dokładnie pękło?"].forEach((t, i) =>
    s.addText(t, { x: 8.3, y: 3.05 + i * 0.75, w: 4.4, h: 0.65, fontFace: F.body, fontSize: 15, bold: true, color: C.ink, lineSpacingMultiple: 1.25 }));
}

/* 3 — odpowiedź */
{
  const s = pptx.addSlide(); s.background = { color: C.paper };
  chrome(s, { eyebrow: "Odpowiedź", min: "0:02 · otwarcie", stopka: "„na razie pilnuje tego review” to najdroższe zdanie w tym repo", dot: C.slowo });
  s.addText("Fabryka zrobiła dokładnie to, co jej kazano. Problem w tym, że nikt jej niczego nie kazał.", { x: M, y: 1.0, w: 11.4, h: 1.15, fontFace: F.display, fontSize: 27, bold: true, color: C.ink, lineSpacingMultiple: 1.14 });
  codeBox(s, [
    ["docs/adr/0001-arytmetyka-pieniedzy-tylko-w-pricing.md", C.codeDim],
    ["przyjęty 2025-11-04", C.codeDim], [" ", null],
    ["Rabat to implementacja DiscountPolicy w pricing-lib,", C.yellow],
    ["a nie if w serwisie. Serwisy nie wywołują add, subtract,", C.yellow],
    ["multiply, divide ani setScale na BigDecimal.", C.yellow], [" ", null],
    ["Na razie pilnuje tego review, automatycznej reguły", C.red],
    ["jeszcze nie ma.", C.red],
  ], { x: M, y: 2.45, w: 7.4, h: 2.85, size: 11 });
  s.addText("Co było w systemie, a czego agent nie dostał:", { x: 8.3, y: 2.5, w: 4.4, h: 0.35, fontFace: F.body, fontSize: 13, color: C.ink2 });
  [["ADR-0001", "nie w kontekście zlecenia"], ["reguła ArchUnit", "nie istnieje"],
   ["scenariusz", "nikt nie napisał"], ["człowiek", "polityka nie kazała pytać"]].forEach(([a, b], i) => {
    s.addText("✘", { x: 8.3, y: 3.0 + i * 0.62, w: 0.25, h: 0.35, fontFace: F.body, fontSize: 13, bold: true, color: C.slowo });
    s.addText([{ text: a + "  ", options: { bold: true, color: C.ink } }, { text: b, options: { color: C.ink3 } }],
      { x: 8.62, y: 3.0 + i * 0.62, w: 4.1, h: 0.35, fontFace: F.body, fontSize: 12.5, valign: "middle" });
  });
  s.addText("Przez najbliższe dwie godziny zamienimy każde takie zdanie w coś, czego agent nie może zignorować.",
    { x: M, y: 5.55, w: 11.4, h: 0.5, fontFace: F.body, fontSize: 14, bold: true, color: C.ink });
}

/* 4 — karta wykonawcy, zapowiedź */
{
  const s = pptx.addSlide(); s.background = { color: C.paper };
  chrome(s, { eyebrow: "Nić przewodnia · karta wykonawcy", min: "0:05 · otwarcie", stopka: "sześć rodzajów reguł · dziesięć lekcji" });
  s.addText("Każda lekcja dopisuje agentowi jedną regułę. Na koniec policzymy, ile z nich to tylko słowa.", { x: M, y: 1.0, w: 11.4, h: 1.15, fontFace: F.display, fontSize: 27, bold: true, color: C.ink, lineSpacingMultiple: 1.14 });
  s.addText("Agent, którego dziś zatrudniamy, na starcie nie wie nic. Po każdym ćwiczeniu dopisujemy mu jedną regułę i zaznaczamy, czym ta reguła jest naprawdę. Ta różnica jest całą tezą warsztatu: reguła, którą model może zignorować, i reguła, która go o zdanie nie pyta, wyglądają w dokumentacji identycznie.",
    { x: M, y: 2.4, w: 5.3, h: 2.2, fontFace: F.body, fontSize: 14, color: C.ink2, lineSpacingMultiple: 1.35 });
  const kinds = [["słowo", "slowo", "instrukcja w prompcie, model może ją zignorować"],
    ["kontekst", "kontekst", "agent to czyta, zanim dotknie kodu"],
    ["ściana", "sciana", "serwer albo klaster odmawia wykonania"],
    ["bramka", "bramka", "kod sprawdza wynik poza agentem"],
    ["polityka", "polityka", "plik decyduje, kto patrzy i ile naraz"],
    ["ślad", "slad", "zapisane, choćby agent nie chciał"]];
  s.addShape(pptx.ShapeType.roundRect, { x: 6.35, y: 2.3, w: W - M - 6.35, h: 3.5, rectRadius: 0.06, fill: { color: C.paper }, line: { color: C.line, width: 0.75 } });
  kinds.forEach(([label, kind, desc], i) => {
    const y = 2.55 + i * 0.53, col = C[kind];
    s.addShape(pptx.ShapeType.roundRect, { x: 6.6, y: y + 0.06, w: 0.98, h: 0.28, rectRadius: 0.04, fill: { color: C.paper }, line: { color: col, width: 0.75 } });
    s.addText(label.toUpperCase(), { x: 6.6, y: y + 0.06, w: 0.98, h: 0.28, fontFace: F.mono, fontSize: 8, bold: true, color: col, align: "center", valign: "middle" });
    s.addText(desc, { x: 7.72, y, w: 4.6, h: 0.4, fontFace: F.body, fontSize: 12, color: C.ink3, valign: "middle" });
  });
}

/* 5–14 — lekcje */
LEKCJE.forEach((L, i) => {
  const s = pptx.addSlide(); s.background = { color: C.paper };
  chrome(s, { eyebrow: `Lekcja ${L.n} · ${L.tytul}`, min: `${L.min} · lekcja ${L.n}`, stopka: L.stopka });
  s.addText(L.head, { x: M, y: 1.05, w: 6.5, h: 1.5, fontFace: F.display, fontSize: 24, bold: true, color: C.ink, lineSpacingMultiple: 1.16 });
  s.addText(L.teza, { x: M, y: 2.52, w: 6.4, h: 1.9, fontFace: F.body, fontSize: 13.5, color: C.ink2, lineSpacingMultiple: 1.38 });
  s.addText("ĆWICZENIE", { x: M, y: 4.48, w: 6.4, h: 0.28, fontFace: F.body, fontSize: 10, bold: true, color: C.accentInk, charSpacing: 1.4 });
  s.addText(L.cw, { x: M, y: 4.78, w: 6.4, h: 0.9, fontFace: F.body, fontSize: 12.5, color: C.ink, lineSpacingMultiple: 1.3 });
  illustration(s, L.scena, { x: 7.3, y: 1.05, w: 5.413, h: 3.609 });
  ruleStrip(s, i, 6.05);
});

/* 15 — puenta */
{
  const s = pptx.addSlide(); s.background = { color: C.paper };
  chrome(s, { eyebrow: "Zamknięcie · rozstrzygnięcie zakładu", min: "1:53 · zamknięcie", stopka: "puenta: prompt to jedna dziesiąta fabryki" });
  s.addText("Dziesięć reguł. Jedna z nich jest zdaniem, które model może zignorować.", { x: M, y: 1.0, w: 8.2, h: 1.15, fontFace: F.display, fontSize: 26, bold: true, color: C.ink, lineSpacingMultiple: 1.14 });
  RULES.forEach(([label, kind, text], i) => {
    const col = C[kind], x = i < 5 ? M : 4.72, y = 2.2 + (i % 5) * 0.5;
    s.addText(`${i + 1}.`, { x, y, w: 0.46, h: 0.4, fontFace: F.mono, fontSize: 10, color: C.ink3, valign: "middle" });
    s.addShape(pptx.ShapeType.roundRect, { x: x + 0.44, y: y + 0.06, w: 0.9, h: 0.27, rectRadius: 0.04, fill: { color: C.paper }, line: { color: col, width: 0.75 } });
    s.addText(label.toUpperCase(), { x: x + 0.44, y: y + 0.06, w: 0.9, h: 0.27, fontFace: F.mono, fontSize: 7.5, bold: true, color: col, align: "center", valign: "middle" });
    s.addText(text, { x: x + 1.44, y, w: 2.62, h: 0.4, fontFace: F.body, fontSize: 10.5, color: C.ink, valign: "middle", lineSpacingMultiple: 1.1 });
  });
  const tally = [["1 ×", "słowo", "slowo"], ["1 ×", "kontekst", "kontekst"], ["3 ×", "ściana", "sciana"],
    ["3 ×", "bramka", "bramka"], ["1 ×", "polityka", "polityka"], ["1 ×", "ślad", "slad"]];
  tally.forEach(([n, label, kind], i) =>
    s.addText([{ text: n + " ", options: { bold: true } }, { text: label, options: {} }],
      { x: M + (i % 3) * 1.45, y: 4.92 + Math.floor(i / 3) * 0.42, w: 1.4, h: 0.38, fontFace: F.mono, fontSize: 12, color: C[kind], valign: "middle" }));
  s.addText("Dziewięć z dziesięciu reguł działa, nawet jeśli model ma gorszy dzień, ktoś podmieni prompt albo biblioteka w logu każe mu zignorować wcześniejsze instrukcje. W dokumentacji wszystkie dziesięć wygląda tak samo.",
    { x: M, y: 5.88, w: 8.2, h: 0.85, fontFace: F.body, fontSize: 13, color: C.ink2, lineSpacingMultiple: 1.32 });
  illustration(s, "l11-karta", { x: 9.23, y: 1.05, w: 3.48, h: 2.32 });
}

/* 16 — na poniedziałek */
{
  const s = pptx.addSlide(); s.background = { color: C.paper };
  chrome(s, { eyebrow: "Zamknięcie · co zabrać na poniedziałek", min: "1:55 · zamknięcie", stopka: "kind · kagent · MCP · A2A · Argo · Kyverno · OTel · cosign" });
  s.addText("Dziesięć plików, które dziś zmieniłeś, to cała fabryka. Reszta to projekty Linux Foundation.", { x: M, y: 1.0, w: 11.4, h: 1.15, fontFace: F.display, fontSize: 26, bold: true, color: C.ink, lineSpacingMultiple: 1.14 });
  const pliki = [["agent-przyjecie.yaml", "agent bez narzędzi tylko pyta"], ["mcpserver.yaml · PROTECTED", "gdzie agent nie pisze"],
    ["module.json owns", "kto jest właścicielem pojęcia"], ["zlecenia/*.md Kryteria", "co przyjmuje linia"],
    ["make klucz", "klucz widzi tylko pod agenta"], ["ArchitectureRulesTest", "reguła jest bramką i kontekstem"],
    ["mcpserver.yaml · HIDDEN", "czego agent nie czyta"], ["review-rules.json", "review z kryteriami pass i fail"],
    ["fabryka.yaml · Kyverno", "gdzie stoi człowiek"], ["ledger.jsonl", "co się stało, podpisane"]];
  pliki.forEach(([a, b], i) => {
    const y = 2.35 + i * 0.4;
    s.addShape(pptx.ShapeType.line, { x: M, y: y + 0.38, w: 6.9, h: 0, line: { color: C.line, width: 0.5 } });
    s.addText(`${i + 1}`, { x: M, y, w: 0.3, h: 0.38, fontFace: F.mono, fontSize: 10, color: C.ink3, valign: "middle" });
    s.addText(a, { x: M + 0.36, y, w: 3.1, h: 0.38, fontFace: F.mono, fontSize: 10.5, color: C.ink, valign: "middle" });
    s.addText(b, { x: M + 3.5, y, w: 3.4, h: 0.38, fontFace: F.body, fontSize: 11.5, color: C.ink2, valign: "middle" });
  });
  s.addText("Dwie metryki na poniedziałek", { x: 8.1, y: 2.35, w: 4.6, h: 0.4, fontFace: F.body, fontSize: 15, bold: true, color: C.ink });
  s.addText([{ text: "Minuty człowieka na przyjętą zmianę", options: { bold: true, color: C.ink } },
             { text: ", liczone także w górę strumienia: specyfikacje, scenariusze, andony. Nie tylko review.", options: { color: C.ink2 } }],
    { x: 8.1, y: 2.9, w: 4.6, h: 1.2, fontFace: F.body, fontSize: 13, lineSpacingMultiple: 1.35 });
  s.addText([{ text: "Ucieczki", options: { bold: true, color: C.ink } },
             { text: ": defekty, które przeszły przez fabrykę. Bez atrybucji defektu do zmiany nie ma z czego zarobić autonomii.", options: { color: C.ink2 } }],
    { x: 8.1, y: 4.15, w: 4.6, h: 1.3, fontFace: F.body, fontSize: 13, lineSpacingMultiple: 1.35 });
}

/* 17 — zamknięcie */
{
  const s = pptx.addSlide(); s.background = { color: C.ink };
  s.addText("Pytanie nie brzmi, czy zbudujesz fabrykę. Tylko gdzie zapalisz światło i czym zmierzysz resztę.",
    { x: M, y: 2.2, w: 9.6, h: 2.6, fontFace: F.display, fontSize: 32, bold: true, color: C.paper, lineSpacingMultiple: 1.16 });
  s.addText("github.com/ArturSkowronski/confitura-agentic-sdlc", { x: M, y: 5.2, w: 8, h: 0.4, fontFace: F.mono, fontSize: 13, color: C.accent });
  s.addText("Artur Skowroński · VirtusLab", { x: M, y: 5.68, w: 8, h: 0.35, fontFace: F.mono, fontSize: 11, color: C.ink3 });
}

const out = path.join(HERE, "fabryka-od-podstaw.pptx");
await pptx.writeFile({ fileName: out });
const n = LEKCJE.filter((L) => art(L.scena)).length + (art("cover-fabryka") ? 1 : 0) + (art("l11-karta") ? 1 : 0);
console.log(`zapisane: ${path.relative(process.cwd(), out)}  ·  slajdów: 17  ·  grafik wstawionych: ${n}/12`);

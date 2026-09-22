# Deck prezentacyjny w stylistyce Visdoma

Siedemnaście slajdów na projektor: zimne otwarcie, dziesięć lekcji po jednym slajdzie,
puenta z kartą wykonawcy i zamknięcie. To **nie** jest przewodnik uczestnika, ten jest
w `warsztat/przewodnik.html` i ma 48 slajdów z komendami i wyjściem.

```bash
npm install
node build.mjs      # -> fabryka-od-podstaw.pptx
```

Plik wychodzi jako `.pptx`, bo Keynote otwiera go natywnie (Plik → Otwórz), a tekst
zostaje edytowalny. Prawdziwego `.key` nie da się złożyć bez zainstalowanego Keynote.

## Skąd się bierze wygląd

| Element | Źródło |
|---|---|
| Kolory | `visdom-materials/tokens/visdom.tokens.json`: rampa stone + emerald |
| Typografia | Merriweather (nagłówki), Geist (tekst), Geist Mono (kod i etykiety) |
| Logo | `visdom-materials/assets/logos/visdom-logo-sdlc-light.svg`, zrasteryzowane do `visdom-sdlc.png` |
| Ilustracje | `../grafiki/out/<scena>-v1.png`, styl JVM Weekly |

Brakującą ilustrację generator zastępuje ramką z nazwą sceny, więc deck składa się
także przed wygenerowaniem grafik.

## Czcionki

Geist i Merriweather muszą być zainstalowane w systemie, inaczej Keynote podstawi
własne. LibreOffice podstawia je nawet wtedy, gdy są, więc PDF z `soffice` służy do
sprawdzania układu, a nie typografii.

# Deck prezentacyjny w stylistyce Visdoma

Siedemnaście slajdów na projektor: zimne otwarcie, dziesięć lekcji po jednym slajdzie,
puenta z kartą wykonawcy i zamknięcie. To **nie** jest przewodnik uczestnika, ten jest
w `warsztat/przewodnik.html` i ma 48 slajdów z komendami i wyjściem.

```bash
npm install
node build.mjs      # -> fabryka-od-podstaw.pptx
./to-key.sh         # -> fabryka-od-podstaw.key (konwertuje sam Keynote)
```

Generator pisze `.pptx`, bo żadna biblioteka nie umie zapisać formatu Apple. Natywny
`.key` robi `to-key.sh`: otwiera pptx w Keynote i zapisuje jako `.key`. Sprawdzone na
Keynote 15.1.1, wynik ma 17 slajdów i poprawne kroje.

Aplikacja bywa przemianowana na dysku (tutaj `Keynote Creator Studio.app`, ale
identyfikator pakietu to `com.apple.Keynote` i podpis jest Apple), dlatego skrypt
adresuje ją przez `application id`, a nie przez nazwę.

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
własne. LibreOffice podstawia je nawet wtedy, gdy są, więc PDF z `soffice` sprawdza
układ, a nie typografię. Do sprawdzenia krojów eksportuj PDF z samego Keynote.

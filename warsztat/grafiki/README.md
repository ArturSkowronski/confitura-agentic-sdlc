# Ilustracje warsztatu

Dwanaście scen w stylu JVM Weekly: druk sitowy, płaskie farby, halftone, cztery do
pięciu kolorów i ta sama postać co w newsletterze. Styl i referencja postaci pochodzą
z `~/Priv/jvm-weekly` (`tools/illugen.py`, `grafiki/prompts.md`); referencji nie
kopiujemy do tego repo.

```bash
python3 warsztat/grafiki/gen.py --list
python3 warsztat/grafiki/gen.py cover-fabryka --dry-run     # sam prompt
python3 warsztat/grafiki/gen.py --all                       # wszystkie sceny
python3 warsztat/grafiki/gen.py l06-bramki --variants 3     # trzy kandydatki
```

Klucz bierze się z `OPENAI_API_KEY`, potem z `~/.config/openai/key`. Nigdzie nie jest
zapisywany. `--key-from file` pomija środowisko, co przydaje się, gdy w środowisku
siedzi klucz bez kredytów.

Każdy PNG dostaje obok plik `.txt` z modelem, ustawieniami i pełnym promptem, żeby
dobry wynik dało się powtórzyć, a zły zdiagnozować. Deck bierze wariant `-v1`; jeśli
wolisz inny, przemianuj go na `-v1` albo podmień plik.

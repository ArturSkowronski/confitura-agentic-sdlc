Temat: Confitura 2026, warsztat „fabryka oprogramowania”: setup przed [piątek 25.09 / sobota 26.09]

Cześć,

dzięki za zapis na warsztat „Zbuduj prawdziwą agentową platformę SDLC od podstaw”.
Widzimy się [DZIEŃ] o [GODZINA] w sali [SALA], ADN Conference Center, Grzybowska 56.

Mamy 120 minut i chcę, żebyśmy spędzili je na budowaniu, a nie na instalowaniu. Dlatego
proszę o jedną rzecz przed warsztatem: setup, około 15 minut, najlepiej w domu, a nie na
konferencyjnym Wi-Fi.

Instrukcja: https://github.com/ArturSkowronski/confitura-agentic-sdlc/blob/main/SETUP.md

W skrócie:

1. Sklonuj repozytorium.
2. Uruchom `make bootstrap`. Powstanie Twoje własne repo na GitHubie z całym pipeline'em.
3. Uruchom `make doctor`. Wszystko ma być zielone.

Co będziemy robić: zbudujemy fabrykę oprogramowania. Ludzie piszą specyfikacje i scenariusze,
agenci piszą kod, a fabryka decyduje, co przyjąć bez człowieka, co odesłać do poprawki, a przy
czym zatrzymać linię. Po drodze: przyjęcie zlecenia, kontekst organizacji, scenariusze, których
agent nie widzi, pętla poprawek, limit WIP i podpisana księga zdarzeń. Wszystko na open source,
a runnerem jest GitHub Actions. W środku jest sklep z konfiturami w Javie, z historią gita,
ADR-ami i jednym incydentem, który wróci w trakcie warsztatu.

Weź ze sobą:

- naładowany laptop, na którym możesz instalować programy,
- telefon do 2FA na GitHubie.

Klucza do modelu nie potrzebujesz, dostaniesz go na miejscu. Do tego czasu agent działa
w trybie replay, bez modelu.

Jeśli `make doctor` świeci na czerwono, odpisz na tego maila z wynikiem. Wolę to naprawić
w środę niż w trakcie warsztatu.

Do zobaczenia,
Artur Skowroński

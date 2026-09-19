Temat: Confitura 2026, warsztat „fabryka oprogramowania”: setup przed sobotą 26.09

Cześć,

dzięki za zapis na warsztat „Zbuduj prawdziwą agentową platformę SDLC od podstaw”.
Widzimy się w sobotę 26.09 o 10:15 w sali [SALA], ADN Conference Center, Grzybowska 56.

Mamy 120 minut i chcę, żebyśmy spędzili je na budowaniu, a nie na instalowaniu. Dlatego
proszę o jedną rzecz przed warsztatem: setup, około 20 minut, najlepiej w domu, a nie na
konferencyjnym Wi-Fi. Cała fabryka działa w klastrze na Twoim laptopie.

Instrukcja: https://github.com/ArturSkowronski/confitura-agentic-sdlc/blob/main/SETUP.md

W skrócie:

1. Zainstaluj Dockera, kind, kubectl, helm, argo, cosign, Javę 21 i Mavena.
2. Sklonuj repozytorium i uruchom `make klaster`, potem `make setup`.
3. Uruchom `make doctor`. Wszystko ma być zielone.

Co będziemy robić: zbudujemy fabrykę oprogramowania w dziesięciu lekcjach, commit po commicie.
Ludzie piszą specyfikacje i scenariusze, agenci piszą kod, a fabryka decyduje, co przyjąć bez
człowieka, co odesłać do poprawki, a przy czym zatrzymać linię. Wszystko na projektach Linux
Foundation: kagent orkiestruje agentów, Argo Workflows prowadzi linię, Kyverno pilnuje
deklaracji, cosign podpisuje księgę, Jaeger pokazuje ślady. W środku jest sklep z konfiturami
w Javie, z historią gita, ADR-ami i jednym incydentem, który wróci w trakcie warsztatu.

Weź ze sobą:

- naładowany laptop (16 GB RAM), na którym możesz instalować programy, z gotowym klastrem,
- dobry humor. Klucz do modelu dostaniesz na miejscu.

Jeśli `make doctor` jest czerwony i nie wiesz dlaczego, odpisz na tego maila z wynikiem.

Do zobaczenia,
Artur

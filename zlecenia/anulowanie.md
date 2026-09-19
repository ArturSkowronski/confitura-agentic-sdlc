# Anulowanie zamówienia

Klient może anulować zamówienie, dopóki nie jest opłacone. Trzeba to dodać w serwisie
zamówień, bo teraz dzwonią na infolinię.

Kryteria:
- zamówienie w stanie NEW: anulowanie zmienia stan na CANCELLED, płatność nie jest tworzona
- zamówienie w stanie PAID: anulowanie jest odrzucone z komunikatem „zamówienie jest opłacone”
- zamówienie już CANCELLED: ponowne anulowanie nic nie zmienia i nie zgłasza błędu

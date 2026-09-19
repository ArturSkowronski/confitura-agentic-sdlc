# Rabat 10% dla zamówień powyżej 500 zł

Klienci, którzy zamówią konfitury za więcej niż 500 zł, dostają 10% rabatu od całego koszyka.
Rabat działa w konfiguracji produkcyjnej (`OrdersModule.production()`) i jest widoczny
w odpowiedzi `OrderController.place(...)` w polu `discount`.

Kryteria:
- 500,00 zł: bez rabatu
- 500,01 zł: rabat 50,00 zł
- 600,00 zł: rabat 60,00 zł, do zapłaty 540,00 zł

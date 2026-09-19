# Zwroty częściowe

Klient kupił trzy słoiki, jeden przyszedł rozbity. Chcemy zwrócić część kwoty płatności,
a nie całość.

Kontrakt: `PaymentController.refundPartially(String paymentId, String amount)` zwraca
`RefundResponse` z łączną zwróconą kwotą w polu `refunded`.

Kryteria:
- płatność 90,00 zł, zwrot 30,00 zł: zwrócono 30,00 zł
- kolejne zwroty częściowe tej samej płatności się sumują
- nie da się zwrócić więcej, niż zostało do zwrotu

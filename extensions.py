import requests
import json
from config import EXCHANGE_API_URL


class APIException(Exception):  # кастомное исключение для обработки ошибок
    pass

class CurrencyConverter:
    @staticmethod
    def get_price(base: str, quote: str, amount: float):
        try:
            amount = float(amount)
            if amount <= 0:
                raise APIException("Сумма валюты не может быть отрицательной !")
        except ValueError:
            raise APIException("Некорректное значение валюты !")

        base, quote = base.upper(), quote.upper()

        response = requests.get(f'{EXCHANGE_API_URL}{base}')
        if response.status_code != 200:
            raise APIException("Ошибка получения данных !")

        try:
            rates = response.json()["rates"]
            if quote not in rates:
                raise APIException(f'Валюта {quote} не найдена !')

            conversion_rate = rates[quote]
            total = conversion_rate * amount
            return f'{amount} {base} = {total:.2f} {quote}'
        except KeyError:
            raise APIException("Ошибка обработки данных о валюте !")

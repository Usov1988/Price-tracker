from datetime import datetime
import json
import os
from bs4 import BeautifulSoup
import requests


def check_prices():
  # Список товаров для примера (в дальнейшем сюда можно добавить категории с 21vek)
  # Сейчас здесь заложена логика имитации поиска аномалий для демонстрации
  found_deals = [
      {
          "title": "Пример: Смартфон (Аномальная цена)",
          "store_price": 500,
          "market_price": 1200,
          "store_url": "https://www.21vek.by",
          "catalog_url": "https://catalog.onliner.by",
          "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
      }
  ]

  # Здесь в будущем будет реальный код парсинга 21vek и запросов к Onliner API

  # Сохраняем результаты в JSON-файл, который будет читать сайт
  data = []
  if os.path.exists("prices.json"):
    try:
      with open("prices.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    except:
      pass

  # Добавляем новые находки ( избегая дубликатов)
  for deal in found_deals:
    if deal not in data:
      data.insert(0, deal)

  # Оставляем только последние 50 записей
  data = data[:50]

  with open("prices.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
  check_prices()
  

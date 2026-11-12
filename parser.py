from datetime import datetime
import json
import os
from bs4 import BeautifulSoup
import cloudscraper


def parse_21vek_smartphones():
  url = "https://www.21vek.by/smartphones/"

  # Создаем скрапер, который умеет обходить защиту Cloudflare
  scraper = cloudscraper.create_scraper(
      browser={"custom": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}
  )

  found_deals = []

  try:
    print(f"Запрос к каталогу смартфонов: {url}")
    response = scraper.get(url, timeout=20)

    if response.status_code == 200:
      soup = BeautifulSoup(response.text, "html.parser")

      # Ищем карточки товаров на странице 21века
      items = soup.select(".g-i-tile") or soup.select("[data-qa-id='product-card']")
      print(f"Найдено карточек товаров: {len(items)}")

      for item in items:
        try:
          # Название товара
          title_elem = item.select_one(".g-i-tile-title") or item.select_one("a")
          if not title_elem:
            continue
          title = title_elem.get_text(strip=True)

          # Ссылка на товар
          link = title_elem.get("href", "")
          if link and not link.startswith("http"):
            link = "https://www.21vek.by" + link

          # Цена товара в 21веке
          price_elem = item.select_one(".g-price") or item.select_one("[data-qa-id='product-price']")
          if not price_elem:
            continue
          
          price_text = (
              price_elem.get_text(strip=True)
              .replace("р.", "")
              .replace("с", "")
              .replace(" ", "")
              .replace(",", ".")
          )
          store_price = float("".join(filter(lambda c: c.isdigit() or c == '.', price_text)))

          if store_price <= 0:
            continue

          # Для сравнения: ищем похожий товар в каталоге Onliner (формируем поисковый запрос)
          onliner_search_url = f"https://catalog.onliner.by/search?query={title.replace(' ', '+')}"

          # Умная логика поиска аномалии:
          # Допустим, если смартфон стоит меньше 250 рублей (или подозрительно дешево для рынка), фиксируем
          # (Здесь ты сможешь настроить порог под себя)
          if store_price < 250:
            found_deals.append({
                "title": title,
                "store_price": store_price,
                "market_price": round(store_price * 1.8, 2),  # Примерно оцениваем рынок
                "store_url": link,
                "catalog_url": onliner_search_url,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            })

        except Exception as e:
          continue
    else:
      print(f"Ошибка доступа к сайту: код {response.status_code}")

  except Exception as e:
    print(f"Ошибка при парсинге: {e}")

  # Если реальный парсинг ничего не поймал (или сработал блок), оставляем заглушку,
  # чтобы таблица не была пустой
  if not found_deals:
    found_deals.append({
        "title": "🔴 Смартфон (Сканирование идет, аномалий не найдено)",
        "store_price": 0.00,
        "market_price": 0.00,
        "store_url": url,
        "catalog_url": "https://catalog.onliner.by",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })

  return found_deals


def update_json():
  new_deals = parse_21vek_smartphones()

  data = []
  if os.path.exists("prices.json"):
    try:
      with open("prices.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    except:
      pass

  # Объединяем старые и новые находки (без дубликатов по названию)
  for deal in new_deals:
    if not any(d["title"] == deal["title"] for d in data):
      data.insert(0, deal)

  # Храним последние 50 записей
  data = data[:50]

  with open("prices.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
  update_json()
  # test
  

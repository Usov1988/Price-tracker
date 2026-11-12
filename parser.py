import json
from bs4 import BeautifulSoup
import cloudscraper

scraper = cloudscraper.create_scraper()
url = "https://www.21vek.by/mobile/"

print(f"Запрос к сайту: {url}")
response = scraper.get(url)

data_to_save = []

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Ищем карточки товаров по основным тегам и классам 21vek
    items = soup.find_all('li', class_='g-card')
    if not items:
        items = soup.select('div[class*="card"]')

    for item in items[:10]: # Первые 10 товаров
        try:
            # Название товара (пробуем разные варианты селекторов)
            title_elem = item.find('span', {'data-testid': 'name'}) or item.find('a', class_='g-card-image') or item.find('img')
            title = ""
            if title_elem:
                title = title_elem.get('alt') or title_elem.get_text(strip=True)
            
            if not title:
                # Если в теге изображения или ссылки пусто, ищем текстовый заголовок
                title_tag = item.find(['span', 'a'], class_=lambda x: x and 'name' in x)
                title = title_tag.get_text(strip=True) if title_tag else ""

            # Цена товара
            price_elem = item.find('span', class_='g-price-current') or item.find('p', class_='g-price') or item.find('span', class_='price__value')
            price = price_elem.get_text(strip=True) if price_elem else ""
            
            if title and price:
                data_to_save.append({
                    "title": title,
                    "price": price
                })
        except Exception as e:
            continue

# Если по какой-то причине элементы не распарсились, сохраним детальный отчет
if not data_to_save:
    data_to_save.append({
        "title": "Связь есть (200), но селекторы не нашли товары",
        "price": "Нужна корректировка класса"
    })

with open('prices.json', 'w', encoding='utf-8') as f:
    json.dump(data_to_save, f, ensure_ascii=False, indent=4)

print("Парсинг завершен.")

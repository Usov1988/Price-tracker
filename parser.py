import json
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup
import cloudscraper

scraper = cloudscraper.create_scraper()
url = "https://www.21vek.by/mobile/"

response = scraper.get(url)
data_to_save = []

tz_minsk = timezone(timedelta(hours=3))
current_date = datetime.now(tz_minsk).strftime("%Y-%m-%d %H:%M")

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Ищем карточки товаров на странице
    items = soup.find_all('li', class_=lambda x: x and 'card' in x)
    if not items:
        items = soup.select('.g-card, [data-testid="card"]')

    for item in items[:15]: # Собираем первые 15 товаров
        try:
            title_elem = item.find(['span', 'a', 'div'], class_=lambda x: x and ('name' in x or 'title' in x))
            title = title_elem.get_text(strip=True) if title_elem else ""

            price_elem = item.find(['p', 'span', 'div'], class_=lambda x: x and ('price' in x))
            price = price_elem.get_text(strip=True) if price_elem else ""
            
            link_elem = item.find('a', href=True)
            product_link = link_elem['href'] if link_elem else url
            if product_link.startswith('/'):
                product_link = "https://www.21vek.by" + product_link

            if title and price:
                data_to_save.append({
                    "title": title,
                    "price": price,
                    "price_21vek": price,
                    "price_onliner": "-",
                    "date": current_date,
                    "link_21vek": product_link,
                    "link_onliner": "https://catalog.onliner.by/"
                })
        except Exception:
            continue

# Сохраняем результат (файл останется пустым [], если товары не найдены)
with open('prices.json', 'w', encoding='utf-8') as f:
    json.dump(data_to_save, f, ensure_ascii=False, indent=4)
    

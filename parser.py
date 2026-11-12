import json
from datetime import datetime
from bs4 import BeautifulSoup
import cloudscraper

scraper = cloudscraper.create_scraper()
url = "https://www.21vek.by/mobile/"

print(f"Запрос к сайту: {url}")
response = scraper.get(url)

data_to_save = []
current_date = datetime.now().strftime("%Y-%m-%d %H:%M")

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Ищем карточки товаров
    items = soup.find_all('li', class_='g-card') or soup.select('div[class*="card"]')

    for item in items[:10]:
        try:
            # Название товара
            title_elem = item.find('span', {'data-testid': 'name'}) or item.find('a', class_='g-card-image')
            title = ""
            if title_elem:
                title = title_elem.get('alt') or title_elem.get_text(strip=True)
            
            if not title:
                title_tag = item.find(['span', 'a'], class_=lambda x: x and 'name' in x)
                title = title_tag.get_text(strip=True) if title_tag else "Смартфон"

            # Цена 21vek
            price_elem = item.find('span', class_='g-price-current') or item.find('p', class_='g-price') or item.find('span', class_='price__value')
            price = price_elem.get_text(strip=True) if price_elem else "Уточняется"
            
            # Ссылка на товар
            link_elem = item.find('a', href=True)
            product_link = link_elem['href'] if link_elem else url
            if product_link.startswith('/'):
                product_link = "https://www.21vek.by" + product_link

            if title:
                data_to_save.append({
                    "title": title,
                    "price_21vek": price,
                    "price_onliner": "-",       # Заглушка для каталога Onliner, если не парсится отдельно
                    "date": current_date,
                    "link_21vek": product_link,
                    "link_onliner": "https://catalog.onliner.by/"
                })
        except Exception as e:
            continue

# Если элементы не нашлись, выводим понятную строку в правильном формате таблицы
if not data_to_save:
    data_to_save.append({
        "title": "Связь с 21vek есть (200), требуется уточнить селекторы",
        "price_21vek": "0 BYN",
        "price_onliner": "-",
        "date": current_date,
        "link_21vek": url,
        "link_onliner": "#"
    })

# Сохраняем в prices.json
with open('prices.json', 'w', encoding='utf-8') as f:
    json.dump(data_to_save, f, ensure_ascii=False, indent=4)

print("Парсинг и формирование данных завершены.")

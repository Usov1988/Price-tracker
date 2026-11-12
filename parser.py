import json
from bs4 import BeautifulSoup
import cloudscraper

# Создаем скрапер, который умеет обходить Cloudflare на 21vek.by
scraper = cloudscraper.create_scraper()

# Ссылка на категорию смартфонов (или конкретный товар для теста) на 21vek.by
url = "https://www.21vek.by/mobile/"

print(f"Запрос к сайту: {url}")
response = scraper.get(url)

data_to_save = []

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Ищем карточки товаров (структура селекторов может зависеть от верстки каталога 21vek)
    # Ниже универсальный пример поиска блоков товаров
    items = soup.find_all('div', class_='g-card') # или актуальный класс карточки товара
    
    if not items:
        # Резервный поиск по тегам, если класс изменился
        items = soup.select('.result__item')

    for item in items[:10]: # Берем первые 10 товаров для примера
        try:
            # Название товара
            title_elem = item.find('span', {'data-testid': 'name'}) or item.find('a', class_='g-card-image')
            title = title_elem.get_text(strip=True) if title_elem else "Смартфон"
            
            # Цена
            price_elem = item.find('span', class_='g-price-current') or item.find('div', class_='price__current')
            price = price_elem.get_text(strip=True) if price_elem else "Цена не найдена"
            
            if title and price:
                data_to_save.append({
                    "title": title,
                    "price": price
                })
        except Exception as e:
            continue

# Если по какой-то причине селекторы на сайте не отдали товары (например, защита выдала капчу),
# чтобы файл не был пустым или со старым примером, зафиксируем статус или запишем актуальную попытку
if not data_to_save:
    # Записываем структуру с актуальным статусом проверки
    data_to_save = [
        {"title": "Проверка связи с 21vek.by", "price": f"Статус ответа: {response.status_code}"}
    ]

# Сохраняем результат в prices.json
with open('prices.json', 'w', encoding='utf-8') as f:
    json.dump(data_to_save, f, ensure_ascii=False, indent=4)

print("Парсинг завершен, файл prices.json обновлен.")

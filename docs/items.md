# Документация API Товары

Модуль `PlayerokItemsApi` предоставляет функционал для управления товарами (лотами) на платформе Playerok. Он позволяет получать информацию о товарах, копировать товары, повышать их приоритет и возобновлять завершенные лоты.

## Инициализация

```python
from api.items import PlayerokItemsApi

api = PlayerokItemsApi(cookies_file="cookies.json", logger=False)
```

- **cookies_file**: Путь к файлу с cookies для аутентификации (по умолчанию `cookies.json`).
- **logger**: Включение/выключение логирования (по умолчанию `False`).

## Методы

| Метод                            | Описание                                                                 | Возвращаемое значение                     |
|----------------------------------|--------------------------------------------------------------------------|------------------------------------------|
| `get_username()`                 | Получает имя пользователя и ID текущего аккаунта из cookies.             | Кортеж `(username, id)` или `('', '')` при ошибке. |
| `fetch_lots(after_cursor=None)`  | Получает завершенные лоты с пагинацией.                                  | Словарь с данными лотов или `None` при ошибке. |
| `fetch_exhibited_lots(userid=None, after_cursor=None)` | Получает выставленные лоты (свои или другого пользователя). | Словарь с данными лотов или `None` при ошибке. |
| `all_exhibited_lots(userid=None)`| Получает все выставленные лоты (свои или другого пользователя).          | Список словарей с данными лотов.         |
| `get_all_lots(search_filter=None)` | Получает все завершенные лоты с опциональным фильтром поиска.           | Список словарей с данными лотов.         |
| `copy_product(link)`             | Получает данные для выставления товара по ссылке.                       | Словарь с данными товара или `None` при ошибке. |
| `increase_item_priority(item_id)`| Повышает приоритет товара по его ID.                                    | Словарь с ответом API или `None` при ошибке. |
| `refill_item(item_id)`           | Возобновляет завершенный товар по его ID.                               | Словарь с ответом API или `None` при ошибке. |
| `get_product_data(link)`         | Получает полную информацию о товаре по ссылке.                          | Словарь с данными товара или `None` при ошибке. |
| `get_item_positioninfind(item_slug)` | Получает позицию товара на рынке по его slug.                        | `int` (позиция) или ошибка.              |
| `get_categories_page(link)`         | Получает информацию о странице по ссылке                      | Словарь с данными страницы или `None` при ошибке. |

## Пример использования

### Получение всех выставленных лотов

```python
lots = api.all_exhibited_lots()
if lots:
    for lot in lots:
        print(f"Товар: {lot['node']['name']}, Цена: {lot['node']['price']}")
else:
    print("Ошибка при получении лотов")
```

### Копирование товара

```python
link = "https://playerok.com/products/example-product"
product_data = api.copy_product(link)
if product_data:
    print(f"Название: {product_data['title']}, Цена: {product_data['price']}")
else:
    print("Ошибка при копировании товара")
```

## Обработка ошибок

- При ошибках (например, неверная ссылка или проблемы с API) методы возвращают `None` или пустой список и выводят сообщение об ошибке.
- Включите логирование (`logger=True`) для получения дополнительной информации.
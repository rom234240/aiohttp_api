# Реализованная функциональность аутентификации и авторизации

## Модель пользователя
- **Файл**: `aiohttp/app/models/user.py`
- **Особенности**: 
  - Хеширование паролей с bcrypt
  - Уникальные username и email
  - Связь с объявлениями

## Эндпоинты аутентификации
- **POST /register** - регистрация нового пользователя
- **POST /login** - аутентификация и получение JWT токена

## JWT система
- **Генерация токенов**: `app/auth/jwt.py`
- **Срок действия**: 24 часа
- **Middleware**: автоматическая проверка токенов

## Контроль доступа
- Создание объявлений: требуется аутентификация
- Удаление объявлений: только владелец
- Просмотр объявлений: публичный доступ

## Защищенные маршруты
- `POST /advertisements` - требует JWT
- `DELETE /advertisements/{id}` - требует JWT и проверку владения

В проекте полностью реализована требуемая функциональность:

1. ✅ Модель User с хешированием паролей (bcrypt)
   - Файл: aiohttp/app/models/user.py
   - Хеширование: aiohttp/app/auth/passwords.py

2. ✅ Эндпоинты аутентификации
   - POST /register - регистрация
   - POST /login - вход
   - Файл: aiohttp/app/routes/auth.py

3. ✅ JWT-аутентификация
   - Генерация/верификация: aiohttp/app/auth/jwt.py
   - Middleware: aiohttp/app/middleware/auth.py

4. ✅ Контроль доступа
   - Проверка владения при удалении: aiohttp/app/routes/advertisements.py:delete_advertisement()
   - Код: if ad.user_id != request.user_id: return 403

Все компоненты работают и протестированы через api_test.http.
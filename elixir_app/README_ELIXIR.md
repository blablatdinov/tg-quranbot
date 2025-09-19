# QuranBot - Elixir версия (только рассылки)

Elixir-версия бота для рассылки аятов Корана и времени намаза с параллельной обработкой сообщений.
**Примечание**: Это приложение предназначено только для рассылок. Обработка сообщений пользователей остается на Python.

## Основные особенности

### 🚀 Параллельная рассылка
- Использование `Task.async_stream/3` для параллельной отправки сообщений
- Настраиваемый уровень параллелизма (по умолчанию 10 одновременных запросов)
- Автоматическая обработка ошибок и отписок пользователей

### 📊 Мониторинг и логирование
- Подробное логирование всех операций
- Счетчики успешных отправок, ошибок и отписок
- Интеграция с Prometheus для метрик

### 🌐 Webhook API
- HTTP endpoints для запуска рассылок
- Интеграция с внешним планировщиком (croniq)
- Асинхронная обработка запросов
- Защита с помощью webhook секрета

## Архитектура

### Основные модули

#### `QuranBot.Events.MorningContentPublished`
- Обработка утренней рассылки аятов
- Параллельная отправка сообщений всем активным пользователям
- Автоматическое обновление дня пользователей

#### `QuranBot.Events.PrayersMailing`
- Обработка рассылки времени намаза
- Получение времени намаза для каждого пользователя
- Создание клавиатуры с кнопками

#### `QuranBot.Webhook`
- HTTP сервер для получения webhook запросов
- Обработка запросов от внешнего планировщика
- Асинхронный запуск рассылок

#### `QuranBot.Telegram`
- Работа с Telegram Bot API (только отправка)
- Отправка сообщений и файлов
- Обработка ошибок API

#### `QuranBot.Users`
- Управление пользователями
- Пометка неактивных пользователей
- Batch операции для оптимизации

## Установка и запуск

### Требования
- Elixir 1.15+
- Erlang/OTP 25+
- PostgreSQL
- Redis

### Установка зависимостей
```bash
mix deps.get
```

### Настройка базы данных
```bash
mix ecto.create
mix ecto.migrate
```

### Настройка переменных окружения
```bash
export TELEGRAM_TOKEN="your_telegram_bot_token"
export DATABASE_URL="postgresql://user:password@localhost/quranbot"
export REDIS_URL="redis://localhost:6379"
export WEBHOOK_PORT="4000"
export WEBHOOK_SECRET="your_webhook_secret"
export DAILY_AYATS="on"
export DAILY_PRAYERS="on"
export RAMADAN_MODE="false"
```

### Запуск
```bash
# Для разработки
mix run --no-halt

# Для продакшена
MIX_ENV=prod mix release
./_build/prod/rel/quran_bot/bin/quran_bot start
```

## Webhook API

### Endpoints

#### Health Check
```bash
GET /health
```
Проверка работоспособности сервиса.

#### Утренняя рассылка аятов
```bash
POST /webhook/morning-content
Headers:
  Authorization: Bearer your_webhook_secret
  # или
  X-Webhook-Secret: your_webhook_secret
```

#### Рассылка времени намаза
```bash
POST /webhook/prayers
Headers:
  Authorization: Bearer your_webhook_secret
  # или
  X-Webhook-Secret: your_webhook_secret
```

#### Универсальный webhook
```bash
POST /webhook/mailing/{type}
```
Где `{type}` может быть:
- `morning-content` - утренняя рассылка аятов
- `prayers` - рассылка времени намаза

### Примеры запросов

```bash
# Проверка здоровья
curl http://localhost:4000/health

# Запуск утренней рассылки
curl -X POST http://localhost:4000/webhook/morning-content \
  -H "Authorization: Bearer your_webhook_secret"

# Запуск рассылки намаза
curl -X POST http://localhost:4000/webhook/prayers \
  -H "X-Webhook-Secret: your_webhook_secret"

# Универсальный webhook
curl -X POST http://localhost:4000/webhook/mailing/morning-content \
  -H "Authorization: Bearer your_webhook_secret"
```

### Ответы API

#### Успешный запуск (202 Accepted)
```json
{
  "status": "accepted",
  "message": "Morning content mailing started"
}
```

#### Ошибка авторизации (401 Unauthorized)
```json
{
  "error": "Unauthorized"
}
```

#### Неизвестный тип рассылки (400 Bad Request)
```json
{
  "error": "Unknown mailing type: invalid_type"
}
```

## Интеграция с croniq

### Настройка планировщика

В croniq настройте следующие задачи:

```yaml
# Утренняя рассылка аятов в 6:00 утра
morning_content_mailing:
  schedule: "0 6 * * *"
  webhook:
    url: "http://your-server:4000/webhook/morning-content"
    headers:
      Authorization: "Bearer your_webhook_secret"

# Рассылка времени намаза в 20:00 вечера
prayers_mailing:
  schedule: "0 20 * * *"
  webhook:
    url: "http://your-server:4000/webhook/prayers"
    headers:
      X-Webhook-Secret: "your_webhook_secret"
```

### Альтернативная настройка с универсальным webhook

```yaml
# Утренняя рассылка аятов
morning_content_mailing:
  schedule: "0 6 * * *"
  webhook:
    url: "http://your-server:4000/webhook/mailing/morning-content"
    headers:
      Authorization: "Bearer your_webhook_secret"

# Рассылка времени намаза
prayers_mailing:
  schedule: "0 20 * * *"
  webhook:
    url: "http://your-server:4000/webhook/mailing/prayers"
    headers:
      Authorization: "Bearer your_webhook_secret"
```

## Конфигурация

### Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `TELEGRAM_TOKEN` | Токен Telegram бота | - |
| `DATABASE_URL` | URL базы данных PostgreSQL | `postgresql://postgres:postgres@localhost/quranbot` |
| `REDIS_URL` | URL Redis | `redis://localhost:6379` |
| `WEBHOOK_PORT` | Порт для webhook сервера | `4000` |
| `WEBHOOK_SECRET` | Секрет для защиты webhook | - |
| `DAILY_AYATS` | Включить/выключить рассылку аятов | `on` |
| `DAILY_PRAYERS` | Включить/выключить рассылку намаза | `on` |
| `RAMADAN_MODE` | Режим Рамадана | `false` |
| `LOG_LEVEL` | Уровень логирования | `info` |
| `POOL_SIZE` | Размер пула соединений БД | `10` |

### Настройка параллелизма

В модулях рассылки можно настроить уровень параллелизма:

```elixir
# В MorningContentPublished.process/0 и PrayersMailing.process/0
active_users
|> Task.async_stream(&send_message/1, 
    max_concurrency: 10,  # Количество одновременных запросов
    timeout: 30_000)      # Таймаут в миллисекундах
```

## API

### Ручной запуск рассылок

```elixir
# Запуск утренней рассылки аятов
QuranBot.Events.MorningContentPublished.process()

# Запуск рассылки времени намаза
QuranBot.Events.PrayersMailing.process()
```

### Работа с пользователями

```elixir
# Создание пользователя
QuranBot.Users.create_user(chat_id, city_id)

# Пометка как неактивного
QuranBot.Users.mark_as_inactive(chat_id)

# Batch операция
QuranBot.Users.batch_mark_as_inactive([chat_id1, chat_id2])
```

## Производительность

### Преимущества Elixir-версии

1. **Параллелизм**: Использование `Task.async_stream/3` позволяет отправлять сообщения параллельно
2. **Отказоустойчивость**: Автоматическое восстановление после ошибок
3. **Масштабируемость**: Легкое горизонтальное масштабирование
4. **Мониторинг**: Встроенные метрики и логирование
5. **Webhook API**: Интеграция с внешними планировщиками

### Сравнение с Python-версией

| Аспект | Python | Elixir |
|--------|--------|--------|
| Параллелизм | Последовательная отправка | Параллельная отправка |
| Обработка ошибок | Try/catch в цикле | Автоматическая обработка |
| Производительность | Медленнее при большом количестве пользователей | Быстрее благодаря параллелизму |
| Мониторинг | Базовое логирование | Подробные метрики и логи |
| Планировщик | Встроенный | Внешний (croniq) |

## Интеграция с Python-версией

### Совместная работа

1. **Python-версия**: Обрабатывает сообщения пользователей, команды, callback queries
2. **Elixir-версия**: Выполняет только рассылки с параллельной обработкой

### Общая база данных

Обе версии используют одну и ту же базу данных PostgreSQL:
- Таблица `users` - информация о пользователях
- Таблица `ayats` - аяты для рассылки
- Таблица `prayers` - время намаза
- Таблица `suras` - информация о сурах

### Запуск

```bash
# Запуск Python-версии (обработка сообщений)
python src/main.py

# Запуск Elixir-версии (рассылки)
mix run --no-halt
```

## Разработка

### Запуск тестов
```bash
mix test
```

### Проверка кода
```bash
mix credo
mix dialyzer
```

### Форматирование кода
```bash
mix format
```

## Docker

### Сборка образа
```bash
docker build -t quranbot-elixir -f Dockerfile.elixir .
```

### Запуск контейнера
```bash
docker run -d \
  --name quranbot-elixir \
  -p 4000:4000 \
  -e TELEGRAM_TOKEN="your_token" \
  -e DATABASE_URL="postgresql://user:pass@host/db" \
  -e REDIS_URL="redis://host:6379" \
  -e WEBHOOK_SECRET="your_webhook_secret" \
  quranbot-elixir
```

## Лицензия

MIT License - см. файл LICENSE. 
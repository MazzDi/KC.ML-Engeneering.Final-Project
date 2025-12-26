## Credit Scoring Service (FastAPI + Postgres + RabbitMQ + CatBoost)

Сервис поднимает **API + Web UI** для скоринга клиентов.

- **Клиент**: видит свой профиль, назначенного менеджера, кредит и историю платежей, может запросить/обновить скор.
- **Менеджер**: видит список клиентов, может открыть карточку, редактировать признаки клиента и пересчитывать скор.
- **ML часть**: `ml-worker` считает `predict_proba` CatBoost по RPC через RabbitMQ и возвращает вероятность дефолта (`proba`).

### Компоненты

- **`app/`**: FastAPI + UI (статика) + CRUD слой + модели.
- **`database/`**: подключение к БД и настройки.
- **Postgres**: хранение пользователей/клиентов/менеджеров/кредитов/скорингов.
- **RabbitMQ**: RPC шина для ML воркеров.
- **`ml-worker`**: CatBoost classifier RPC worker (`ml_scoring_queue`).
- **`rm-worker`**: второй RPC worker, тоже грузит CatBoost модель из `app/ml_worker/model.cbm` (очередь `rm_task_queue`).

### Данные и сущности

- **User**: login/password_hash/role, связка 1-1 с `Client` или `Manager`.
- **Client**: признаки для скоринга + `manager_id`.
- **Manager**: менеджер + список клиентов.
- **Credit**: 1 кредит на 1 клиента (`client_id` unique), `amount_total`, `annual_rate`, `payment_history` (JSON).
- **Score**: событие скоринга (`client_id`, `score` = proba), `timestamp` (из base-модели).

### Как запустить (Docker Compose)

1) Подготовить env:
- файл: `app/.env` (используется в `docker-compose.yaml`)

2) Поднять сервис:

```bash
cd /Users/nskorotkov/GIT/KC.ML-Engeneering.Final-Project-1
docker compose --env-file ./app/.env up -d --build
```

3) Открыть:
- **UI**: `http://localhost/`
- **API** (через прокси): `http://localhost/health`

### Инициализация / seed

`db-init` запускает `app/scripts/seed_db.py` и создаёт тестовые данные:

- 1510 клиентов
- 30 менеджеров (клиенты распределяются равномерно)
- 2 администратора
- каждому клиенту создаётся `Credit` и подгружается `payment_history` из `app/scripts/test_data/credit_history.csv`
- `days_employed_bin` берётся из `df_to_keep.csv` и сохраняется в `Client`

### Скоринг

- Сервис хранит **`Score.score` как вероятность дефолта (`proba`)**.
- В UI отображается “рейтинг” как **`round(1 - proba, 2)`** (чем больше — тем лучше).

### Основные endpoints (высокоуровнево)

- **Health**: `GET /health`
- **Auth (cookie session)**: `POST /auth/login`, `POST /auth/logout`, `GET /auth/me`
- **CRUD API**: `GET /users/{id}`, `GET /clients/{id}`, `GET /managers/{id}`, `GET /managers/{id}/clients`
- **Scoring**: `POST /clients/{client_id}/score`
- **UI API**: маршруты для dashboard клиента/менеджера (см. `app/routes/ui_api.py`)

### Тесты

Тесты на `pytest`, БД в тестах — `sqlite` in-memory.

```bash
pytest -q
```

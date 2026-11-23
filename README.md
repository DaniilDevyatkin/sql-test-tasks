# SQL test tasks (Airbnb · Alfabank · Samokat · Сбер · VK · ДомКлик)

Тестовые задания по SQL из каталога Hexlet (`Hexlet/ru-test-assignments`, раздел SQL).
Для каждой задачи скачан **родной датасет** (DDL + данные) и написан запрос.
Все 26 задач реально прогнаны на PostgreSQL 16 — полный вывод: `run.log`.

## Как запустить

```bash
docker compose up -d          # PostgreSQL на 127.0.0.1:55432
python3 runner.py             # все задачи, каждая в своей базе
python3 runner.py 74 93       # выбранные
```

`runner.py` для каждой задачи создаёт отдельную базу `task_<id>`, накатывает
`sql/<company>/tests/<id>/*.sql` и выполняет запрос — поэтому INSERT (#58)
и CREATE VIEW (#80) не мешают соседним задачам.

## Задачи

| # | Компания | Что считается | Ключ решения |
|---|----------|---------------|--------------|
| 74 | Airbnb | id + YES/NO по наличию интернета | `CASE WHEN` |
| 59 | Airbnb | пользователи с белорусским номером | `LIKE '+375%'` |
| 61 | Airbnb | комнаты, занятые хотя бы сутки в 12-ю неделю 2020 | пересечение интервалов дат |
| 62 | Airbnb | популярность доменов 2-го уровня | `substring(email FROM '[^@]+$')` + `GROUP BY` |
| 64 | Airbnb | бронирования по месяцам | `EXTRACT(YEAR/MONTH)`, `GROUP BY 1,2` |
| 65 | Airbnb | рейтинг комнат, floor(avg) | `FLOOR(AVG())` + join reviews |
| 66 | Airbnb | комнаты со всеми удобствами: дни и сумма | `LEFT JOIN` + `COALESCE(...,0)` |
| 68 | Airbnb | последний арендатор и дата выезда | `DISTINCT ON (room_id) ... ORDER BY end_date DESC` |
| 69 | Airbnb | заработок владельцев | join rooms→reservations, `SUM(total)` |
| 70 | Airbnb | economy / comfort / premium | `CASE WHEN price <= 100 … >= 200` |
| 71 | Airbnb | % активных пользователей | `ROUND(100.0 * n / total, 2)`, `UNION`-подобный `IN (...) OR IN (...)` |
| 72 | Airbnb | средняя цена суток, ceil | `CEIL(AVG(price))` |
| 73 | Airbnb | комнаты с нечётным числом аренд | `HAVING COUNT(*) % 2 = 1` |
| 76 | Airbnb | признаки owner / tenant | два `EXISTS` → 1/0 |
| 78 | Airbnb | почта на hotmail.com | `LIKE '%@hotmail.com'` |
| 79 | Airbnb | цена со скидкой 10% при ТВ+интернет | `CASE WHEN … THEN price * 0.9` |
| 80 | Airbnb | представление Verified_Users | `CREATE VIEW` + `email_verified_at IS NOT NULL` |
| 58 | Airbnb | добавить отзыв 5 баллов | `INSERT … SELECT COUNT(*)+1 … RETURNING *` |
| 93 | Alfabank | средний возраст покупателей Smartwatch-2024 | три join'а + `AVG` |
| 94 | Alfabank | купили и Laptop, и Monitor в марте 2024 | `HAVING COUNT(DISTINCT name) = 2` |
| 97 | Samokat | города с >80 работающих складов на сегодня | `date_open <= CURRENT_DATE AND (date_close IS NULL OR > CURRENT_DATE)` |
| 99 | VK | доход с женской аудитории | `SUM(items * price)`, `gender IN ('female','f')` |
| 101 | VK | первый по времени товар пользователя | `DISTINCT ON (user_id) … ORDER BY transaction_ts` |
| 103 | Сбер | зарплата выше руководителя | self-join `employees` по `chief_id` |
| 109 | ДомКлик | страна города Salzburg | cities → regions → countries |
| 111 | ДомКлик | население регионов | `SUM(population)` + `GROUP BY region` |

## Решения по совместимости с PostgreSQL

Датасеты в каталоге собраны под MySQL/SQLite (sql-academy) и в чистом виде PostgreSQL
не принимает. Правки минимальные и только в типах, данные не тронуты:

* `DATETIME` → `TIMESTAMP` (в PostgreSQL такого типа нет);
* в `rooms` флаги `has_tv/has_internet/has_kitchen/has_air_con` объявлены `BOOLEAN`,
  а вставляются числа `0/1` → объявлены `INT` (в задачах 74/66/79 сравнение с `1`);
* `regions.countryid` объявлен `VARCHAR`, при этом в нём лежат числа → `::int` в join;
* `transactions.transaction_id` не влезает в `INT` (значения > 2^31) → `BIGINT`.

## Что осталось

* Appbooster (`sql/appbooster/…md`) — не набор задач с датасетом, а вопрос
  «почему тормозят запросы»: ответ текстом (индексы `(user_id)`, `(post_id)`,
  `(user_id, post_id)`, `EXPLAIN ANALYZE`, частичные индексы, `NOT EXISTS` вместо `NOT IN`).
  Оформляю отдельной заметкой, если нужно.
* Задачи опционально можно сверить с эталоном sql-academy (нужен платный аккаунт тренажёра);
  сейчас корректность проверена прогоном на реальном PostgreSQL и ручной сверкой логики.

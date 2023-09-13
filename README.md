# Test task DRF
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![DRF CI](https://github.com/nvkey/test_task_drf/actions/workflows/workflow.yml/badge.svg)

Тестовый проект на Django REST framework
## Задание
Соберите с помощью Django Rest Framework каталог исполнителей и их альбомов с песнями такой структуры:
- Исполнитель
    - Название
- Альбом
    - Исполнитель
    - Год выпуска
- Песня
    - Название
    - Порядковый номер в альбоме

Одна и та же песня может быть включена в несколько альбомов, но под разными порядковыми номерами.⋅⋅
В качестве площадки для демонстрации АПИ подключите к нему Swagger, чтобы можно было проверить работу АПИ через Postman.⋅⋅
Результат присылайте в виде репозитория в GitHub с инструкцией по запуску. Бонусом будет, если проект будет запускаться через docker compose.

## Запуск проекта(Docker):

Клонировать репозиторий и перейти в него в командной строке:
``` bash
git clone git@github.com:nvkey/test_task_drf.git
cd test_task_drf
```

Создайте файл .env в папке `/infra/` со следующими ключами:
```bash
SECRET_KEY=<ваш_django_секретный_ключ>
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```
Вы можете сгенерировать `SECRET_KEY` следующим образом. Из корневой директории проекта выполнить:

```bash
python manage.py shell
from django.core.management.utils import get_random_secret_key  
get_random_secret_key()
```
Полученный ключ скопировать в .env

Запустить docker-compose:
``` bash
cd infra
docker compose up -d --build
```

Выполнить миграции, дата-миграции и сформировать статику:
``` bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic --no-input 
```
Проект: http://localhost/api/v1⋅⋅
Swagger API: http://localhost/swagger/⋅⋅
Redoc: http://localhost/redoc

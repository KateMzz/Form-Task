## Setup

1. Склонируйте репозиторий:

```bash
git clone https://github.com/KateMzz/Form-Task.git
```
```bash
cd Form-Task
```

2. Создайте .env в корне проекта

   ```bash
      
      DB_NAME=your_database
      DB_COLLECTION=your_db
      
    ```
3. Используйте следующие команды для запуска проекта:

```bash
   docker-compose up --build
```
Это поднимет контейнеры для вашего приложения и базы данных MongoDB.

4. Чтобы запустить тесты, используйте команду:

    ```bash
    docker exec -it get_form pytest
    ```
##


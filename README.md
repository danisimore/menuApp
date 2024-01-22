# MenuApp
Реализация первого ДЗ в рамках интенсива от Y_LAB.

## Инструкция по развертыванию приложения.
**ТРЕБОВАНИЯ**
+ У вас должен быть установлен docker
### Linux
1. Скопируйте ссылку репозитория ![Copy Repo-link](https://i.imgur.com/p8WPXpm.png)
2. Создайте директорию и откройте в ней командную строку ![Open CMD](https://i.imgur.com/DQay8e8.png)
3. Склонируйте репозиторий с помощью команды `git clone https://github.com/danisimore/menuApp.git` ![Clon Repo](https://i.imgur.com/FkDS1pr.png)
4. С помощью команды `cd menuApp` перейдите в директорию, которая была склонирована
5. Создайте файл .env-prod используя редактор nano - `nano .env-prod`. У вас откроется окно редактора nano.
6. Скопируйте и вставьте следующие переменные окружения:
   ```
   DB_HOST=db
   DB_PORT=5432
   DB_NAME=postgres
   DB_USER=postgres
   DB_PASSWORD=postgres
    
   POSTGRES_DB=postgres
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   ```
7. Нажмите **Crtl + O**, затем **ENTER**. Файл будет сохранен, чтобы выйти из редактора нажмите сочетание клавиш **Ctrl + X**.
8. Напишите команду `sudo docker compose build`
9. Напишите команду `sudo docker compose up`
10. Подождите 10 секунд. Задержка выставлена, для того чтобы БД успела полностью инициализироваться перед тем, как alembic начнет делать миграции.

**Приложение готово к работе! Можно запускать Postman тесты**

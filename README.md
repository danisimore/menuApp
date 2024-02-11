# MenuApp
Реализация учебного проекта в рамках курса Интенсив по Python от Ylab.

**ВЕРСИЯ ОТ 11.02.2024**

🛠 **Реализация ДЗ #4 - *Многопроцессорность, асинхронность***
- [x] Переписать текущее FastAPI приложение на асинхронное выполнение
- [x] Добавить в проект фоновую задачу с помощью Celery + RabbitMQ.
- [x] Добавить эндпоинт (GET) для вывода всех меню со всеми связанными подменю и со всеми связанными блюдами.
- [x] Реализовать инвалидация кэша в background task (встроено в FastAPI)
- [x] * Обновление меню из google sheets раз в 15 сек.
- [x] ** Блюда по акции. Размер скидки (%) указывается в столбце G файла Menu.xlsx


✨ **Задания со звездочкой**
   1. *Реализовать вывод количества подменю и блюд для Меню через один (сложный) ORM запрос*
      ```
      /api_v1/database/database_services.py -> Функция select_specific_menu
      ```
   2. *Реализовать тестовый сценарий «Проверка кол-ва блюд и подменю в меню» из Postman с помощью pytest*
      ```
      /tests/test_quan_of_dishes_and_submenus.py
      ```
   3. *Описать ручки API в соответствий c OpenAPI*
      ```
      URL - http://localhost:8000/docs

      JSON и yaml c описанием ручек -> /api_v1/docs/
      ```
   4. *Реализовать в тестах аналог Django reverse() для FastAPI*
      ```
      /api_v1/custom_router.py
      ```
   5. *Обновление меню из google sheets раз в 15 сек*
      ```
      /api_v1/sync_google_sheets/data_sync.py
      ```
   6. *Блюда по акции. Размер скидки (%) указывается в столбце G файла Menu.xlsx*
      ```
      Скидка сохраняется в кэше, если указана в столбце:
         api_v1/sync_google_sheets/operations.py

      Далее используется функция для применения скидки к цене во время формирования ответа сервера:
         /api_v1/dish/dish_utils.py
      ```
**❗️ КОММЕНТАРИИ ❗️**

⚠️ Ссылка на гугл таблицу -

https://docs.google.com/spreadsheets/d/1hhrwkP1xBU7jvxVEcwtBVkSOhLEwJBG3ZpOiA0D-hfY/edit?usp=sharing

⚠️ Открыл доступ на редактирование всем. Можете использовать эту таблицу для тестирования синхронизации.

## Инструкция по развертыванию приложения.
1. Скопируйте ссылку репозитория ![Copy Repo-link](https://i.imgur.com/p8WPXpm.png)
2. Создайте директорию и откройте в ней командную строку ![Open CMD](https://i.imgur.com/DQay8e8.png)
3. Склонируйте репозиторий с помощью команды
   ```
   git clone https://github.com/danisimore/menuApp.git
   ```
    ![Clon Repo](https://i.imgur.com/FkDS1pr.png)
4. Перейдите в директорию, которая была склонирована c помощью команды:
   ```
   cd menuApp
   ```

5. Чтобы зпустить контейнер с приложением используйте команду
    ```
    sudo make up
    ```
6. Чтобы запустить контейнер с тестами используйте команду
   ```
   sudo make up_tests_container
   ```
7. Чтобы включить синхорнизацию с Google Sheets используйте команду
   ```
   make run_sync
   ```
8. Для того, чтобы остановить синхорнизацию используйте команду
   ```
   make stop_sync
   ```

## Тестирование
Реализованы тестовые сценарии аналогичные тестированию в Postman.

**Запуск тестов**:
1. Чтобы запустить **все тесты**, используйте команду:
   ```
   sudo make run_tests
   ```
2. Чтобы отдельно протестировать CRUD операции **меню**, используйте команду:
   ```
   sudo make run_menu_tests
   ```
3. Чтобы отдельно протестировать CRUD операции **подменю**, используйте команду:
   ```
   sudo make run_submenu_tests
   ```
4. Чтобы отдельно протестировать CRUD операции **блюд**, используйте команду:
   ```
   sudo make run_dishes_tests
   ```
5. Чтобы отдельно протестировать сценарий операции **Проверка кол-ва блюд и подменю в меню**, используйте команду:
   ```
   sudo make run_check_quan_of_dishes_and_submenus_tests
   ```

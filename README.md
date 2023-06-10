# Сравниваем зарплату программистов

- Программа позволяет собрать данные по вакансиями и оценить среднюю зарплату по языкам программирования на сайтах HeadHunter и Superjob
- Результат выводится в консоль ввиде таблицы

### Как установить

- Зарегистрировать свое приложение в API SuperJob
- Создать в корне проекта файл **.env**, указать в нем данные с SuperJob:
  - Логин: **SJ_LOGIN**
  - Пароль: **SJ_PASSWORD**
  - ID клиента: **SJ_CLIENT_ID**
  - Секретный код: **SJ_SECRET_CODE**
- Python3 должен быть установлен
- Затем используйте `pip` (или `pip3`, еслить есть конфликт с Python2) для установки зависимостей: 
    ```
    pip install -r requirements.txt
    ```

- Рекомендуется использовать [virtualenv/venv](https://docs.python.org/3/library/venv.html) для изоляции проекта.

### Как пользоваться

- Программа содержит 2 скриптf:
  - ```utils.py``` - получить токены от API SuperJob
  - ```get_salaries_sj_hh.py``` - получить таблицы со средними зарплатами
  - Следует сначала запустить utils.py, чтобы получить токены:
    ```
        python3 utils.py
    ```
  - Добавить полученные токены в файл **.env**:
    - Access token: **SJ_TOKEN**
    - Refresh token: **SJ_REFRESH_TOKEN**
  - Пример файла **.env**:
    ```
    SJ_TOKEN='v3.r.136dfedf348'
    SJ_REFRESH_TOKEN='v3.r.343434'
    SJ_SECRET_CODE='v3.r.136088883'
    SJ_LOGIN='example@gmail.com'
    SJ_PASSWORD='qwerty'
    SJ_CLIENT_ID=1346
    ```
  - Запустить скрипт:
    ```
        python3 get_salaries_sj_hh.py
    ```

### Цель проекта

Код написан в образовательный целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).

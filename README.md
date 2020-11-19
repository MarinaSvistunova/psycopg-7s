# psycopg-7s

*Для работы приложения необходимо установить postgres.*

Инструкция:

1. Создать virtualenv:

```virtualenv psycopg-7s```

2. Перейти в созданную папку виртуального окружения:

```cd psycopg-7s```

3. Активировать virtualenv:

```source bin/activate```

4. Клонировать репозиторий:

```git clone https://github.com/MarinaSvistunova/psycopg-7s.git```

5. Перейти в папку psycopg-7s:

```cd psycopg-7s```

6. Сменить ветку проекта:

```git checkout flask```

7. Выполнить установку зависимостей:

```pip install -r requirements.txt```

8. В файле db_functions.py изменить строку номер 9. Необходимо указать данные своего сервера (необходимо установить postgres).

```self.connection_string = 'dbname=postgres user=marinasvistunova password=1997 host=localhost port=5432'```

9. Запустить приложение:

```python app.py```

```
virtualenv venv
cd venv
source bin/activate
git clone https://github.com/MarinaSvistunova/psycopg-7s.git
cd psycopg-7s
pip install -r requirements.txt
cd todoapp_psycopg2
python manage.py runserver
```
Перейти по адресу http://127.0.0.1:8000/todo/list/

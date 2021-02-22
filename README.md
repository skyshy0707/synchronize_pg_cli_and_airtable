# synchronize_pg_cli_and_airtable
Syncronization of the postgres client db with an airtable db rest api


**Назначение:**


Скрипт используется совместно с веб-проектом на django (https://github.com/skyshy0707/meta_therapists).
Скрипт предназначен для синхронизации данных таблицы сервиса airtable.com вида (https://airtable.com/shrlHQArEK0WNdylo/tblzxpZ9KSX09akd4/viwwEoRm3YKZ4LFbY?blocks=hide) с базой данных postges на локальной машине.
Скрипт добавляет/обновляет только те строки, которые имеют все данные. Если какие-то поля пустые, то такие строки будут проигнорированы.

Кроме того, скрипт при каждом запуске выгружает все данные в отдельную таблицу *rawdata* с указанием времени запуска скрипта.


**Конфигурация ОС и установленного ПО:**


Windows 10;

Postgres 12;

Django 3.1.7;


**Зависимости:**


Python 3.8.3;

request 2.25.1;

psycopg2 2.8.6;

sqlalchemy 1.3.23


**Использование:**

1) Перейдите в директорию *to_django_path* с проектом django, использующим postgres:


>\>cd to_django_path


2) Запустите команды создания необходимых баз данных:

>\>python manage.py makemigrations

>\>python manage.py migrate


3) Перейдите в директорию *to_path* проекта *synchronize_pg_cli_and_airtable* где находится скрипт *synchronize.py*:


>\>cd to_path


4) Запустите скрипт *synchronize.py* из cmd:


>\>python synchronize.py [--username USERNAME] [--password PASSWORD] [--port PORT] [--dbname DBNAME] [--baseid BASEID] [--api_key API_KEY]



**Параметры соединения с postgres на ПК клиента:**


--username --- имя пользователя;

--password --- пароль;

--port --- номер порта;

--dbname --- имя базы данных

**Параметры соединения с REST API базы данных Airtable:**


--baseid --- id базы данных (BaseId);

--api_key --- ключ, по которому осуществляется доступ к базе данных с BaseId



Значения всех параметров соединений по умолчанию заданы в файле config.ini, в котором их можно определить, либо же задать в качестве параметра при запуске скрипта synchronize.py из cmd.

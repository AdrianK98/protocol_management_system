# protocol_management_system

A simple protocol management system writen in python uses [django](https://www.djangoproject.com/) and [PostgreSQL](https://www.postgresql.org/).
The project uses [poetry](https://python-poetry.org/) as package manager.

## Features:
 - [x] Adding/deleting/editing users (employees)
 - [x] Adding/deleting/editing items
 - [x] Creating protocols
 - [x] Creating utilizations
 - [x] Regionalization
 - [ ] Alerts/notifications
 - [ ] Reports


## Configuration
You should configure database by your self (user, db) and pass the data to .env file.

Example of .env file:

``` .env

POSTGRES_DB=database_name
POSTGRES_USER=database_user
POSTGRES_PASSWORD=database_user_password
DB_HOST=localhost

```

Run poetry shell:

```console
$ poetry shell
```

If you are using pipx:

```console
$ pipx run poetry shell
```

Then run src/manage.py script:

```console
$ python3 src/manage.py makemigrations
$ python3 src/manage.py migrate
```

To run server:

```console
$ python3 src/manage.py runserver
```

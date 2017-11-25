clockIn
=======

Simple job timing and billing application.

## Installation

### Environment Setup
#### `pyenv` & `pyenv-virtualenv`
```
$ pyenv virtualenv 2.7 clockIn_venv
$ echo 'clockIn_venv' > .python-version
$ pip install -r requirements.txt
```

#### `virualenv`
```
$ virtualenv clockIn_venv
$ source ./clockIn_venv/bin/activate
$ pip install -r requirements.txt
```


### Database Setup
Copy the example database config file and edit it as required
```
$ cp ./config/example.database.cfg ./config/database.cfg
```

This command will create a database if it doesn't already exist and
all the required tables if they don't exist.
```
$ python init_db.py
```

Once the database is setup it is necessary to create a `User` & `Job`.
This can be done in `python` by running the following code snippet:
```python
from models import db_session, Job, User

# Create and commit a new User
new_user = User(
    name='?',  # Only this field is actually required to create a User
    company_name='?',
    phone_number='?',
    email='?',
    bank_name='?',
    branch='?',
    account_number='?',
    btc_wallet_address='?',
)
db_session.add(new_user)
db_session.commit()

# Create and commit a new Job
new_job = Job(name='?', rate=0.0, invoice_address_to='?')
db_session.add(new_job)
db_session.commit()
```

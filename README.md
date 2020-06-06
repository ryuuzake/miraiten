# Kyou.id Clone

This is a project that tries to clone kyou.id with a same concept that is japanese goods
(otaku goods) e-commerce.

## How to use

To use this project, follow these steps:

    # Clone Repository
    
    $ git clone https://github.com/ryuuzake/kyou-id-clone.git
    $ cd kyou-id-clone
    
    # Create virtual environment (Linux)

    $ python3 -m venv venv
    $ source venv/bin/activate
    (venv) $ pip install -r requirements.txt
    
    # Create virtual environment (Linux)

    > python -m venv venv
    > venv\Scripts\activate.bat
    (venv) > pip install -r requirements.txt
    
    # Start application
    
    $ python manage.py makemigrations
    $ python manage.py migration
    $ python manage.py createsuperuser
    $ python manage.py runserver
    
## Contribute Guidelines

create new branch for adding feature or fixing bug.
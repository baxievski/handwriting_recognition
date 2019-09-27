# Setup

## clone repo

```shell
git clone https://github.com/baxievski/handwriting_recognition.git
cd handwriting_recognition
```

## First time

```shell
docker-compose up --build --detach
docker-compose run web python /code/manage.py migrate
docker-compose run web python /code/manage.py createsuperuser
```

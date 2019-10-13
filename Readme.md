# Handwriting recognition

A django application that recognizes handwritten digits.

Predictions are done by a simple feedforward neural network with one hidden layer.

The neural network is trained on datasets (digits, cyrillic characters) stored in postgress `ArrayField`.

Django admin is used to check/fix/discard the inputs.

You can access a live version at [bojanaxievski.duckdns.org](http://bojanaxievski.duckdns.org/)

## Setup

Start a development environment:

```shell
docker-compose \
--file docker-compose-dev.yml \
up --detach
```

Create the database migration scripts

```shell
docker-compose \
--file docker-compose-dev.yml \
web python /code/manage.py makemigrations handwriting
```

Migrate (create) db:

```sh
docker-compose \
--file docker-compose-dev.yml \
web python /code/manage.py migrate
```

Now the db and web containers should be started.

Navigate to [localhost:8000](http://localhost:8000) to access the app.

You can start creating the dataset.

Train the neural network on the digits dataset:

```shell
docker-compose \
--file docker-compose-dev.yml \
web python /code/manage.py train --kind digits
```

## TODO

* [ ] Finish cyrillic dataset
* [ ] Train on cyrillic dataset
* [ ] lets encrypt ssl certificate
* [ ] Form to confirm/correct prediction
* [ ] Save input on prediction
* [ ] Async saving
* [ ] Privacy notice
* [ ] Create a "combined" nn

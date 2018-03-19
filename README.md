# Maxibooking billing
Maxibooking billing django rest backend

## urls
* two-factor setup url: account/two_factor/setup/
* admin: admin/ (login: admin password: password)

## minimum requirements
* vagrant docker

## installation
* vagrant up

## start project
* vagrant ssh
* server (url: localhost:8000)
* optional: pytest

## deploy
* key location: ~/.ssh/pem/maxibookingltd.pem
* staging: ansible-playbook -i .ansible/staging.ini .ansible/deploy.yml
* prod: ansible-playbook -i .ansible/prod.ini .ansible/deploy.yml

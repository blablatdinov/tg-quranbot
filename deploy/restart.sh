#!/bin/bash
cd /home/www/code/quranbot-aiogram

git pull
git reset --hard origin/master

poetry install --no-dev

sudo supervisorctl restart quranbot
sudo supervisorctl restart quranbot-event-reciever

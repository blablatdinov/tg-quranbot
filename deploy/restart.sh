cd /home/www/code/quranbot-aiogram

#git pull
#git reset --hard origin/master

/home/www/.poetry/bin/poetry install --no-dev

sudo supervisorctl restart quranbot

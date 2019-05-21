# Questable

A game-like To-Do List Telegram Bot.

Source code for [Questable Bot](https://t.me/questable_bot) and the relevant
[API](https://api.questable.webionite.com/)

# Self Hosting

+ Clone the repository.
	+ `git clone https://gitlab.com/questable/questable_bot.git`
+ `cd questable`

## Telegram Bot

+ Install the dependencies
	+ `pip3 install python-telegram-bot`
+ Copy `sample.config.py` to `config.py` and edit it accordingly.
+ Run the bot
	+ `python3 bot.py`

## Questable API Server

+ Install the dependencies
	+ `pip3 install Flask`
+ Install `gunicorn`
	+ `pip3 install gunicorn`
+ Run `gunicorn3 -b 127.0.0.1:5000 server:app`. Change port if you want to run
  gunicorn on a different port.
+ Set up a reverse proxy from your webserver to `localhost:5000`.

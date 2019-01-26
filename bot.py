import time
import logging
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup
import requests
import json

logging.basicConfig(level=logging.INFO)


def handle(msg):
    """
    A function that will be invoked when a message is
    recevied by the bot
    """
    # Get text or data from the message
    text = msg.get("text", None)
    data = msg.get("data", None)

    if data is not None:
        # This is a message from a custom keyboard
        chat_id = msg["message"]["chat"]["id"]
        content_type = "data"
    elif text is not None:
        # This is a text message from the user
        chat_id = msg["chat"]["id"]
        content_type = "text"
    else:
        # This is a message we don't know how to handle
        content_type = "unknown"

    if content_type == "text":
        message = msg["text"]
        logging.info("Received from chat_id={}: {}".format(chat_id, message))

        if message == "/start":
            url_register = 'http://127.0.0.1:5000/register'
            user_id = {'chat_id': chat_id}
            resp = requests.post(url_register, json=user_id)
            resp_json = resp.json()
            logging.info('Request to /register data is {}'.format(user_id))
            # logging.info('Tpye of chat_id is {}'.format(type(chat_id)))
            logging.info('resp_json from /register is {}, TYPE {}'.format(resp_json, type(resp_json)))
            msg = 'Welcome back!' if resp_json['exists'] == 1 else "Welcome!"
            bot.sendMessage(chat_id, msg)

        elif message == "/rate":
            # Ask the server to return a random
            # movie, and ask the user to rate the movie
            # You should send the user the following information:
            # 1. Name of the movie
            # 2. A link to the movie on IMDB
            url_get_unrated_movie = 'http://127.0.0.1:5000/get_unrated_movie'
            user_id = {'chat_id': chat_id}
            resp = requests.post(url_get_unrated_movie, json=user_id)
            resp_json = resp.json()
            movie_id = resp_json['id']
            movie_title = resp_json['title']
            movie_imdb_url = resp_json['url']
            logging.info('Request to /get_unrated_movie data is {}'.format(user_id))
            logging.info('resp_json from /get_unrated_movie is {}, TYPE {}'.format(resp_json, type(resp_json)))
            # Create a custom keyboard to let user enter rating
            my_inline_keyboard = [[
                InlineKeyboardButton(text='1', callback_data=json.dumps({'movie_id': movie_id, 'rating': 1})),
                InlineKeyboardButton(text='2', callback_data=json.dumps({'movie_id': movie_id, 'rating': 2})),
                InlineKeyboardButton(text='3', callback_data=json.dumps({'movie_id': movie_id, 'rating': 3})),
                InlineKeyboardButton(text='4', callback_data=json.dumps({'movie_id': movie_id, 'rating': 4})),
                InlineKeyboardButton(text='5', callback_data=json.dumps({'movie_id': movie_id, 'rating': 5}))
            ]]
            keyboard = InlineKeyboardMarkup(inline_keyboard=my_inline_keyboard)
            bot.sendMessage(chat_id, '{}: {}'.format(movie_title, movie_imdb_url))
            bot.sendMessage(chat_id, "How do you rate this movie?", reply_markup=keyboard)

        elif message == "/recommend":
            # Ask the server to generate a list of
            # recommended movies to the user
            url_recommend = 'http://127.0.0.1:5000/recommend'
            resp = requests.post(url_recommend, json={"chat_id": chat_id, "top_n": 3})
            resp_json = resp.json()
            logging.info('Request to /get_unrated_movie data is {}'.format({"chat_id": chat_id, "top_n": 3}))
            movie_list = resp_json['movies']
            logging.info('resp_json from /recommend is {}, TYPE {}'.format(resp_json, type(resp_json)))
            if movie_list:
                bot.sendMessage(chat_id, "My recommendations:")
                for movie_info in movie_list:
                    bot.sendMessage(chat_id, '{}: {}'.format(movie_info['title'], movie_info['url']))
            else:
                bot.sendMessage(chat_id, 'You have not rated enough movies, we cannot generate recommendation for you.')

        else:
            # Some command that we don't understand
            bot.sendMessage(chat_id, "I don't understand your command.")

    elif content_type == "data":
        # This is data returned by the custom keyboard
        # Extract the movie ID and the rating from the data
        # and then send this to the server
        logging.info("Received rating: {}, TYPE: {}".format(data, type(data)))
        data = json.loads(data)
        movie_id = data['movie_id']
        rating = data['rating']
        url_rate_movie = 'http://127.0.0.1:5000/rate_movie'
        rate_movie_data = {
            'chat_id': chat_id,
            'movie_id': movie_id,
            'rating': rating
        }
        resp = requests.post(url_rate_movie, json=rate_movie_data)
        resp_json = resp.json()
        logging.info('Request to /rate_movie data is {}'.format(rate_movie_data))
        logging.info('resp_json from /rate_movie is {}, TYPE {}'.format(resp_json, type(resp_json)))
        bot.sendMessage(chat_id, "Your rating is received!")


if __name__ == "__main__":
    bot = telepot.Bot("")
    MessageLoop(bot, handle).run_as_thread()

    while True:
        time.sleep(10)

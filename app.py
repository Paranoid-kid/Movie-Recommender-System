from flask import Flask, request, jsonify
import logging
import pandas as pd
import numpy as np
from scipy.stats import pearsonr
import time
import random

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

data_path = ''
df_ratings_data = pd.read_csv(data_path + 'ratings.small.csv')
df_movie_names = pd.read_csv(data_path + 'movies.csv')
df_movie_links = pd.read_csv(data_path + 'links.csv', dtype={'imdbId': str})
df_movie_name_imdb = pd.DataFrame.merge(df_movie_names, df_movie_links, on='movieId')
df_movie_name_imdb.drop(['genres', 'tmdbId'], axis=1, inplace=True)
df_movie_name_imdb.set_index(["movieId"], inplace=True)
df_users_movies = df_ratings_data.pivot(index='userId', columns='movieId', values='rating').fillna(0)


def similarity(u1, u2):
    r, _ = pearsonr(df_users_movies.loc[u1], df_users_movies.loc[u2])
    return r


def top_n_matches(user, n=20):
    scores = [(similarity(user, u), u) for u in list(df_users_movies.index) if u != user]
    scores.sort(reverse=True)
    return scores[0:n]


def top_n_recommended(user, top_n_neighbours, n=3):
    start = time.time()
    totals = {}
    sim_sums = {}
    users_ids = list(df_users_movies.index)
    logging.info('users_ids: [-2]: {}, [-1]: {} (check if new user was added to the matrix)'.format(users_ids[-2], users_ids[-1]))
    r_mean_user = np.mean([r for r in df_users_movies.loc[user] if r > 0])
    unrated_movie_list = df_users_movies.loc[user]
    unrated_movie_list = unrated_movie_list[unrated_movie_list == 0]
    for neighbour in top_n_neighbours:
        sim = neighbour[0]
        u = neighbour[1]
        r_mean_u = np.mean([r for r in df_users_movies.loc[u] if r > 0])
        for unrated_movie in unrated_movie_list.index:
            if df_users_movies[unrated_movie][u] == 0: continue
            totals.setdefault(unrated_movie, 0)
            totals[unrated_movie] += sim * (df_users_movies[unrated_movie][u] - r_mean_u)
            sim_sums.setdefault(unrated_movie, 0)
            sim_sums[unrated_movie] += sim
    rankings = [(r_mean_user + total / sim_sums[unrated_movie], unrated_movie) for unrated_movie, total in totals.items()]
    rankings.sort(reverse=True)
    end = time.time()
    logging.info('Time used: {}s'.format(end - start))
    return rankings[:n]


@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        logging.info('Request data from /register : {}'.format(data))
        user_id = data['chat_id']
        users_ids = list(df_users_movies.index)
        if user_id in users_ids:
            return jsonify({"exists": 1})
        else:
            df_users_movies.loc[user_id] = 0
            # ----------------random rate 50 movies for test user----------
            # for movie_id in random.sample(df_users_movies.columns.values.tolist(), 50):
            #     df_users_movies[movie_id][user_id] = random.randint(1, 5)
            return jsonify({"exists": 0})


@app.route('/get_unrated_movie', methods=['POST'])
def get_unrated_movie():
    if request.method == 'POST':
        data = request.get_json()
        logging.info('Request data from /get_unrated_movie : {}'.format(data))
        user_id = data['chat_id']
        unrated_movie_list = df_users_movies.loc[user_id]
        unrated_movie_list = unrated_movie_list[unrated_movie_list == 0]
        random_picked_unrated_movie_id = unrated_movie_list.sample().index.tolist()[0]
        title = df_movie_name_imdb.loc[random_picked_unrated_movie_id]['title']
        imdb_id = df_movie_name_imdb.loc[random_picked_unrated_movie_id]['imdbId']
        movie_info = {
            "id": random_picked_unrated_movie_id,
            "title": title,
            "url": 'https://www.imdb.com/title/tt{}/'.format(imdb_id)
        }
        logging.info('movie_info: {}'.format(movie_info))
        return jsonify(movie_info)


@app.route('/rate_movie', methods=['POST'])
def rate_movie():
    if request.method == 'POST':
        data = request.get_json()
        logging.info('Request data from /rate_movie : {}'.format(data))
        user_id = data['chat_id']
        movie_id = data['movie_id']
        rating = data['rating']
        df_users_movies[movie_id][user_id] = rating
        return jsonify({'status': 'success'})


@app.route('/recommend', methods=['POST'])
def recommend():
    if request.method == 'POST':
        data = request.get_json()
        logging.info('Request data from /recommend : {}'.format(data))
        user_id = data['chat_id']
        top_n = data['top_n']
        rated_movie_counts = df_users_movies.loc[user_id].value_counts().drop(0).sum()
        logging.info('rated_movie_counts: {}'.format(rated_movie_counts))
        movie_list = []
        if rated_movie_counts >= 10:
            top_n_neighbours = top_n_matches(user_id)
            recommend_movies = top_n_recommended(user_id, top_n_neighbours, top_n)
            movie_list = [{
                "title": df_movie_name_imdb.loc[movie_id].title,
                "url": 'https://www.imdb.com/title/tt{}/'.format(df_movie_name_imdb.loc[movie_id].imdbId)
            } for movie_id in [i[1] for i in recommend_movies]]
        return jsonify({'movies': movie_list})


if __name__ == '__main__':
    app.run()

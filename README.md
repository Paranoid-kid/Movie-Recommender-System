# Movie Recommender System

A movie recommender system using user-based collaborative filtering algorithm.

## Algorithm

[User-based collaborative filtering](https://en.wikipedia.org/wiki/Collaborative_filtering)

## Dataset

The dataset consists of 100,000 ratings on different movies by the users of the MovieLens recommender system:

- 100,000 ratings (1-5) from **600 users** on **9,000 movies**
- Each user has at least 20 movies
- Data about the movies and the users

>
> **MovieLens 100K movie ratings dataset** created by GroupLens at the University of Minnesota.
>
> https://grouplens.org/datasets/movielens/

## System Architecture

![image-1](https://raw.githubusercontent.com/Paranoid-kid/Image-Classifier-on-Telegram/master/img/2.png)

## Useage

User can use three Telegram bot commands to interact with recommender system.

- /start
  - A command to register with the application. If user is new, reply “Welcome!”, otherwise reply “Welcome back!”
- /rate
  - A command to ask the application to present a movie for rating. User should receive two messages:
    - A message containing the name of the movie, and the URL to the movie’s page on IMDB
    - A message asking for the user’s rating on this movie, with a custom keyboard
  - ![image-2](https://raw.githubusercontent.com/Paranoid-kid/Image-Classifier-on-Telegram/master/img/2.png)
- /recommend
  - A command to ask the application to recommend a list of movies based on previous ratings. On receiving this command, the system will send the **top 3** recommended movies for the user.
  - The server may return two different responses, depending on the number of ratings given by that user:
    - If the user has **10 or more** ratings, the server will return a list of recommended movies
    - If the user has **less than 10** ratings, the server will return an empty list and send the following message to the user: **“You have not rated enough movies, we cannot generate recommendation for you”**.
  - ![image-3](https://raw.githubusercontent.com/Paranoid-kid/Image-Classifier-on-Telegram/master/img/2.png)
  - ![image-4](https://raw.githubusercontent.com/Paranoid-kid/Image-Classifier-on-Telegram/master/img/2.png)
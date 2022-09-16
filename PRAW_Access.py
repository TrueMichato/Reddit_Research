import praw
import psaw
import json
import pandas as pd
import csv
from psaw import PushshiftAPI  # library Pushshift
import datetime as dt  # library for date management
import matplotlib.pyplot as plt  # library for plotting
from typing import List, Dict, Tuple, TypedDict, Type, Any
from tqdm import tqdm

from defaults import *


class Secrets(TypedDict):
    client_id: str
    client_secret: str
    user_agent: str
    redirect_uri: str
    refresh_token: str
    username: str
    password: str


def get_reddit() -> praw.Reddit:
    with open("client_secrets.json") as f:
        secrets: Secrets = json.loads(f.read())
    r = praw.Reddit(client_id=secrets['client_id'],
                    client_secret=secrets['client_secret'],
                    password=secrets['password'],
                    user_agent=secrets['user_agent'],
                    username=secrets['username'], )
    return r


reddit = get_reddit()
print(reddit.user.me())
reddit.read_only = True
pushshift = PushshiftAPI(reddit)

# # assume you have a praw.Reddit instance bound to variable `reddit`
# subreddit = reddit.subreddit("dndnext")
#
# print(subreddit.display_name)
# # Output: redditdev
# print(subreddit.title)
# # Output: reddit development
# print(subreddit.description)
# # Output: a subreddit for discussion of ...
#
# # assume you have a Subreddit instance bound to variable `subreddit`
# for submission in subreddit.hot(limit=None):
#     print(submission.title)
#     # Output: the submission's title
#     print(submission.score)
#     # Output: the submission's score
#     print(submission.id)
#     # Output: the submission's ID
#     print(submission.url)
#     # Output: the URL the submission points to or the submission's URL if it's a self post


def posts_to_dict(columns: List[str], post: praw.Reddit.submission) -> Dict[str, Any]:
    post_dict: Dict[str, Any] = {}
    for col in columns:
        try:
            post_dict[col] = getattr(post, col)
        except AttributeError:
            post_dict[col] = None
    return post_dict


def data_prep_posts(subreddits, start_time, end_time, filters, limit) -> pd.DataFrame:
    posts = list()
    for subreddit in tqdm(subreddits):
        posts += list(pushshift.search_submissions(
            subreddit=subreddit,  # Subreddit we want to audit
            after=start_time,  # Start date
            before=end_time,  # End date
            filter=filters,  # Column names we want to retrieve
            limit=limit))  # Max number of posts
    return pd.DataFrame([post.__dict__ for post in tqdm(posts)], columns=filters)  # Return dataframe for analysis

# def data_pred_praw_posts(ids: List[str], filters) -> pd.DataFrame:
#     posts: List[praw.Reddit.submission] = []
#     for id_ in ids:
#         posts.append(reddit.submission(id_))
#     posts_dicts: List[Dict[str, Any]] = [posts_to_dict(filters, post) for post in posts]
#     return pd.DataFrame(sorted(posts_dicts, key=len, reverse=True))  # Return dataframe for analysis


def count_posts_per_date(df_p, title, xlabel, ylabel):
    df_p.groupby([df_p.datetime.dt.date]).count().plot(y='id', rot=45, kind='bar', label='Posts')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.show()


def mean_comments_per_date(df_p, title, xlabel, ylabel):
    df_p.groupby([df_p.datetime.dt.date]).mean().plot(y='num_comments', rot=45, kind='line', label='Comments')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.show()


def main():
    subreddit = DND_SUBREDDITS_LIST
    start_time = int(dt.datetime(2020, 8, 23).timestamp())
    # Starting date for our search
    end_time = int(dt.datetime(2022, 8, 23).timestamp())
    # Ending date for our search
    filters = FILTERS
    limit = 20000  # Elements we want to receive
    # Call function for dataframe creation of comments
    df_posts = data_prep_posts(subreddit, start_time, end_time, filters, limit)
    # df_praw_posts = data_pred_praw_posts(df_posts['id'].to_list(), filters)
    # Drop the column on timestamp format
    # check_df = df_praw_posts == df_posts
    df_posts['datetime'] = df_posts['created_utc'].map(lambda t: dt.datetime.fromtimestamp(t))
    df_p = df_posts.drop('created_utc', axis=1)
    # # Sort the Row by datetime
    df_p = df_p.sort_values(by='datetime')
    # # Convert timestamp format to datetime for data analysis
    df_p["datetime"] = pd.to_datetime(df_p["datetime"])
    df_p.to_csv(f'dataset_general_dnd_posts_{start_time}_{end_time}.csv', sep=',',  header=True, index=False, columns=COLUMNS)
    # count_posts_per_date(df_p, 'Post per day', 'Days', 'posts')
    # mean_comments_per_date(df_p, 'Average comments per day', 'Days', 'comments')
    # most_active_author(df_p, 'Most active users',          #Function to plot the most active users on the subreddit
    #                    'Posts', 'Users', 10)
    # get_posts_orign(df_p, 'Origin of crosspostings',       #Function to que the orgin form the crossposting
    #                 'Crossposts', 'Origins', 10,
    #                 subreddit)


main()

import os

import gradio as gr
import praw
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()
# Initialize Reddit instance
reddit = praw.Reddit(
    client_id=os.getenv("client_id"),
    client_secret=os.getenv("client_secret"),
    user_agent=os.getenv("user_agent"),
    username=os.getenv("username"),
    password=os.getenv("password"),
)


# Define function to search Reddit and return results
def search_reddit(query):
    # Search Reddit for the query
    subreddit = reddit.subreddit("all")
    search_results = subreddit.search(query, limit=10)
    data = {}
    # Extract URLs and pinpoint answers
    for submission in search_results:
        submission.comments.replace_more(limit=0)
        for comment in submission.comments.list():
            data[submission.title] = {
                "URL": submission.url,
                "Comment": comment.body,
                "Comment URL": f"{submission.url}{comment.id}",
            }
    # Get the value of the key from the environment variables
    key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are taking a query and a list of data from which you will return the most relevant answer along with its commment url.",
            },
            {"role": "user", "content": f"""Query is: {query} Data is: {data}"""},
        ],
    )
    message = response.choices[0].message.content
    return message


# Create interface
iface = gr.Interface(
    fn=search_reddit, inputs="textbox", outputs="text", title="Reddit Search"
)

iface.launch()

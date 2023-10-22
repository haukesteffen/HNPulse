import os
import pandas as pd
import openai
from sqlalchemy import create_engine

engine = create_engine(f'postgresql://{os.environ["DBUSER"]}:{os.environ["DBPW"]}@localhost:5432/hn')
openai.api_key = os.getenv("OPENAI_API_KEY")

def _get_prompt(id):
    story_query = f"""
    SELECT *
    FROM stories
    WHERE id = {id}
    """

    comments_query = f"""
    SELECT *
    FROM comments
    WHERE parent = {id}
    """

    with engine.begin() as con:
        story_df = pd.read_sql(con=con, sql=story_query)
        comments_df = pd.read_sql(con=con, sql=comments_query)

    prompt = f"""
    This is a json-formatted Hacker News Post (delimited in three single quotes):
    '''
    {story_df.to_json()}
    '''
    Following are the comments to the aforementioned Hacker News Post (delimited in three single quotes):
    {comments_df.to_json()}
    """

    return prompt

def hnquery(id):
    test_prompt = _get_prompt(id)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a tech journalist in silicon valley, writing blog posts about tech news. You get as input Hacker News posts and respective comments in json format. Write a short summary in form of a blog post. Do not mention Hacker News. Do not mention posts. Do not mention comments. Write the blog post as a standalone piece and format it accordingly."},
            {"role": "user", "content": f"{test_prompt}"}
        ]
    )
    response_message = response["choices"][0]["message"]
    return response_message['content']
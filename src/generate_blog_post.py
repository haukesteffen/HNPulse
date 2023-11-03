import openai
import pandas as pd
from sqlalchemy import create_engine
import os

# Set up OpenAI API key
openai.api_key = os.environ['OPENAI_API_KEY']

# Connect to database
engine = create_engine(f'postgresql://{os.environ["DBUSER"]}:{os.environ["DBPW"]}@localhost:5432/hn')

# Post_id to summarize
post_id = 3078440  

# Define the SQL query to retrieve the post and comments data with hierarchy
sql_query = f"""
WITH RECURSIVE CommentHierarchy AS (
    SELECT
        c.id AS comment_id,
        c.text AS comment_text,
        c.by AS comment_author,
        c.parent AS parent_id
    FROM
        comments c
    WHERE
        c.parent = {post_id}

    UNION ALL

    SELECT
        c.id AS comment_id,
        c.text AS comment_text,
        c.by AS comment_author,
        c.parent AS parent_id
    FROM
        comments c
    INNER JOIN
        CommentHierarchy ch ON c.parent = ch.comment_id
)

-- Select the hierarchical comments
SELECT
	s.id AS id,
	s.title AS text,
	s.by AS author,
	NULL AS parent
FROM stories s
WHERE s.id = {post_id}

UNION ALL

SELECT
    ch.comment_id AS id,
    ch.comment_text AS text,
    ch.comment_author AS author,
    ch.parent_id AS parent
FROM
    CommentHierarchy ch;
"""

# Execute the SQL query to retrieve the comments hierarchy
with engine.begin() as con:
    comment_df = pd.read_sql_query(sql_query, con, coerce_float=False)

print(comment_df)
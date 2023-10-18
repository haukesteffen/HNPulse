import os
import requests
import numpy as np
import pandas as pd
from datetime import datetime, timezone
from sqlalchemy import create_engine

class Scraper:
    def __init__(self):
        self._empty_dicts()
        self.client = requests.Session()
        self.engine = create_engine(f'postgresql://{os.environ["DBUSER"]}:{os.environ["DBPW"]}@localhost:5432/hn')
        self.max_id = self._get_max()
        self.last_id = self._get_last()

    def begin_scraping(self):
        self._empty_dicts()
        for idx in range(self._get_last()+1, self._get_max()+1):
            self._to_dict(idx)
            if idx % 1000 == 0:
                self._convert_dicts()
                self._insert_sql()
                self._empty_dicts()

    def _empty_dicts(self):
        self.stories = {
            'id':[],
            'title':[],
            'by':[],
            'descendants':[],
            'score':[],
            'time':[],
            'url':[]
        }
        self.jobs = {
            'id':[],
            'title':[],
            'text':[],
            'by':[],
            'score':[],
            'time':[],
            'url':[],
        }
        self.comments = {
            'id':[],
            'text':[],
            'by':[],
            'time':[]
        }
        self.polls = {
            'id':[],
            'title':[],
            'text':[],
            'by':[],
            'descendants':[],
            'score':[],
            'time':[],
        }
        self.pollopts = {
            'id':[],
            'text':[],
            'by':[],
            'poll':[],
            'score':[],
            'time':[],
        }
        self.parents = {
            'item':[],
            'parent':[],
            'type':[],
        }
        self.deleted = {
            'item':[]
        }
        self.dead = {
            'item':[]
        }
        self.scrape = {
            'id':[],
            'scrape_time':[]
        }
        self.skipped = []

    def _get(self, id):
        url = f'https://hacker-news.firebaseio.com/v0/item/{id}.json'
        response = self.client.get(url)
        return response.json()

    def _get_last(self):
        last_query = """
        SELECT id
        FROM scrape
        ORDER BY scrape_time DESC
        LIMIT 1
        """
    
        with self.engine.begin() as con:
            return pd.read_sql(sql=last_query, con=con).values[0][0]

    def _get_max(self):
        url = 'https://hacker-news.firebaseio.com/v0/maxitem.json'
        response = self.client.get(url)
        return int(response.text)

    def _to_dict(self, input_id):
        response = self._get(input_id)

        # sanity check
        try:
            id = response['id']
            type = response['type']
        except KeyError:
            self.skipped.append(id)
            return
        
        # get scrape time
        self.scrape['id'].append(input_id)
        self.scrape['scrape_time'].append(datetime.now(timezone.utc))

        # check if deleted
        try:
            if response['deleted']:
                self.deleted['item'].append(response['id'])
        except KeyError:
            pass

        # check if dead
        try: 
            if response['dead']:
                self.dead['item'].append(response['id'])
        except KeyError:
            pass

        try:
            title = response['title']
        except KeyError:
            title = np.nan

        try:
            text = response['text']
        except KeyError:
            text = np.nan

        try:
            by = response['by']
        except KeyError:
            by = np.nan
        
        try:
            score = response['score']
        except KeyError:
            score = np.nan
            
        try:
            time = datetime.fromtimestamp(int(response['time']))
        except KeyError:
            time = np.nan

        try:
            url = response['url']
        except KeyError:
            url = np.nan

        try:
            descendants = response['descendants']
        except KeyError:
            descendants = np.nan

        try:
            poll = response['poll']
        except KeyError:
            poll = np.nan

        try:
            parent = response['parent']
        except KeyError:
            parent = np.nan

        if type == 'story':
            self.stories['id'].append(id)
            self.stories['title'].append(title)
            self.stories['by'].append(by)
            self.stories['descendants'].append(descendants)
            self.stories['score'].append(score)
            self.stories['time'].append(time)
            self.stories['url'].append(url)

        elif type == 'job':
            self.jobs['id'].append(id)
            self.jobs['title'].append(title)
            self.jobs['text'].append(text)
            self.jobs['by'].append(by)
            self.jobs['score'].append(score)
            self.jobs['time'].append(time)
            self.jobs['url'].append(url)

        elif type == 'comment':
            self.parents['item'].append(id)
            self.parents['parent'].append(parent)
            self.parents['type'].append('comment')
            self.comments['id'].append(id)
            self.comments['text'].append(text)
            self.comments['by'].append(by)
            self.comments['time'].append(time)

        elif type == 'poll':
            self.polls['id'].append(id)
            self.polls['title'].append(title)
            self.polls['text'].append(text)
            self.polls['by'].append(by)
            self.polls['descendants'].append(descendants)
            self.polls['score'].append(score)
            self.polls['time'].append(time)

        elif type == 'pollopt':
            self.pollopts['id'].append(id)
            self.pollopts['text'].append(text)
            self.pollopts['by'].append(by)
            self.pollopts['poll'].append(poll)
            self.pollopts['score'].append(score)
            self.pollopts['time'].append(time)

    def _convert_dicts(self):
        self.scrape_df = pd.DataFrame(self.scrape)
        self.skipped_df = pd.DataFrame(self.skipped)
        self.deleted_df = pd.DataFrame(self.deleted)
        self.dead_df = pd.DataFrame(self.dead)
        self.stories_df = pd.DataFrame(self.stories)
        self.jobs_df = pd.DataFrame(self.jobs)
        self.parents_df = pd.DataFrame(self.parents)
        self.comments_df = pd.DataFrame(self.comments)
        self.polls_df = pd.DataFrame(self.polls)
        self.pollopts_df = pd.DataFrame(self.pollopts)

    def _insert_sql(self):
        with self.engine.begin() as con:
            self.scrape_df.to_sql(name='scrape', con=con, if_exists='append', index=False)
            self.skipped_df.to_sql(name='skipped', con=con, if_exists='append', index=False)
            self.deleted_df.to_sql(name='deleted', con=con, if_exists='append', index=False)
            self.dead_df.to_sql(name='dead', con=con, if_exists='append', index=False)
            self.stories_df.to_sql(name='stories', con=con, if_exists='append', index=False)
            self.jobs_df.to_sql(name='jobs', con=con, if_exists='append', index=False)
            self.parents_df.to_sql(name='parents', con=con, if_exists='append', index=False)
            self.comments_df.to_sql(name='comments', con=con, if_exists='append', index=False)
            self.polls_df.to_sql(name='polls', con=con, if_exists='append', index=False)
            self.pollopts_df.to_sql(name='pollopts', con=con, if_exists='append', index=False)


def main():
    scraper = Scraper()
    scraper.begin_scraping()

if __name__ == '__main__':
    main()

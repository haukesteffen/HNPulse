import asyncio
import aiohttp
import os
import html
import requests
import numpy as np
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from time import perf_counter


class Scraper:
    def __init__(self, batch_size=1000, verbose=False):
        self.verbose = verbose
        self.batch_size = batch_size
        self._empty_dicts()
        self.client = requests.Session()
        self.engine = create_engine(f'postgresql://{os.environ["DBUSER"]}:{os.environ["DBPW"]}@localhost:5432/hn')
        self.max_id = self._get_max()
        self.last_id = self._get_last()
        if self.verbose:
            print(f'Initialized scraper. Last ID: {self.last_id}, Max ID: {self.max_id}, Batch Size: {self.batch_size}')

    async def begin_scraping(self):
        while self.last_id < self.max_id:
            start = perf_counter()
            self._empty_dicts()
            self.ids = range(self.last_id+1, min(self.last_id+1+self.batch_size, self.max_id+1))
            self.jsons = await self._scrape_batch(self.ids)
            for json in self.jsons:
                self._to_dict(json)
            self._convert_dicts()
            self._insert_sql()
            self.last_id = self._get_last()
            self.max_id = self._get_max()
            stop = perf_counter()
            if self.verbose:
                print(f'Processing of batch took {(stop-start):.2f} seconds')

    async def _scrape_batch(self, ids):
        async with aiohttp.ClientSession() as session:
            jsons = await self._fetch_batch(session, ids)
            return jsons

    async def _fetch_batch(self, s, ids):
        tasks = []
        for id in ids:
            task = asyncio.create_task(self._fetch(s, id))
            tasks.append(task)
        res = await asyncio.gather(*tasks)
        return res

    async def _fetch(self, s, id):
        async with s.get(f'https://hacker-news.firebaseio.com/v0/item/{id}.json') as r:
            if r.status != 200:
                r.raise_for_status()
            return await r.json()

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
            'time':[],
            'parent':[]
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

    def _to_dict(self, json):
        # sanity check
        try:
            id = json['id']
            type = json['type']
        except KeyError:
            self.skipped.append(id)
            return
        
        # get scrape time
        self.scrape['id'].append(id)
        self.scrape['scrape_time'].append(datetime.now())

        # check if deleted
        try:
            if json['deleted']:
                self.deleted['item'].append(json['id'])
        except KeyError:
            pass

        # check if dead
        try: 
            if json['dead']:
                self.dead['item'].append(json['id'])
        except KeyError:
            pass

        try:
            title = json['title']
            title = html.unescape(title)
            title = title.replace('\\x00','')
        except KeyError:
            title = np.nan

        try:
            text = json['text']
            text = html.unescape(text)
            text = text.replace('\x00','')
        except KeyError:
            text = np.nan

        try:
            by = json['by']
        except KeyError:
            by = np.nan
        
        try:
            score = json['score']
        except KeyError:
            score = np.nan
            
        try:
            time = datetime.fromtimestamp(int(json['time']))
        except KeyError:
            time = np.nan

        try:
            url = json['url']
        except KeyError:
            url = np.nan

        try:
            descendants = json['descendants']
        except KeyError:
            descendants = np.nan

        try:
            poll = json['poll']
        except KeyError:
            poll = np.nan

        try:
            parent = json['parent']
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
            self.comments['id'].append(id)
            self.comments['text'].append(text)
            self.comments['by'].append(by)
            self.comments['time'].append(time)
            self.comments['parent'].append(parent)

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
            self.comments_df.to_sql(name='comments', con=con, if_exists='append', index=False)
            self.polls_df.to_sql(name='polls', con=con, if_exists='append', index=False)
            self.pollopts_df.to_sql(name='pollopts', con=con, if_exists='append', index=False)


async def main():
    scraper = Scraper(batch_size=10000, verbose=True)
    await scraper.begin_scraping()

if __name__ == '__main__':
    asyncio.run(main())

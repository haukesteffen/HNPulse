DROP TABLE IF EXISTS stories;
DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS polls;
DROP TABLE IF EXISTS pollopts;
DROP TABLE IF EXISTS parents;
DROP TABLE IF EXISTS deleted;
DROP TABLE IF EXISTS dead;
DROP TABLE IF EXISTS skipped;


CREATE TABLE stories (
    id INTEGER,
    title TEXT,
    by INTEGER,
    descendants INTEGER,
    score INTEGER,
    time TIMESTAMP,
    url TEXT,
  	PRIMARY KEY (id)
);

CREATE TABLE jobs (
    id INTEGER,
    title TEXT,
    text TEXT,
    by INTEGER,
    score INTEGER,
    time TIMESTAMP,
    url TEXT,
  	PRIMARY KEY (id)
);

CREATE TABLE comments (
    id INTEGER,
    text TEXT,
    by INTEGER,
    time TIMESTAMP,
  	PRIMARY KEY (id)
);

CREATE TABLE polls (
    id INTEGER,
    title TEXT,
    text TEXT,
    by INTEGER,
    descendants INTEGER,
    score INTEGER,
    time TIMESTAMP,
  	PRIMARY KEY (id)
);

CREATE TABLE pollopts (
    id INTEGER,
    text TEXT,
    by INTEGER,
    poll INTEGER,
    score INTEGER,
    time TIMESTAMP,
    CONSTRAINT fk_poll FOREIGN KEY(poll) REFERENCES polls(id),
  	PRIMARY KEY (id)
);

CREATE TABLE parents (
    item INTEGER,
    parent INTEGER,
    type varchar(7),
  	PRIMARY KEY (item)
);

CREATE TABLE deleted (
    item INTEGER,
  	PRIMARY KEY (item)
);

CREATE TABLE dead (
    item INTEGER,
  	PRIMARY KEY (item)
);

CREATE TABLE scrape (
    last_id INTEGER
);

CREATE TABLE skipped (
    item INTEGER
);
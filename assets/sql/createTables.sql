DROP TABLE IF EXISTS stories;
DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS polls;
DROP TABLE IF EXISTS pollopts;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS parents;
DROP TABLE IF EXISTS deleted;
DROP TABLE IF EXISTS dead;

CREATE TABLE users (
    id SERIAL,
    username VARCHAR(15),
    created TIMESTAMP,
    karma INTEGER,
    about TEXT,
  	PRIMARY KEY (id)
);

CREATE TABLE stories (
    id INTEGER,
    title TEXT,
    by_id INTEGER,
    descendants INTEGER,
    score INTEGER,
    time TIMESTAMP,
    url TEXT,
    CONSTRAINT fk_by FOREIGN KEY(by_id) REFERENCES users(id),
  	PRIMARY KEY (id)
);

CREATE TABLE jobs (
    id INTEGER,
    title TEXT,
    text TEXT,
    by_id INTEGER,
    score INTEGER,
    time TIMESTAMP,
    url TEXT,
    CONSTRAINT fk_by FOREIGN KEY(by_id) REFERENCES users(id),
  	PRIMARY KEY (id)
);

CREATE TABLE comments (
    id INTEGER,
    text TEXT,
    by_id INTEGER,
    time TIMESTAMP,
    CONSTRAINT fk_by FOREIGN KEY(by_id) REFERENCES users(id),
  	PRIMARY KEY (id)
);

CREATE TABLE polls (
    id INTEGER,
    title TEXT,
    text TEXT,
    by_id INTEGER,
    descendants INTEGER,
    score INTEGER,
    time TIMESTAMP,
    CONSTRAINT fk_by FOREIGN KEY(by_id) REFERENCES users(id),
  	PRIMARY KEY (id)
);

CREATE TABLE pollopts (
    id INTEGER,
    text TEXT,
    by_id INTEGER,
    poll INTEGER,
    score INTEGER,
    time TIMESTAMP,
    CONSTRAINT fk_by FOREIGN KEY(by_id) REFERENCES users(id),
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
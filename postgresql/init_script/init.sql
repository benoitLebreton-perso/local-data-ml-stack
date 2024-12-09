CREATE DATABASE mlflowdb;
CREATE DATABASE ucdb;
CREATE DATABASE web_app;
CREATE DATABASE shop;

ALTER DATABASE web_app OWNER TO postgres;
ALTER DATABASE shop OWNER TO postgres;
\connect web_app

CREATE TABLE users
(id INT, surname char(50));

INSERT INTO users (id, surname) VALUES
    (1,'MICHEL'),
    (2,'POLNAREFF'),
    (3,'JOESTAR'),
    (4,'PLATINIUM');

ALTER DATABASE shop OWNER TO postgres;
\connect shop

CREATE TABLE transactions
(id int, user_id int, time_stamp timestamp, amount decimal);

INSERT INTO transactions (id,user_id,time_stamp,amount) VALUES
    (1,1,'2020-01-01 04:05:06',50),
    (2,1,'2020-01-02 04:05:06',100),
    (3,1,'2020-01-03 04:05:06',100),
    (4,2,'2020-01-03 04:05:06',1000),
    (5,2,'2020-01-03 04:05:06',1500),
    (6,3,'2020-01-04 04:05:06',10);
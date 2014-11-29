#!/usr/bin/env python
import pymysql
import urllib2
import json
import collections
import types
import time
import datetime
import sys
from pprint import pprint

# Setup ------------------------------------------

# Database connection
conn = pymysql.connect(host='127.0.0.1', port=3306, user='scripts', passwd='scripts', db='sentiment', charset='utf8')
cur = conn.cursor()

print
print "Creating new batch..."

cur.execute("INSERT INTO result_batch (description) values (null);")
conn.commit();
batchId = cur.lastrowid

print "Done. New batch is " + str(batchId)
print "Calculating trending..."
cur.execute("""insert into result (description, positive, result_batch_id, result_type_id) select entity, num, %s batch, 1 type from (select entity, count(entity) num from entities e inner join comments c on e.id_comment_local = c.id inner join threads t on c.id_thread = t.id  where entity not in 	(select word from words inner join category on words.id_category = category.id where category.id = 1) and t.created >= adddate(now(), INTERVAL -1 DAY) group by entity order by count(entity) desc limit 10) subq""", (batchId))
conn.commit()
print "Calculating loved..."
cur.execute("""insert into result (description, positive, result_batch_id, result_type_id) select entity, sum(e.score), %s batch, 2 type from entities e  inner join comments c on e.id_comment_local = c.id inner join threads t on c.id_thread = t.id  where entity not in (select word from words inner join category on words.id_category = category.id where category.id = 1) and t.created >= adddate(now(), INTERVAL -1 DAY) and e.score > 0 group by entity having sum(e.score) <> 0 order by sum(e.score) desc limit 5""", (batchId))
conn.commit()
print "Calculating hated..."
cur.execute("""insert into result (description, negative, result_batch_id, result_type_id) select entity, sum(e.score), %s batch, 3 type from entities e  inner join comments c on e.id_comment_local = c.id inner join threads t on c.id_thread = t.id  where entity not in (select word from words inner join category on words.id_category = category.id where category.id = 1) and t.created >= adddate(now(), INTERVAL -1 DAY) and e.score < 0 group by entity having sum(e.score) <> 0 order by sum(e.score) asc limit 5""", (batchId))
conn.commit()
print "Calculating thread count..."
cur.execute("""insert into result (description, positive, result_batch_id, result_type_id) select 'Count', count(*), %s batch, 4 type from threads where created >= adddate(now(), INTERVAL -1 DAY)""", (batchId))
conn.commit()
print "Calculating teams..."
cur.execute("""insert into result (description, positive, negative, result_batch_id, result_type_id) select entity, sum(if(e.score > 0, e.score, 0)) as positive, sum(if(e.score < 0, e.score, 0)) negative, %s, 5 from entities e inner join comments c on e.id_comment_local = c.id inner join threads t on c.id_thread = t.id where entity not in (select word from words inner join category on words.id_category = category.id where category.id = 1) and entity in (select word from words inner join category on words.id_category = category.id where category.id = 2) and t.created >= adddate(now(), INTERVAL -1 DAY) group by entity having sum(e.score) <> 0 order by entity""", (batchId));
conn.commit()
print "Calculating players..."
cur.execute("""insert into result (description, positive, negative, result_batch_id, result_type_id) select entity, sum(if(e.score > 0, e.score, 0)) as positive, sum(if(e.score < 0, e.score, 0)) negative, %s, 6 from entities e inner join comments c on e.id_comment_local = c.id inner join threads t on c.id_thread = t.id where entity not in (select word from words inner join category on words.id_category = category.id where category.id = 1) and entity in (select word from words inner join category on words.id_category = category.id where category.id = 3) and t.created >= adddate(now(), INTERVAL -1 DAY) group by entity having sum(e.score) <> 0 order by entity""", (batchId))
conn.commit()
print "Calculating champions..."
cur.execute("""insert into result (description, positive, negative, result_batch_id, result_type_id) select entity, sum(if(e.score > 0, e.score, 0)) as positive, sum(if(e.score < 0, e.score, 0)) negative, %s, 7 from entities e inner join comments c on e.id_comment_local = c.id inner join threads t on c.id_thread = t.id where entity not in (select word from words inner join category on words.id_category = category.id where category.id = 1) and entity in (select word from words inner join category on words.id_category = category.id where category.id = 4) and t.created >= adddate(now(), INTERVAL -1 DAY) group by entity having sum(e.score) <> 0 order by entity;""", (batchId))
conn.commit()
print "Calculating overall..."
cur.execute("""insert into result (description, positive, negative, result_batch_id, result_type_id) select result, sum(positive) positive, sum(negative) negative, %s, 8 from ( select 'result', if (e.score > 0, e.score, 0) positive, if (e.score < 0, e.score, 0) negative from entities e inner join comments c on e.id_comment_local = c.id inner join threads t on c.id_thread = t.id where entity not in ( select word from words inner join category on words.id_category = category.id where category.id = 1 ) and t.created >= adddate(now(), INTERVAL -1 DAY) ) t1;""", (batchId))
conn.commit()
print "All done"

# Close the connection
cur.close()
conn.close()

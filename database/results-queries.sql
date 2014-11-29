--------------------------------------------------------------------------------------------------
-- Results based on the sum of polarities. Does not currently take subjectivity into consideration
--------------------------------------------------------------------------------------------------

-----------------------------------
-- SELECT FORM - Use it for testing
-----------------------------------

-- 1. Number of Threads
select count(*) from threads where created >= adddate(now(), INTERVAL -1 DAY);

-- 2. Overall
select category, count
from (
  select cat.category, count(e.entity) as count
  from entities e
  inner join comments c on e.id_comment_local = c.id
  inner join threads t on c.id_thread = t.id
  inner join words w on e.entity = w.word
  inner join category cat on w.id_category = cat.id
  where entity not in (select word from words inner join category on words.id_category = category.id where category.id = 1)
  and t.created >= adddate(now(), INTERVAL -1 DAY)
  group by cat.category
) t1

union

select label, count
from (
  select 'others' as label, count(e.entity) as count
  from entities e
  inner join comments c on e.id_comment_local = c.id
  inner join threads t on c.id_thread = t.id
  inner join words w on e.entity = w.word
  inner join category cat on w.id_category = cat.id
  where entity not in (select word from words inner join category on words.id_category = category.id where category.id = 2 or category.id = 3 or category.id = 4)
  and t.created >= adddate(now(), INTERVAL -1 DAY)
  group by label
) t2;

-- 3. Trending
select entity, count(entity) as count, sum(if(e.score > 0, e.score, 0)) as positive, sum(if(e.score < 0, e.score, 0)) as negative
from entities e
inner join comments c on e.id_comment_local = c.id
inner join threads t on c.id_thread = t.id

where entity not in
  (select word from words inner join category on words.id_category = category.id where category.id = 1)
and t.created >= adddate(now(), INTERVAL -1 DAY)
group by entity order by count(entity) desc limit 10;

-- 4. Teams (category.id = 2), Players (category.id = 3), Champions (category.id = 4)
select entity, sum(if(e.score > 0, e.score, 0)) as positive, sum(if(e.score < 0, e.score, 0)) negative
from entities e
inner join comments c on e.id_comment_local = c.id
inner join threads t on c.id_thread = t.id

where entity not in (select word from words inner join category on words.id_category = category.id where category.id = 1)
and entity in (select word from words inner join category on words.id_category = category.id where category.id = 4)
and t.created >= adddate(now(), INTERVAL -1 DAY)

group by entity
having sum(e.score) <> 0
order by sum(if(e.score > 0, e.score, 0));

----------------------------------------------
-- INSERT FORM - These queries go into the results.py script
-- Be mindful of the "result_type_id" field. They should match the category in the "result_type" table
----------------------------------------------

-- 0. New Results Batch
insert into result_batch (description) values (null);

-- 1: Trending
insert into result (description, positive, result_batch_id, result_type_id) select entity, num, (select max(id) from result_batch) batch, 1 type from (select entity, count(entity) num from entities e inner join comments c on e.id_comment_local = c.id inner join threads t on c.id_thread = t.id  where entity not in 	(select word from words inner join category on words.id_category = category.id where category.id = 1) and t.created >= adddate(now(), INTERVAL -1 DAY) group by entity order by count(entity) desc limit 10) subq;

-- 2: Loved
insert into result (description, positive, result_batch_id, result_type_id) select entity, sum(e.score), (select max(id) from result_batch) batch, 2 type from entities e  inner join comments c on e.id_comment_local = c.id inner join threads t on c.id_thread = t.id  where entity not in (select word from words inner join category on words.id_category = category.id where category.id = 1) and t.created >= adddate(now(), INTERVAL -1 DAY) and e.score > 0 group by entity having sum(e.score) <> 0 order by sum(e.score) desc limit 5;

-- 3: Hated
insert into result (description, negative, result_batch_id, result_type_id) select entity, sum(e.score), (select max(id) from result_batch) batch, 3 type from entities e  inner join comments c on e.id_comment_local = c.id inner join threads t on c.id_thread = t.id  where entity not in (select word from words inner join category on words.id_category = category.id where category.id = 1) and t.created >= adddate(now(), INTERVAL -1 DAY) and e.score < 0 group by entity having sum(e.score) <> 0 order by sum(e.score) asc limit 5;

-- 4: Number of Threads
insert into result (description, positive, result_batch_id, result_type_id) select 'Count', count(*), (select max(id) from result_batch) batch, 4 type from threads where created >= adddate(now(), INTERVAL -1 DAY);

-- 5: Teams
insert into result (description, positive, negative, result_batch_id, result_type_id) 
select entity, sum(if(e.score > 0, e.score, 0)) as positive, sum(if(e.score < 0, e.score, 0)) negative, (select max(id) from result_batch), 5

from entities e
inner join comments c on e.id_comment_local = c.id
inner join threads t on c.id_thread = t.id

where entity not in (select word from words inner join category on words.id_category = category.id where category.id = 1)
and entity in (select word from words inner join category on words.id_category = category.id where category.id = 2)
and t.created >= adddate(now(), INTERVAL -1 DAY)

group by entity
having sum(e.score) <> 0
order by entity;

-- 6: Players
insert into result (description, positive, negative, result_batch_id, result_type_id) 
select entity, sum(if(e.score > 0, e.score, 0)) as positive, sum(if(e.score < 0, e.score, 0)) negative, (select max(id) from result_batch), 6

from entities e
inner join comments c on e.id_comment_local = c.id
inner join threads t on c.id_thread = t.id

where entity not in (select word from words inner join category on words.id_category = category.id where category.id = 1)
and entity in (select word from words inner join category on words.id_category = category.id where category.id = 3)
and t.created >= adddate(now(), INTERVAL -1 DAY)

group by entity
having sum(e.score) <> 0
order by entity;

-- 7: Champions
insert into result (description, positive, negative, result_batch_id, result_type_id) 
select entity, sum(if(e.score > 0, e.score, 0)) as positive, sum(if(e.score < 0, e.score, 0)) negative, (select max(id) from result_batch), 7

from entities e
inner join comments c on e.id_comment_local = c.id
inner join threads t on c.id_thread = t.id

where entity not in (select word from words inner join category on words.id_category = category.id where category.id = 1)
and entity in (select word from words inner join category on words.id_category = category.id where category.id = 4)
and t.created >= adddate(now(), INTERVAL -1 DAY)

group by entity
having sum(e.score) <> 0
order by entity;

-- 8: Overall
insert into result(description, positive, negative, result_batch_id, result_type_id)
select result, sum(positive) positive, sum(negative) negative, (select max(id) from result_batch), 8

from (
  select 'result', if (e.score > 0, e.score, 0) positive, if (e.score < 0, e.score, 0) negative
  from entities e
  inner join comments c on e.id_comment_local = c.id
  inner join threads t on c.id_thread = t.id
  where entity not in (
    select word from words inner join category on words.id_category = category.id where category.id = 1
  ) and t.created >= adddate(now(), INTERVAL -1 DAY)
) t1;

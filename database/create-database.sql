CREATE SCHEMA sentiment DEFAULT CHARSET 'utf8' COLLATE 'utf8_general_ci';

USE sentiment;

CREATE TABLE threads (
id int primary key not null auto_increment,
id_thread varchar(16) not null unique key,
id_sub int not null,
title text not null,
url varchar(255) not null,
score int not null,
created timestamp
) engine=innodb;

CREATE TABLE comments (
id int primary key not null auto_increment,
id_comment varchar(16) not null unique key,
id_thread int not null,
comment text not null,
url varchar(255) not null,
score int not null,
created timestamp
) engine=innodb;

CREATE TABLE logs (
id int primary key not null auto_increment,
startingTime timestamp not null,
endingTime timestamp not null,
newThreads int not null,
ignoredThreads int not null,
newComments int not null,
ignoredComments int not null
) engine=innodb;

CREATE TABLE `entities` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_comment_local` int(11) NOT NULL,
  `id_comment` varchar(16) NOT NULL,
  `entity` varchar(255) NOT NULL,
  `word` varchar(255) NOT NULL,
  `score` double DEFAULT NULL,
  `sub` double NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;

CREATE TABLE category (
id int primary key not null auto_increment,
category varchar(255) not null
) engine=innodb;

INSERT INTO category (category) values
("exclude"),
("teams"),
("players"),
("champions");

-- Words related to analysis
-- word_group referst o words that should be treated as the same. Set same number for words that mean the same thing
CREATE TABLE words (
id int primary key not null auto_increment,
id_category int NOT NULL,
word varchar(255) NOT NULL,
word_group int,
created timestamp
) engine=innodb;

create table result (
id int primary key not null auto_increment,
description varchar(255),
positive double default null,
negative double default null,
result_batch_id int not null,
result_type_id int not null,
created timestamp not null default current_timestamp) engine=innodb;

create table result_batch (
id int primary key not null auto_increment,
description varchar(50),
created timestamp not null default current_timestamp) engine=innodb;

create table result_type (
id int primary key not null auto_increment,
type varchar(255) not null) engine=innodb;

-- Create the result types
insert into result_type(type) values ("Trending"); -- 1
insert into result_type(type) values ("Loved"); -- 2, not currently used
insert into result_type(type) values ("Hated"); -- 3, not currently used
insert into result_type(type) values ("Number of Threads"); -- 4
insert into result_type(type) values ("Teams"); -- 5
insert into result_type(type) values ("Players"); -- 6
insert into result_type(type) values ("Champions"); -- 7
insert into result_type(type) values ("Overall"); -- 8

-- Create the constraints
ALTER TABLE words ADD FOREIGN KEY (id_category) references category(id);
ALTER TABLE comments ADD FOREIGN KEY (id_thread) references threads(id);
ALTER TABLE entities ADD FOREIGN KEY (id_comment_local) references comments(id);

ALTER TABLE result ADD FOREIGN KEY (result_batch_id) references result_batch(id);
ALTER TABLE result ADD FOREIGN KEY (result_type_id) references result_type(id);

create user 'scripts'@'localhost' identified by 'scripts';
grant select, insert, update, delete on sentiment.* to 'scripts'@'localhost';
create user 'processor'@'localhost' identified by 'processor';
grant select, insert, update, delete on sentiment.* to 'processor'@'localhost';
flush privileges;

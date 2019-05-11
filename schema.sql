CREATE TABLE IF NOT EXISTS quests(
	chat_id int NOT NULL,
	qid int NOT NULL,
	name varchar(255),
	difficulty int,
	importance int,
	state int DEFAULT 0,
	UNIQUE(chat_id, qid)
);


CREATE TABLE IF NOT EXISTS side_quests(
	chat_id int NOT NULL,
	qid int NOT NULL,
	name varchar(255),
	difficulty int,
	importance int,
	state int DEFAULT 0,
	UNIQUE(chat_id, qid)
);


CREATE TABLE IF NOT EXISTS points(
	chat_id int PRIMARY KEY,
	points int
	);


CREATE TABLE IF NOT EXISTS state(
	chat_id int PRIMARY KEY,
	state varchar(10),
	extra varchar(10)
);


CREATE TABLE IF NOT EXISTS tokens(
	chat_id int,
	token varchar(36) PRIMARY KEY
);

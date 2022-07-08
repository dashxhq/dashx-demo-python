CREATE TABLE [IF NOT EXISTS] user (
   id varchar(36) PRIMARY KEY,
   first_name varchar(50) NOT NULL,
   last_name varchar(50),
   email varchar(50) UNIQUE NOT NULL,
   password varchar(50) NOT NULL
);

drop table if exists weather;
create table weather (
    id integer primary key autoincrement,
    date timestamp,
    temperature float,
    humidity float,
    pressure float
);

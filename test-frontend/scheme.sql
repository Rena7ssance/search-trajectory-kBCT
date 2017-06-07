drop table if exists admins;
create table admins (
    id integer primary key autoincrement,
    admin_name text primary key not null,
    password text not null
);
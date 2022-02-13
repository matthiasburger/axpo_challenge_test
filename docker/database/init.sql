drop database if exists time_series;
create database time_series;

CREATE USER 'matthias'@'localhost' IDENTIFIED BY 'new_password' PASSWORD EXPIRE NEVER;
GRANT ALL ON time_series.* TO 'matthias'@'localhost';

This project arose as the company I worked for rapidly grew, and with it a feeling of losing connectedness with coworkers. CoffeeChats is an attempted solution to maintain a community, and to unite remote and on-site employees. A SQLite DB containing the names, emails, and departments -- as well as previous pairings -- is used alongside the Google Calendar API. This lets us programatically iterate through employee calendars, find a mutually free slot, and place a short meeting on their calendar. 

Requirements
------------
Thanks to the Google Python Quickstart (https://developers.google.com/google-apps/calendar/quickstart/python) getting started is made much easier. Almost all prerequisites are in the standard python library, except for pandas and numpy.  Both can be installed via pip. 

pip install pandas

pip install numpy

The SQLite table used alongside the scripts is detailed below:

CREATE TABLE Chat (
  PersonId1 INTEGER,
  PersonId2 INTEGER,
  ChatTime DATETIME,
  primary key (PersonId1, PersonId2));
CREATE TABLE Person (
  Id INTEGER primary key,
  Name VARCHAR(100),
  Email VARCHAR(255),
  DepartmentID INTEGER, Include int);
CREATE TABLE [Department] (
[ID] INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT,
[Name] VARCHAR(100)  UNIQUE NOT NULL

Running
 ------------
This is executed from coffeechats.py, where the user will be prompted for a monday in the future. 

License
 ------------
This project is licensed under the MIT License

Acknowledgments
 ------------

Thanks to Jordan for the go-ahead, Maheen for identifying a problem, and Timna for letting me run wild with this one. 

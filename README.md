# bbb_rooms_insertion
Easy script to create BigBlueButton rooms from CSV file

# Prerequesites
- [python-wordpress-xmlrpc](https://python-wordpress-xmlrpc.readthedocs.io/en/latest/index.html) package

- [Wordpress BigBlueButton plugin](https://github.com/albertosgz/Wordpress_BigBlueButton_plugin) plugin

## Example
```
./create_meetings.py --csv_file accounts.csv --category_name Luminosa --site_url http://foo.bar.com/xmlrpc.php --site_user admin --site_password admin --sql_host foo.bar.com --sql_user pantheon --sql_password abcd --sql_db pantheon --sql_port 18162 -v --column_rec_pw 5
```

And the CSV files looks like:
```
Conference Rooms,Bridge Numbers,Moderator PW,Participate PW,Recordings User Name,Recordings PW
,,,,,
Canada,1111,foo!,pa,u1,focbar!
Toronto,2222,bar!,pa,u2,recbar!
```

Will create 2 posts for rooms Canada and Toronto, and its respectful recordings posts

**_Remember to write site URL finishing in /xmlrpc.php_**



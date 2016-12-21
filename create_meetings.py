#!/usr/bin/python

from wordpress_xmlrpc import Client, WordPressPost, WordPressTerm
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc.methods import taxonomies
import requests
import string
import random
import time
import argparse
import MySQLdb
import csv
import sys
import uuid

# Global Variables
VERBOSITY=False
WAIT_FOR_MODERATOR=1 # 1 fro true, 0 for false
RECORD_MEETING=1 # 1 for true, 0 for false

# Helpers functions
def id_generator(size=12, chars='abcdef' + string.digits):
	return str(uuid.uuid4())

def logs(message):
        if VERBOSITY:
            print message

def create_category(wp_client,new_category):
    # Look up for Conference rooms category
    catlist = wp_client.call(taxonomies.GetTerms('category',{"search":new_category.name}))
    #print (str(cat))
    if catlist:
        for item in catlist:
            logs("Found category "+item.name+" (id: "+item.id+")")
            return item # already exists the category, so return it
    else:
        # Creating new category for the Conference rooms
        new_category.id = wp.call(taxonomies.NewTerm(new_category))
        logs("Created category "+new_category.name+" (id: "+new_category.id+")")
        return new_category

# Let's parsing the arguments
parser = argparse.ArgumentParser(description="Script to load several BBB rooms to wordpress, creating automatically a page with all roooms and other page with ")
parser.add_argument("--csv_file",help="CSV file path to load", required=True)
parser.add_argument("--category_name",help="Category name for all rooms", required=True)
parser.add_argument("--first_title",help="Is the first line a title?", type=bool, default=True)
parser.add_argument("--column_conference_room_name",help="Position of the Conference room name column, starting by 0", type=int, default=0)
parser.add_argument("--column_bridge",help="Position of the Voice Bridge column, starting by 0", type=int, default=1)
parser.add_argument("--column_mod_pw",help="Position of the Moderator Password column, starting by 0", type=int, default=2)
parser.add_argument("--column_part_pw",help="Position of the Participant Password column, starting by 0", type=int, default=3)
parser.add_argument("--column_rec_pw",help="Position of the Recording Password column, starting by 0", type=int, default=4)
parser.add_argument("--site_url",help="URL of xmlrpc of the wordpress site to load into",required=True)
parser.add_argument("--site_user",help="Admin user",required=True)
parser.add_argument("--site_password",help="Admin password",required=True)
parser.add_argument("--sql_host",help="MySQL host", required=True)
parser.add_argument("--sql_port",help="MySQL port", type=int, default=3306)
parser.add_argument("--sql_user",help="MySQL user", required=True)
parser.add_argument("--sql_password",help="MySQL password", required=True)
parser.add_argument("--sql_db",help="MySQL Database schema", required=True)
parser.add_argument("-v","--verbose",help="Add verbosity logs", action="store_true")
args = parser.parse_args()

if args.verbose:
    VERBOSITY=True
    logs ("Enable Verbosity mode")

print
print 'Loading settings into '+args.site_url
print 'Connecting to MySQL with next info:'
print '  Host:     '+args.sql_host
print '  Port:     '+str(args.sql_port)
print '  User:     '+args.sql_user
print '  Password: '+args.sql_password
print '  Schema:   '+args.sql_db
print
print
print

# Stablishing connections
wp = Client('http://dev-luminosa.pantheonsite.io/xmlrpc.php', 'admin', 'admin')
db = MySQLdb.connect(host=args.sql_host,port=args.sql_port,user=args.sql_user,passwd=args.sql_password,db=args.sql_db)
cur = db.cursor() # you must create a Cursor object. It will let you execute all the queries you need

### Look up for Conference rooms category
##cat_confrooms = wp.call(taxonomies.GetTerms('category',{"search":'Conference rooms'}))
##print str(cat_confrooms)
###print str(cat_confrooms.id)
##
##for item in cat_confrooms:
##     print str(item)
##     print str(item.id)
##     print dir(item)

# Creating new category for the Conference rooms
conf_cat = WordPressTerm()
conf_cat.taxonomy = 'category'
conf_cat.description = 'Conference room category '+args.category_name+' created automatically by script at '+time.strftime("%c")
#conf_cat.parent = parent_cat.id
conf_cat.name = "Room "+args.category_name
conf_cat = create_category(wp,conf_cat)
print

# Creating new category for the Recordings
rec_cat = WordPressTerm()
rec_cat.taxonomy = 'category'
rec_cat.description = 'Recordings category '+args.category_name+' created automatically by script at '+time.strftime("%c")
#conf_cat.parent = parent_cat.id
rec_cat.name = "Recordings "+args.category_name
rec_cat = create_category (wp,rec_cat)
print

# Reading CSV file
print "Start to read the CSV file "+args.csv_file
print "--------------------------------------------------"
filename = args.csv_file
lines=0
with open(filename, 'rb') as f:
    reader = csv.reader(f)
    try:
        for row in reader:
            lines += 1

            logs ("Reading line "+str(lines)+": "+str(row))

            # It is a title?
            if args.first_title and lines == 1:
                print "  Skipping first line since is title:"
                print "    "+str(row)
                continue

            # It is a empty line?
            if row[args.column_conference_room_name]=="":
                print "  Skipping empty line "+str(lines)
                continue

            # Generating the Meeting ID, which it will be used for both post and BBB meeting
            meeting_id = id_generator()

            # Managing new line
            conf_room_name = row[args.column_conference_room_name]
            voicebridge = str(row[args.column_bridge])
            mod_pw = row[args.column_mod_pw]
            part_pw = row[args.column_part_pw]
            rec_pw = row[args.column_rec_pw]
            logs ("  Meeting ID:           "+meeting_id)
            logs ("  Conference room:      "+conf_room_name) 
            logs ("  VoiceBridge:          "+voicebridge) 
            logs ("  Moderator Password:   "+mod_pw) 
            logs ("  Participant Password: "+part_pw) 
            logs ("  Recording Password:   "+rec_pw) 
            
            # Creating BBB meeting into DB
#            cur.execute("INSERT INTO pantheon.wp_bigbluebutton (meetingID, meetingName, meetingVersion, attendeePW, moderatorPW, waitForModerator,recorded,voiceBridge,welcome)" \
#                        "VALUES ("+meeting_id+"," \
#                                 +conf_room_name+"," \
#                                 +str(time.time())+"," \
#                                 +part_pw+"," \
#                                 +mod_pw+"," \
#                                 +str(WAIT_FOR_MODERATOR)+"," \
#                                 +str(RECORD_MEETING)+"," \
#                                 +voicebridge+"," \
#                                 +"'Welcome to the Conference Room')")
            cur.executemany(
            """INSERT INTO pantheon.wp_bigbluebutton (meetingID, meetingName, meetingVersion, attendeePW, moderatorPW, waitForModerator,recorded,voiceBridge,welcome)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            [
            (meeting_id,
                                 conf_room_name,
                                 str(time.time()),
                                 part_pw,
                                 mod_pw,
                                 str(WAIT_FOR_MODERATOR),
                                 str(RECORD_MEETING),
                                 voicebridge,
                                 "Welcome to the Conference Room")
            ] )

            db.commit() # Make effect of the insertion into DB


            # Creating new category for this post
            post_cat = WordPressTerm()
            post_cat.taxonomy = 'category'
            post_cat.description = 'Conference room '+conf_room_name
            post_cat.parent = conf_cat.id
            post_cat.name = "Room "+args.category_name+' '+conf_room_name
            post_cat = create_category(wp,post_cat)
            post_rec_cat = WordPressTerm()
            post_rec_cat.taxonomy = 'category'
            post_rec_cat.description = 'Recordings room '+args.category_name+' '+conf_room_name
            post_rec_cat.parent = rec_cat.id
            post_rec_cat.name = "Recordings "+conf_room_name
            post_rec_cat = create_category(wp,post_rec_cat)

            # Creating the post according the new meeting room
            post = WordPressPost()
            post.title = 'Conference room - '+args.category_name+' - '+conf_room_name
            post.content = '[bigbluebutton token='+meeting_id+']'
            post.terms_names = {
               'post_tag': ['conference', args.category_name, conf_room_name],
               'category': [conf_cat.name,post_cat.name]
            }
            post.post_status = 'publish'
            wp.call(NewPost(post))

            # Creating the recording post
            post = WordPressPost()
            post.title = 'Recordings - '+args.category_name+' - '+conf_room_name
            post.content = '[[bigbluebutton_recordings token='+meeting_id+']'
            post.terms_names = {
               'post_tag': ['recordings', args.category_name, conf_room_name],
               'category': [rec_cat.name,post_rec_cat.name]
            }
            post.post_status = 'publish'
            post.password = rec_pw
            wp.call(NewPost(post))         

            print ("  Line "+str(lines)+" created ok")
            logs('')

    except csv.Error as e:
        sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))

db.close()

print ("Created "+str(lines)+" meetings rooms ok")
print

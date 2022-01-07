########################################
# flask/db setup
########################################

from flask import Flask, render_template, request, make_response, redirect, url_for
app = Flask(__name__)

# sqlite3 is built in python3, no need to pip3 install
import random
import markdown_compiler
import json
import bleach.sanitizer
from bleach.sanitizer import ALLOWED_ATTRIBUTES, Cleaner
import sqlite3
import requests
from deep_translator import GoogleTranslator
import copy
# process command line arguments
import argparse
parser = argparse.ArgumentParser(description='Create a database for the twitter project')
parser.add_argument('--db_file', default='twitter_clone.db')
args = parser.parse_args()

allowed_tags = bleach.sanitizer.ALLOWED_TAGS
allowed_tags.append('del')
allowed_tags.append('img')
allowed_tags.append('pre')
allowed_tags.append('code')
print(allowed_tags)
allowed_attributes = bleach.sanitizer.ALLOWED_ATTRIBUTES
allowed_attributes['img'] = ['src','alt']
print(allowed_attributes)
cleaner = Cleaner(tags = allowed_tags,attributes=allowed_attributes)

domains = ['.com','.org','.gov','.edu','.net']

interface = {'title':"Twitter clone for CS40!",
'home':'home',
'search':'search',
'logout':'logout',
'login':'login',
'create_message':'create message',
'create_user':'create user',
'message_added':'Message Added!',
'name_not_unique':'ERROR: username taken. User not created',
'password_different':'ERROR: Password does not match. User not created.',
'create_success':'User created!',
'username':'username',
'password':'password',
'confirm_password':'Confirm password',
'confirm':'confirm',
'no_match':'ERROR: username/password does not match',
'success' : 'Success!',
'if_not' : "If you don't have a user account, then",
'create_one': 'create one.',
'logout_success':'Logout Successful!',
'delete_user':'Delete User',
'message':'message',
'created_at':'Created at',
'edit_text':'Edit Text',
'delete_message':'Delete Message',
'previous':'previous',
'next':'next',
'user_deleted':'User Deleted',
'user_not_exist':'User does not exist',
'language':'language',
'edited' :'edited',
'languages': GoogleTranslator.get_supported_languages()
}
current_language='english'
language_list = GoogleTranslator.get_supported_languages()
language_list.remove('Filipino')
language_list.remove('Hebrew')
########################################
# helper functions
########################################

def validate_url(url):
    try:
        r = requests.get(url, timeout = 10)
        return True
    except (requests.exceptions.ConnectTimeout, requests.ConnectionError, requests.exceptions.InvalidSchema,requests.exceptions.MissingSchema):
        return False


def print_debug_info():
    '''
    Print information stored in GET/POST/Cookie variables to the terminal.
    '''
    #this code below uses request (singular) different from requests (plural) from before.

    # html form get
    # these values here are called "query arguments" args is an abreviation
    # they are the values after the ? in the url
    # they are for one webpage only
    print("request.args.get('username')=",request.args.get('username'))
    print("request.args.get('password')=",request.args.get('password'))
    # html form post
    # method = POST on the html form in the html
    print("request.form.get('username')=",request.form.get('username'))
    print("request.form.get('password')=",request.form.get('password'))
    # Cookies
    # not visible to the user directly (not in the url)
    # they persist on every webpage you visit
    print("request.cookies.get('username')=",request.cookies.get('username'))
    print("request.cookies.get('password')=",request.cookies.get('password'))


def is_valid_login(con, username, password):
    '''
    Return True if the given username/password is a valid login;
    otherwise return False.
    '''

    # query the database for users with the given username/password
    sql = """
    SELECT username,password
    FROM users
    WHERE username=?
      AND password=?;
    """
    print('is_valid_login: sql=',sql)
    cur = con.cursor()
    cur.execute(sql,[username,password])
    rows = cur.fetchall()

    # if the total number of rows returned is 0,
    # then no username/password combo was not found
    if len(list(rows))==0:
        return False

    # if the total number of rows returned is > 0,
    # then the username/password combo was found
    else:
        return True
def user_exists1(username):
    con = sqlite3.connect('twitter_clone.db')
    cur = con.cursor()
    cur.execute(f'''select count(*) from users where username = ?;''',[username])
    count1 = 0
    
    for row in cur.fetchall():
        count1 = row[0]
    return count1 != 0
def process_message(message):

    mth_message = markdown_compiler.compile_lines(message)
    word_list = mth_message.split("<a")
    for i,word in enumerate(word_list):
        word_list[i] = word.split("</a>")
    for i,word_group in enumerate(word_list):
        for j,word in enumerate(word_group):
            if i==0 or j>0:
                for domain in domains:
                    if word.find(domain)!=-1:
                        if validate_url(word):
                            word_group[j] = f"<a href = '{word}'>{word}</a>"
                if word.find('@') == 0:
                    possible_user = word[1:]
                    if user_exists1(possible_user):
                        word_group[j] = f"<a href = '/profile?profile_username={possible_user}'>{possible_user}</a>"
    for i,word_group in enumerate(word_list):
        word_list[i] = "</a>".join(word_group)
    dirty_message = "<a".join(word_list)
    clean_message = cleaner.clean(dirty_message)
    return str(clean_message)


def change_interface(languager):
    global interface
    global current_language

    con = sqlite3.connect('language.db')
    cur = con.cursor()
    keys = []
    sql = ''' select '''
    for key in interface.keys():
        if key != 'languages':
            sql += f''' ?, '''
            keys.append(key)
    keys.append('placeholder_for_list')
    for language in language_list:
        language1 = language.replace('(','')
        language1 = language1.replace(')','')
        language1 = language1.split()
        language1 = "_".join(language1)
        sql += f''' ?,'''
        keys.append(language1)
    sql = sql[:-1]
    temper = ''
    for key in keys:
        if key!= 'placeholder_for_list':
            temper+=key+', '
    temper = temper[:-2]
    sql = f''' select '''+temper+''' from languages where current_language = ?;'''
    
    
   
   
    con.set_trace_callback(print)
    
    cur.execute(sql,[languager])
    
    for row in cur.fetchall():
        
        for i,value in enumerate(row):
            if i < keys.index('placeholder_for_list'):
                interface[keys[i]] = value
                
            else:
                break
        temp_list = []
        for i, value in enumerate(row[keys.index('placeholder_for_list'):]):
            temp_list.append(value)
        interface['languages'] = temp_list


def message_selection():
    global interface
    global current_language
    global language_list
    selected_language = request.args.get('selected_language')
    current_path = request.full_path

    if selected_language != None:
        change_interface(selected_language)
        current_language = selected_language

    # this code will check whether we are logged in or not
    # check whether password/username in cookies is in the database
    con = sqlite3.connect(args.db_file)
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    is_logged_in = is_valid_login(con,username,password)
    message1= request.form.get('message1')
    message3 = request.form.get('message3')
    
    liked = request.form.get('liked')

    id3 = request.form.get('id3')
    parent_id = request.form.get('parent_id')
    id2 = request.form.get('id2')
    con = sqlite3.connect('twitter_clone.db')
    cur = con.cursor()
    
    cur.execute(f'''select image from users where username = ?''',[username])
    user_image = None
    for row in cur.fetchall():
        user_image = row[0]
    if message3 != None:
        
        con = sqlite3.connect('twitter_clone.db')
        cur = con.cursor()
        if parent_id != None:
            cur.execute(f'''insert into messages (username,message,liked,parent_id) values (?, ?, ?, ?);''',[username,message3," ",parent_id])
        else:
            cur.execute(f'''insert into messages (username,message,liked) values (?, ?, ?);''',[username,message3," "])
        con.commit()
    if liked != None:
        if username != None:
            if liked == "False":
                cur.execute(f'''select liked from messages where id = ? ;''',[id3])
                liked_string = ""
                for row in cur.fetchall():
                    liked_string += row[0]
                if liked_string!=None:
                    liked_string+=username+"54865855269648348847"
                else:
                    liked_string=username+"54865855269648348847"
                cur.execute(f'''update messages set liked = ? where id = ? ;''',[liked_string,id3])
                con.commit()
            elif liked == "True":
                cur.execute(f'''select liked from messages where id = ? ;''',[id3])
                liked_string = ""
                for row in cur.fetchall():
                    liked_string += row[0]
                
                liked_string = liked_string.replace(username+"54865855269648348847","")
                cur.execute(f'''update messages set liked = ? where id = ?; ''',[liked_string,id3])
                con.commit()

    if id2 != None:
        cur.execute(f'''delete from messages where id = ? ; ''',[id2])
        con.commit()
    if message1 != None:
        id1 = request.form.get('id1')
        print(id1)
        print(message1)
        current_message = None
        cur.execute(f''' select message from messages where id = ? ; ''',[id1])
        for row in cur.fetchall():
            current_message = row[0]
        if current_message != None and message1 != current_message:
            cur.execute(f'''update messages set edit = 'True', created_at = current_timestamp where id = ? ; ''',[id1])
        
        cur.execute(f'''update messages set message = ? where id = ? ; ''',[message1,id1])
        
        con.commit()

    cur.execute("select count(*) from messages;")
    count = 0
    for row in cur.fetchall():
        count = row[0]
    num_pages = count // 50
    num_pages = num_pages + 1
    current_page = 1
    messages = []
    

    selected_page = request.form.get('selected_page')

    if selected_page != None:
        current_page = selected_page
    offset = (int(current_page)-1) * 50 
    sql = f"""
    select username,message,created_at,id,edit,liked from messages where parent_id = ' ' or parent_id is null order by created_at DESC limit 50 offset ?;
    """
    cur.execute(sql,[offset])
    for row in cur.fetchall():
        temp_dict = {}
        temp_dict['username'] = row[0]
        temp_dict['message'] = process_message(row[1])
        temp_dict['created_at'] = row[2]
        temp_dict['id'] = row[3]
        temp_dict['edit'] = row[4]
        temp_dict['liked'] = row[5]
        messages.append(copy.deepcopy(temp_dict))


    sql = """
    select username,age,image from users;
    """
    cur.execute(sql)

    
    for row in cur.fetchall():
        for dict in messages:
            if dict['username'] == row[0]:
                dict['age'] = row[1]
                dict['image'] = row[2]
    
    baby_messages = {}
    for message4 in messages:
        sql = f"""
    select username,message,created_at,id,edit,liked,parent_id from messages where parent_id = ? order by created_at ASC;
    """
        cur.execute(sql,[message4['id']])
        temp_message_list = []
        temp_dict2 = {}

        for row in cur.fetchall():
            temp_dict2 = {}
            temp_dict2['username'] = row[0]
            temp_dict2['message'] = process_message(row[1])
            temp_dict2['created_at'] = row[2]
            temp_dict2['id'] = row[3]
            temp_dict2['edit'] = row[4]
            temp_dict2['liked'] = row[5]
            temp_dict2['parent_id'] = row[6]
            temp_message_list.append(copy.deepcopy(temp_dict2))
        baby_messages[f'{message4["id"]}'] = copy.deepcopy(temp_message_list)
        sql = """
        select username,age,image from users;
        """
        cur.execute(sql)

        
        for row in cur.fetchall():
            for dict in baby_messages[f'{message4["id"]}']:
                if dict['username'] == row[0]:
                    dict['age'] = row[1]
                    dict['image'] = row[2]
    return baby_messages,current_path,is_logged_in,messages,username,current_page,current_path,num_pages,user_image
########################################
# custom routes
########################################

@app.route('/',methods = ['GET','POST'])     
def root():
    print_debug_info()
    
    baby_messages,current_path,is_logged_in,messages,username,current_page,current_path,num_pages,user_image = message_selection()
    

    con = sqlite3.connect('twitter_clone.db')
    cur = con.cursor()

    # sql = '''select username as usernamez from users where usernamez in (select username from (select username, sum(length(replace(liked,' ',''))) as score from messages group by username order by score desc limit 10) where score != 0 ); 
    # '''
    sql = '''select username, sum(length(replace(liked,' ',''))) as score from messages group by username order by score desc limit 10 '''
    cur.execute(sql)
    top_ten= []
    for row in cur.fetchall():
            top_ten.append([row[0],row[1]])
    
    delete_needed = []
    for user in top_ten:
        if user[1] == 0:
            delete_needed.append(user)
    for user in delete_needed:
        top_ten.remove(user)
    for i,user in enumerate(top_ten):
        user[1] = user[1]//25
    sql = '''select image from users where username = ?;'''
    for user in top_ten:
        cur.execute(sql,[user[0]])
        for row in cur.fetchall():
            user.append(row[0])
    stats = []
    num_users = 0
    num_messages = 0
    sql = '''select count(*) from users;'''
    cur.execute(sql)
    for row in cur.fetchall():
        stats.append('Total users: '+str(row[0]))
        num_users = row[0]
    sql = '''select count(*) from messages;'''
    cur.execute(sql)
    for row in cur.fetchall():
        stats.append('Total messages: '+str(row[0]))
        num_messages = row[0]
    sql = '''select sum(length(replace(liked,' ',''))) from messages;'''
    cur.execute(sql)
    for row in cur.fetchall():
        stats.append('Total Likes: '+str(row[0]//25))
    sql = '''select count(*) from messages where parent_id = ' ' or parent_id is null;'''
    cur.execute(sql)
    for row in cur.fetchall():
        stats.append('Total Top Level Posts: '+str(row[0]))
    stats.append('Total Baby Comments: '+str(num_messages-row[0]))
    sql = '''select sum(length(message)) from messages;'''
    cur.execute(sql)
    for row in cur.fetchall():
        stats.append('Average letter per user: '+str(row[0]//num_users))
        stats.append('Average letter per message: '+str(row[0]//num_messages))
    sql = '''select created_at from messages order by created_at desc limit 1;'''
    cur.execute(sql)
    for row in cur.fetchall():
        stats.append('Newest Post: '+str(row[0]))
    sql = '''select created_at from messages order by created_at asc limit 1;'''
    cur.execute(sql)
    for row in cur.fetchall():
        stats.append('Oldest Post: '+str(row[0]))
    sql = '''select username from users;'''
    cur.execute(sql)
    names = []
    for row in cur.fetchall():
        names.append(row[0])
    
    highest_name = None
    highest = 0
    for name in names:
        sql = '''select count(*) from messages where liked like ?;'''
        cur.execute(sql,['%'+name+'%'])
        for row in cur.fetchall():
            if row[0] > highest:
                highest = row[0]
                highest_name = name
    stats.append("Easy Liker: "+highest_name+' with '+str(highest)+' Likes')
    
    with open('messages.json','w') as f:
        temper = copy.deepcopy(messages)
        temper.append(baby_messages)
        json.dump(temper,f)
    return render_template('facebook2.html',stats = stats,top_ten = top_ten, user_image = user_image,baby_messages = baby_messages, language_list = language_list, language = current_language,current_path = current_path, interface=interface, is_logged_in = is_logged_in,messages = messages,username = username,current_page = current_page,num_pages = num_pages)


@app.route('/login', methods =['GET','POST'])
def login():
    print_debug_info()

    global interface
    global current_language
    global language_list
    selected_language = request.args.get('selected_language')
    current_path = request.full_path

    if selected_language != None:
        change_interface(selected_language)
        current_language = selected_language
    con = sqlite3.connect(args.db_file)
    form_username = request.form.get('username')
    form_password = request.form.get('password')

    has_used_form = form_username != None
    unsuccessful_login = False
    successful_login = False
    if has_used_form:
        if is_valid_login(con,form_username,form_password):
            successful_login = True
            result = make_response(render_template('facebook_login.html',language_list = language_list, language = current_language,current_path = current_path,interface=interface,successful_login = successful_login, is_valid_login = True))
            result.set_cookie('username',form_username)
            result.set_cookie('password',form_password)
            return result
        else:
            unsuccessful_login = True
            return render_template('facebook_login.html',language_list = language_list, language = current_language,current_path = current_path,interface=interface,unsuccessful_login = unsuccessful_login)
    else:
        return render_template('facebook_login.html',interface=interface,language_list = language_list, language = current_language,current_path = current_path,)
    

@app.route('/logout')     
def logout():
    global interface
    global current_language
    global language_list

    con = sqlite3.connect(args.db_file)
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    is_logged_in = is_valid_login(con,username,password)

    selected_language = request.args.get('selected_language')
    current_path = request.full_path

    if selected_language != None:
        change_interface(selected_language)
        current_language = selected_language
    print_debug_info()
    result = make_response(render_template('facebook_logout.html',is_logged_in = False,language_list = language_list, language = current_language,current_path = current_path,interface=interface,))
    result.set_cookie('username','',expires = 0)
    result.set_cookie('password','',expires = 0)
    return result
    

@app.route('/create_message',methods = ['GET','POST'])     
def create_message():
    print_debug_info()
    global interface
    global current_language
    global language_list

    con = sqlite3.connect(args.db_file)
    cur = con.cursor()
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    is_logged_in = is_valid_login(con,username,password)

    selected_language = request.args.get('selected_language')
    current_path = request.full_path
    cur.execute(f'''select image from users where username = ?''',[username])
    user_image = None
    for row in cur.fetchall():
        user_image = row[0]
    if selected_language != None:
        change_interface(selected_language)
        current_language = selected_language
    

    
    username = request.cookies.get('username')
    message = request.form.get('message')
    con = sqlite3.connect('twitter_clone.db')
    cur = con.cursor()

    # sql = '''select username as usernamez from users where usernamez in (select username from (select username, sum(length(replace(liked,' ',''))) as score from messages group by username order by score desc limit 10) where score != 0 ); 
    # '''
    sql = '''select username, sum(length(replace(liked,' ',''))) as score from messages group by username order by score desc limit 10 '''
    cur.execute(sql)
    top_ten= []
    for row in cur.fetchall():
            top_ten.append([row[0],row[1]])
    
    delete_needed = []
    for user in top_ten:
        if user[1] == 0:
            delete_needed.append(user)
    for user in delete_needed:
        top_ten.remove(user)
    for i,user in enumerate(top_ten):
        user[1] = user[1]//25
    sql = '''select image from users where username = ?;'''
    for user in top_ten:
        cur.execute(sql,[user[0]])
        for row in cur.fetchall():
            user.append(row[0])
    stats = []
    num_users = 0
    num_messages = 0
    sql = '''select count(*) from users;'''
    cur.execute(sql)
    for row in cur.fetchall():
        stats.append('Total users: '+str(row[0]))
        num_users = row[0]
    sql = '''select count(*) from messages;'''
    cur.execute(sql)
    for row in cur.fetchall():
        stats.append('Total messages: '+str(row[0]))
        num_messages = row[0]
    sql = '''select sum(length(replace(liked,' ',''))) from messages;'''
    cur.execute(sql)
    for row in cur.fetchall():
        stats.append('Total Likes: '+str(row[0]//25))
    sql = '''select count(*) from messages where parent_id = ' ' or parent_id is null;'''
    cur.execute(sql)
    for row in cur.fetchall():
        stats.append('Total Top Level Posts: '+str(row[0]))
    stats.append('Total Baby Comments: '+str(num_messages-row[0]))
    sql = '''select sum(length(message)) from messages;'''
    cur.execute(sql)
    for row in cur.fetchall():
        stats.append('Average letter per user: '+str(row[0]//num_users))
        stats.append('Average letter per message: '+str(row[0]//num_messages))
    sql = '''select created_at from messages order by created_at desc limit 1;'''
    cur.execute(sql)
    for row in cur.fetchall():
        stats.append('Newest Post: '+str(row[0]))
    sql = '''select created_at from messages order by created_at asc limit 1;'''
    cur.execute(sql)
    for row in cur.fetchall():
        stats.append('Oldest Post: '+str(row[0]))
    sql = '''select username from users;'''
    cur.execute(sql)
    names = []
    for row in cur.fetchall():
        names.append(row[0])
    
    highest_name = None
    highest = 0
    for name in names:
        sql = '''select count(*) from messages where liked like ?;'''
        cur.execute(sql,['%'+name+'%'])
        for row in cur.fetchall():
            if row[0] > highest:
                highest = row[0]
                highest_name = name
    stats.append("Easy Liker: "+highest_name+' with '+str(highest)+' Likes')
    
    if message != None:
        
        con = sqlite3.connect('twitter_clone.db')
        cur = con.cursor()
        
        cur.execute(f'''insert into messages (username,message,liked) values (?, ?, ?);''',[username,message," "])
        con.commit()
        return render_template('facebook_create_message.html',stats = stats, top_ten=top_ten,user_image = user_image,is_logged_in = is_logged_in,language_list = language_list, language = current_language,current_path = current_path,interface=interface,message_added = True)
    return render_template('facebook_create_message.html',stats = stats, top_ten=top_ten,user_image = user_image,is_logged_in = is_logged_in,language_list = language_list, language = current_language,current_path = current_path,interface=interface,)
    

@app.route('/create_user',methods = ['GET','POST'])     
def create_user():
    print_debug_info()
    global interface
    global current_language
    global language_list

    con = sqlite3.connect(args.db_file)
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    is_logged_in = is_valid_login(con,username,password)
    selected_language = request.args.get('selected_language')
    current_path = request.full_path

    if selected_language != None:
        change_interface(selected_language)
        current_language = selected_language
    username = request.form.get('username')
    password = request.form.get('password')
    password2 = request.form.get('password2')
    print(password2)
    username_not_unique = True
    password_not_same = True
    if username != None:
        con = sqlite3.connect('twitter_clone.db')
        cur = con.cursor()
        cur.execute(f'''select username from users where username = ?;
        ''',[username])
        
        if len(cur.fetchall()) == 0:
            username_not_unique = False
        else:
            username_not_unique = True
            return render_template('facebook_create_user.html', language_list = language_list, language = current_language,current_path = current_path,interface=interface,username_unique=  username_not_unique)
            
        if password == password2:
            password_not_same = False
            
        else:
            password_not_same = True
            return render_template('facebook_create_user.html',language_list = language_list, language = current_language,current_path = current_path,interface=interface, password_same = password_not_same)
        
        if not password_not_same and not username_not_unique:
            random1 = random.randint(0,100000)
            cur.execute(f'''insert into users (username,password,image) values (?, ?,?);''',[username,password,f"https://robohash.org/{random1}?set=any"])
            con.commit()
            baby_messages,current_path,is_logged_in,messages,username2,current_page,current_path,num_pages,user_image = message_selection()
            result = make_response(redirect('/'))
            result.set_cookie('username',username)
            result.set_cookie('password',password)
            return result
    return render_template('facebook_create_user.html',interface = interface, is_logged_in = is_logged_in,language_list = language_list, language = current_language,current_path = current_path)
    

@app.route('/profile',methods = ['GET','POST'])     
def profile():
    print_debug_info()
    global interface
    global current_language
    global language_list
    selected_language = request.args.get('selected_language')
    current_path = request.full_path

    if selected_language != None:
        change_interface(selected_language)
        current_language = selected_language
    # this code will check whether we are logged in or not
    # check whether password/username in cookies is in the database
    con = sqlite3.connect(args.db_file)
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    
    deleted_user = request.form.get('deleted_user')
    profile_username = request.args.get('profile_username')
    description = request.form.get('description')
    user_match = False
    if profile_username == username:
        user_match = True

    message1= request.form.get('message1')
    is_logged_in = is_valid_login(con,username,password)
    id2 = request.form.get('id2')

    liked = request.form.get('liked')
    message3 = request.form.get('message3')
    id3 = request.form.get('id3')
    parent_id = request.form.get('parent_id')
    con = sqlite3.connect('twitter_clone.db')
    cur = con.cursor()
    
    user_exists = user_exists1(profile_username)
    delete_success = None
    
    con = sqlite3.connect('twitter_clone.db')
    cur = con.cursor()

    # sql = '''select username as usernamez from users where usernamez in (select username from (select username, sum(length(replace(liked,' ',''))) as score from messages group by username order by score desc limit 10) where score != 0 ); 
    # '''
    sql = '''select username, sum(length(replace(liked,' ',''))) as score from messages group by username order by score desc limit 10 '''
    cur.execute(sql)
    top_ten= []
    for row in cur.fetchall():
            top_ten.append([row[0],row[1]])
    
    delete_needed = []
    for user in top_ten:
        if user[1] == 0:
            delete_needed.append(user)
    for user in delete_needed:
        top_ten.remove(user)
    for i,user in enumerate(top_ten):
        user[1] = user[1]//25
    sql = '''select image from users where username = ?;'''
    for user in top_ten:
        cur.execute(sql,[user[0]])
        for row in cur.fetchall():
            user.append(row[0])
    stats = []
    num_users = 0
    num_messages = 0
    sql = '''select count(*) from users;'''
    cur.execute(sql)
    for row in cur.fetchall():
        stats.append('Total users: '+str(row[0]))
        num_users = row[0]
    sql = '''select count(*) from messages;'''
    cur.execute(sql)
    for row in cur.fetchall():
        stats.append('Total messages: '+str(row[0]))
        num_messages = row[0]
    sql = '''select sum(length(replace(liked,' ',''))) from messages;'''
    cur.execute(sql)
    for row in cur.fetchall():
        stats.append('Total Likes: '+str(row[0]//25))
    sql = '''select count(*) from messages where parent_id = ' ' or parent_id is null;'''
    cur.execute(sql)
    for row in cur.fetchall():
        stats.append('Total Top Level Posts: '+str(row[0]))
    stats.append('Total Baby Comments: '+str(num_messages-row[0]))
    sql = '''select sum(length(message)) from messages;'''
    cur.execute(sql)
    for row in cur.fetchall():
        stats.append('Average letter per user: '+str(row[0]//num_users))
        stats.append('Average letter per message: '+str(row[0]//num_messages))
    sql = '''select created_at from messages order by created_at desc limit 1;'''
    cur.execute(sql)
    for row in cur.fetchall():
        stats.append('Newest Post: '+str(row[0]))
    sql = '''select created_at from messages order by created_at asc limit 1;'''
    cur.execute(sql)
    for row in cur.fetchall():
        stats.append('Oldest Post: '+str(row[0]))
    sql = '''select username from users;'''
    cur.execute(sql)
    names = []
    for row in cur.fetchall():
        names.append(row[0])
    
    highest_name = None
    highest = 0
    for name in names:
        sql = '''select count(*) from messages where liked like ?;'''
        cur.execute(sql,['%'+name+'%'])
        for row in cur.fetchall():
            if row[0] > highest:
                highest = row[0]
                highest_name = name
    stats.append("Easy Liker: "+highest_name+' with '+str(highest)+' Likes')
    
    if user_exists:
        cur.execute(f'''select image from users where username = ?''',[username])
        user_image = None
        for row in cur.fetchall():
            user_image = row[0]
        if message3 != None:
            con = sqlite3.connect('twitter_clone.db')
            cur = con.cursor()
            if parent_id != None:
                cur.execute(f'''insert into messages (username,message,liked,parent_id) values (?, ?, ?, ?);''',[username,message3," ",parent_id])
            else:
                cur.execute(f'''insert into messages (username,message,liked) values (?, ?, ?);''',[username,message3," "])
            con.commit()
        if deleted_user != None:
            cur.execute(f'''delete from users where username = ?;''',[deleted_user])
            cur.execute(f'''delete from messages where username = ?;''',[deleted_user])
            
            con.commit()
            delete_success = True
            user_exists = False

        if description != None:
            
            cur.execute(f'''update users set description = ? where username = ?;''',[description,username])
            con.commit()
        if liked != None:
            if username != None:
                if liked == "False":
                    cur.execute(f'''select liked from messages where id = ? ;''',[id3])
                    liked_string = ""
                    for row in cur.fetchall():
                        liked_string += row[0]
                    if liked_string!=None:
                        liked_string+=username+"54865855269648348847"
                    else:
                        liked_string=username+"54865855269648348847"
                    cur.execute(f'''update messages set liked = ? where id = ? ;''',[liked_string,id3])
                    con.commit()
                elif liked == "True":
                    cur.execute(f'''select liked from messages where id = ? ;''',[id3])
                    liked_string = ""
                    for row in cur.fetchall():
                        liked_string += row[0]
                    
                    liked_string = liked_string.replace(username+"54865855269648348847","")
                    cur.execute(f'''update messages set liked = ? where id = ?; ''',[liked_string,id3])
                    con.commit()
        if id2 != None:
            cur.execute(f'''delete from messages where id = ? ; ''',[id2])
            con.commit()
        if message1 != None:
            id1 = request.form.get('id1')
            print(id1)
            
            cur.execute(f'''update messages set message = ? where id = ? ; ''',[message1,id1])
            cur.execute(f'''update messages set edit = 'True' where id = ? ; ''',[id1])
            con.commit()

        cur.execute(f"select count(*) from messages where (parent_id = ' ' or parent_id is null) and username = ?;",[profile_username])
        count = 0
        for row in cur.fetchall():
            count = row[0]
        num_pages = count // 50
        num_pages = num_pages + 1
        current_page = 1
        messages = []
        

        selected_page = request.form.get('selected_page')

        if selected_page != None:
            current_page = selected_page
        offset = (int(current_page)-1) * 50 
        sql = f"""
        select username,message,created_at,id,edit,liked from messages where (parent_id = ' ' or parent_id is null) and username = ? order by created_at DESC limit 50 offset ?;
        """
        cur.execute(sql,[profile_username,offset])
        for row in cur.fetchall():
            temp_dict = {}
            temp_dict['username'] = row[0]
            temp_dict['message'] = process_message(row[1])
            temp_dict['created_at'] = row[2]
            temp_dict['id'] = row[3]
            temp_dict['edit'] = row[4]
            temp_dict['liked'] = row[5]
            messages.append(copy.deepcopy(temp_dict))


        sql = """
        select username,age,description,image from users;
        """
        cur.execute(sql)

        
        for row in cur.fetchall():
            for dict in messages:
                if dict['username'] == row[0]:
                    dict['age'] = row[1]
                    if row[2] != None:
                        description = process_message(row[2])
                    dict['image'] = row[3]
        baby_messages = {}
        for message4 in messages:
            sql = f"""
        select username,message,created_at,id,edit,liked,parent_id from messages where parent_id = ? order by created_at ASC;
        """
            cur.execute(sql,[message4['id']])
            temp_message_list = []
            temp_dict2 = {}

            for row in cur.fetchall():
                temp_dict2 = {}
                temp_dict2['username'] = row[0]
                temp_dict2['message'] = process_message(row[1])
                temp_dict2['created_at'] = row[2]
                temp_dict2['id'] = row[3]
                temp_dict2['edit'] = row[4]
                temp_dict2['liked'] = row[5]
                temp_dict2['parent_id'] = row[6]
                temp_message_list.append(copy.deepcopy(temp_dict2))
            baby_messages[f'{message4["id"]}'] = copy.deepcopy(temp_message_list)
            sql = """
            select username,age,image from users;
            """
            cur.execute(sql)

            
            for row in cur.fetchall():
                for dict in baby_messages[f'{message4["id"]}']:
                    if dict['username'] == row[0]:
                        dict['age'] = row[1]
                        dict['image'] = row[2]
        
            print(num_pages)
        return render_template('facebook_profile.html', stats = stats, top_ten=top_ten,user_image = user_image,baby_messages = baby_messages, language_list = language_list, language = current_language,current_path = current_path,interface=interface,is_logged_in = is_logged_in,messages = messages,username = username,current_page = current_page,num_pages = num_pages, user_match = user_match, description = description,profile_username=profile_username,user_exists = user_exists,delete_success = delete_success)
    else:
        return render_template('facebook_profile.html',stats = stats, top_ten=top_ten,language_list = language_list, language = current_language,current_path = current_path,interface=interface,delete_success = delete_success, user_exists = user_exists)


@app.route('/tester')
def deler():
    text = process_message("~~hihihihihi~~")
    return render_template('del_test.html',text=text)

@app.route('/search',methods = ['GET','POST'])     
def search():
    print_debug_info()
    global interface
    global current_language
    global language_list
    selected_language = request.args.get('selected_language')
    current_path = request.full_path

    if selected_language != None:
        change_interface(selected_language)
        current_language = selected_language
    # this code will check whether we are logged in or not
    # check whether password/username in cookies is in the database
    con = sqlite3.connect(args.db_file)
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    message1= request.form.get('message1')
    liked = request.form.get('liked')
    message3 = request.form.get('message3')
    id3 = request.form.get('id3')
    parent_id = request.form.get('parent_id')
    id2 = request.form.get('id2')
    search_term = request.args.get('search_term')
    is_logged_in = is_valid_login(con,username,password)
    id2 = request.form.get('id2')
    con = sqlite3.connect('twitter_clone.db')
    cur = con.cursor()
    cur.execute(f'''select image from users where username = ?''',[username])
    user_image = None
    for row in cur.fetchall():
        user_image = row[0]
    messages = []
    con = sqlite3.connect('twitter_clone.db')
    cur = con.cursor()

    # sql = '''select username as usernamez from users where usernamez in (select username from (select username, sum(length(replace(liked,' ',''))) as score from messages group by username order by score desc limit 10) where score != 0 ); 
    # '''
    sql = '''select username, sum(length(replace(liked,' ',''))) as score from messages group by username order by score desc limit 10 '''
    cur.execute(sql)
    top_ten= []
    for row in cur.fetchall():
            top_ten.append([row[0],row[1]])
    
    delete_needed = []
    for user in top_ten:
        if user[1] == 0:
            delete_needed.append(user)
    for user in delete_needed:
        top_ten.remove(user)
    for i,user in enumerate(top_ten):
        user[1] = user[1]//25
    sql = '''select image from users where username = ?;'''
    for user in top_ten:
        cur.execute(sql,[user[0]])
        for row in cur.fetchall():
            user.append(row[0])
    stats = []
    num_users = 0
    num_messages = 0
    sql = '''select count(*) from users;'''
    cur.execute(sql)
    for row in cur.fetchall():
        stats.append('Total users: '+str(row[0]))
        num_users = row[0]
    sql = '''select count(*) from messages;'''
    cur.execute(sql)
    for row in cur.fetchall():
        stats.append('Total messages: '+str(row[0]))
        num_messages = row[0]
    sql = '''select sum(length(replace(liked,' ',''))) from messages;'''
    cur.execute(sql)
    for row in cur.fetchall():
        stats.append('Total Likes: '+str(row[0]//25))
    sql = '''select count(*) from messages where parent_id = ' ' or parent_id is null;'''
    cur.execute(sql)
    for row in cur.fetchall():
        stats.append('Total Top Level Posts: '+str(row[0]))
    stats.append('Total Baby Comments: '+str(num_messages-row[0]))
    sql = '''select sum(length(message)) from messages;'''
    cur.execute(sql)
    for row in cur.fetchall():
        stats.append('Average letter per user: '+str(row[0]//num_users))
        stats.append('Average letter per message: '+str(row[0]//num_messages))
    sql = '''select created_at from messages order by created_at desc limit 1;'''
    cur.execute(sql)
    for row in cur.fetchall():
        stats.append('Newest Post: '+str(row[0]))
    sql = '''select created_at from messages order by created_at asc limit 1;'''
    cur.execute(sql)
    for row in cur.fetchall():
        stats.append('Oldest Post: '+str(row[0]))
    sql = '''select username from users;'''
    cur.execute(sql)
    names = []
    for row in cur.fetchall():
        names.append(row[0])
    
    highest_name = None
    highest = 0
    for name in names:
        sql = '''select count(*) from messages where liked like ?;'''
        cur.execute(sql,['%'+name+'%'])
        for row in cur.fetchall():
            if row[0] > highest:
                highest = row[0]
                highest_name = name
    stats.append("Easy Liker: "+highest_name+' with '+str(highest)+' Likes')
    
    if message3 != None:
        
        con = sqlite3.connect('twitter_clone.db')
        cur = con.cursor()
        if parent_id != None:
            cur.execute(f'''insert into messages (username,message,liked,parent_id) values (?, ?, ?, ?);''',[username,message3," ",parent_id])
        else:
            cur.execute(f'''insert into messages (username,message,liked) values (?, ?, ?);''',[username,message3," "])
        con.commit()
    if liked != None:
        if username != None:
            if liked == "False":
                cur.execute(f'''select liked from messages where id = ? ;''',[id3])
                liked_string = ""
                for row in cur.fetchall():
                    liked_string += row[0]
                if liked_string!=None:
                    liked_string+=username+"54865855269648348847"
                else:
                    liked_string=username+"54865855269648348847"
                cur.execute(f'''update messages set liked = ? where id = ? ;''',[liked_string,id3])
                con.commit()
            elif liked == "True":
                cur.execute(f'''select liked from messages where id = ? ;''',[id3])
                liked_string = ""
                for row in cur.fetchall():
                    liked_string += row[0]
                
                liked_string = liked_string.replace(username+"54865855269648348847","")
                cur.execute(f'''update messages set liked = ? where id = ?; ''',[liked_string,id3])
                con.commit()
    if id2 != None:
        cur.execute(f'''delete from messages where id = ?; ''',[id2])
        con.commit()
    if message1 != None:
        id1 = request.form.get('id1')
        print(id1)
        print(message1)
        cur.execute(f'''update messages set message = ? where id = ? ; ''',[message1,id1])
        cur.execute(f'''update messages set edit = 'True' where id = ? ; ''',[id1])
        con.commit()

    
    current_page = 1
    
    

    selected_page = request.form.get('selected_page')

    if selected_page != None:
        current_page = selected_page
    offset = (int(current_page)-1) * 50 
    if search_term != None:

        
        cur.execute(f"select count(*) from messages where (message like '%'||?||'%' or username like '%'||?||'%') and (parent_id = ' ' or parent_id is null);",[search_term,search_term])
        count = 0
        for row in cur.fetchall():
            count = row[0]
        num_pages = count // 50
        num_pages = num_pages + 1
        sql = f"""
        select username,message,created_at,id,edit,liked from messages where (message like '%'||?||'%' or username like '%'||?||'%') and (parent_id = ' ' or parent_id is null) order by created_at DESC limit 50 offset ?;
        """
        cur.execute(sql,[search_term,search_term,offset])
        for row in cur.fetchall():
            temp_dict = {}
            temp_dict['username'] = row[0]
            temp_dict['message'] = process_message(row[1])
            temp_dict['created_at'] = row[2]
            temp_dict['id'] = row[3]
            temp_dict['edit'] = row[4]
            temp_dict['liked'] = row[5]
            messages.append(copy.deepcopy(temp_dict))


        sql = """
        select username,age,image from users;
        """
        cur.execute(sql)

        
        for row in cur.fetchall():
            for dict in messages:
                if dict['username'] == row[0]:
                    dict['age'] = row[1]
                    dict['image'] = row[2]
        baby_messages = {}
        for message4 in messages:
            sql = f"""
        select username,message,created_at,id,edit,liked,parent_id from messages where parent_id = ? order by created_at ASC;
        """
            cur.execute(sql,[message4['id']])
            temp_message_list = []
            temp_dict2 = {}

            for row in cur.fetchall():
                temp_dict2 = {}
                temp_dict2['username'] = row[0]
                temp_dict2['message'] = process_message(row[1])
                temp_dict2['created_at'] = row[2]
                temp_dict2['id'] = row[3]
                temp_dict2['edit'] = row[4]
                temp_dict2['liked'] = row[5]
                temp_dict2['parent_id'] = row[6]
                temp_message_list.append(copy.deepcopy(temp_dict2))
            baby_messages[f'{message4["id"]}'] = copy.deepcopy(temp_message_list)
            sql = """
            select username,age,image from users;
            """
            cur.execute(sql)

            
            for row in cur.fetchall():
                for dict in baby_messages[f'{message4["id"]}']:
                    if dict['username'] == row[0]:
                        dict['age'] = row[1]
                        dict['image'] = row[2]
        return render_template('facebook_search.html',stats = stats, top_ten=top_ten,user_image = user_image, baby_messages=baby_messages, language_list = language_list, language = current_language,current_path = current_path,interface=interface, is_logged_in = is_logged_in,messages = messages,username = username,current_page = current_page,num_pages = num_pages, search_term = search_term)
    return render_template('facebook_search.html',stats = stats, top_ten=top_ten,user_image = user_image,language_list = language_list, language = current_language,current_path = current_path,interface=interface, is_logged_in = is_logged_in,messages = messages,username = username, search_term = search_term)









########################################
# boilerplate
########################################

if __name__=='__main__':
    app.run()

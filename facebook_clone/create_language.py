from deep_translator import GoogleTranslator
import sqlite3
import time
import copy

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
'if_not' : "If you do not have a user account, then",
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
'edited':'edited',
'current_language':'english'
}
language_list = GoogleTranslator.get_supported_languages()
language_list.remove('Filipino')
language_list.remove('Hebrew')



# sql = '''
#     CREATE TABLE languages (
#     '''
# for key in interface.keys():
#     sql += f''' {key} TEXT NOT NULL, '''
# for language in language_list:
#     language1 = language.replace('(','')
#     language1 = language1.replace(')','')
#     language1 = language1.split()
#     language1 = "_".join(language1)
#     sql += f''' {language1} TEXT NOT NULL,'''
# sql = sql[:-1]
# sql += '''
# );'''
# print(sql)
con = sqlite3.connect('language.db')
cur = con.cursor()


temp_interface = {}


current_language = 'zulu'


# try:
#     for language in language_list[language_list.index(current_language):]:
#         current_language = language
#         print(language)
#         if language == 'english':
#             temp_interface = copy.deepcopy(interface)
#             for language1 in language_list:
#                 language2 = language1.replace('(','')
#                 language2 = language2.replace(')','')
#                 language2 = language2.split()
#                 language2 = "_".join(language2)
#                 temp_interface[language2] = language2
#         else:
#             for key,value in interface.items():
#                 temp_interface[key] = GoogleTranslator(source='english', target=language).translate(value)
#             for language1 in language_list:
#                 language2 = language1.replace('(','')
#                 language2 = language2.replace(')','')
#                 language2 = language2.split()
#                 language2 = "_".join(language2)
#                 temp_interface[language2] = GoogleTranslator(source='english', target=language).translate(language2)
#             temp_interface['current_language'] = current_language


#         sql = '''
#         insert into languages (
#         '''
#         temp1 = ''''''
#         temp2 = ''''''
#         for key,value in temp_interface.items():
#             fixed = value.replace('\'','\'\'')
#             temp1+= f'''{key},'''
#             temp2 += f'''\'{fixed}\','''
#         sql+=temp1[:-1]
#         sql+=''') values ('''
#         sql+=temp2[:-1]
#         sql+=''');'''
#         print(sql)
#         cur.execute(sql)
#         con.commit()



try:
    for language in language_list:
        if language != 'english':
            edited = GoogleTranslator(source='english', target=language).translate(interface['edited'])
            language1 = language.replace('\'','\'\'')
            edited = edited.replace('\'','\'\'')
            sql = f'''update languages set edited = '{edited}'  where current_language = '{language1}' '''
            print(sql)
            cur.execute(sql)
            con.commit()


except Exception as err:
    print(err)
    time.sleep(600)
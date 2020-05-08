#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import subprocess
# import datetime
import pymysql
# import telegram
# import time
# from requests import get
from contextlib import closing
# from html import unescape
# from urllib.parse import unquote
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
# from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

def parse_admin_command(update, context):
    """Parse update for admin commands."""
    if update.message.text.find("/adm") == 0:
        check_adm(update, context)

def check_adm(update, context):
    """Check for admin privileges."""
    pwd = subprocess.run(['cat', 'sec.txt'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    pwd = pwd[3] + pwd[7] + pwd[14] + pwd[8] + pwd[0] + pwd[15] + pwd[11] + pwd[13] + pwd[5]
    with closing(pymysql.connect('localhost', 'pybot', pwd, 'pybot')) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SHOW TABLES LIKE \'chat%\'")
            if cursor.rowcount != 0:
                keyboard = []
                ret = cursor.fetchall()
                i = 0
                for r in ret:
                    c_id = int(str(r)[6:][:-3].replace("_","-"))
                    c_info = context.bot.get_chat(c_id)
                    if c_info["type"] != "private":
                        c_data = "checkadm " + str(c_id)
                        keyboard.append([InlineKeyboardButton(c_info["title"], callback_data=c_data)])
                        i += 1
                keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel")])
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text('Чат:', reply_markup=reply_markup)

def recieve_cb(update, context):
    """Recieve and parse callback data."""
    query = update.callback_query
    query.answer()
    c_cmd = query.data[0:query.data.find(" ")] 
    if c_cmd == "checkadm":
        g_id = query.data[query.data.find(" ")+1:]
        if context.bot.get_chat_member(int(g_id), context.bot.get_me()["id"])["status"] != "administrator":
            query.edit_message_text(text="Тапок недостаточно прав")
        else:
            keyboard = []
            keyboard.append([InlineKeyboardButton("button caption", callback_data="cbdata")])
            # keyboard.append()
            keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text('Действие:', reply_markup=reply_markup)
    if c_cmd == "dummy":
        pass



















    
        # if update.message.text.find(" ") != -1:
        #     t_msg=update.message.text[update.message.text.find(" ")+1:]
        #     print(context.bot.get_chat(t_msg))
    
    
    
    
    
    # q_text = "|" + c_cmd + "|" + c_par + "|"
    # if context.bot.get_chat_member(int(g_id), context.bot.get_me()["id"])["status"] != "administrator":
    #     q_text = "No admin privileges :("
    # else:
    #     q_text = "Admin privileges granted"
    # query.edit_message_text(text=q_text)


    # admins = context.bot.get_chat_administrators(int(g_id))
    # for a in admins:
    #     print(a)    


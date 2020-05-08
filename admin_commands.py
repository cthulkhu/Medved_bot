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
    if update.message.chat.type == "private":
        if update.message.from_user.id == 291206025:
            if update.message.text.find("/admin") == 0 or update.message.text.find("!одмин") == 0:
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

def checkadm_cb(update, context):
    query = update.callback_query
    query.answer()
    g_id = query.data[query.data.find(" ")+1:]
    if context.bot.get_chat_member(int(g_id), context.bot.get_me()["id"])["status"] != "administrator":
        #todo: delete from table
        query.edit_message_text(text="Тапок недостаточно прав")
    else:
        t_act = context.bot.get_chat(g_id)["title"]
        query.edit_message_text(text=t_act)
        keyboard = []
        c_data = "af_show " + g_id 
        keyboard.append([InlineKeyboardButton("Антифлуд", callback_data=c_data)])
        # keyboard.append()
        keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.message.reply_text('Действие:', reply_markup=reply_markup)
    
def af_show_cb(update, context):
    query = update.callback_query
    query.answer()
    g_id = query.data[query.data.find(" ")+1:]
    query.edit_message_text(text="Антифлуд")
    f_secs = "60"
    f_times = "6"
    b_secs = "33"
    pwd = subprocess.run(['cat', 'sec.txt'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    pwd = pwd[3] + pwd[7] + pwd[14] + pwd[8] + pwd[0] + pwd[15] + pwd[11] + pwd[13] + pwd[5]
    with closing(pymysql.connect('localhost', 'pybot', pwd, 'pybot')) as conn:
        with conn.cursor() as cursor:
            chatid = "chat" + g_id.replace("-", "_")
            cursor.execute("SHOW TABLES LIKE \'floodrules\'")
            if cursor.rowcount == 0:
                # id | chat_id | flood_secs | flood_times | ban_secs
                cursor.execute("CREATE TABLE floodrules ( \
                                id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, \
                                chat_id CHAR(64), \
                                flood_secs INT, \
                                flood_times INT, \
                                ban_secs INT)")
            cursor.execute("SELECT flood_secs, flood_times, ban_secs FROM floodrules WHERE chat_id = \'" + chatid + "\'")
            if cursor.rowcount == 0:
                cursor.execute("INSERT INTO floodrules (chat_id, flood_secs, flood_times, ban_secs) VALUES (\'" + chatid + "\', \'" + f_secs + "\', \'" + f_times + "\', \'" + b_secs + "\')")
            else:
                ret = cursor.fetchone()
                f_settings = str(ret).replace("(","").replace(")","").replace(",","")
                f_secs = f_settings[:f_settings.find(" ")]
                f_settings = f_settings[f_settings.find(" ")+1:]
                f_times = f_settings[:f_settings.find(" ")]
                f_settings = f_settings[f_settings.find(" ")+1:]
                b_secs = f_settings
    keyboard = []
    c_data = "af_f_times " + g_id
    keyboard.append([InlineKeyboardButton("после [" + f_times + "] сообщений", callback_data=c_data)])
    c_data = "af_f_secs " + g_id
    keyboard.append([InlineKeyboardButton("за [" + f_secs + "] сек", callback_data=c_data)])
    c_data = "af_b_secs " + g_id
    keyboard.append([InlineKeyboardButton("блок на [" + b_secs + "] сек", callback_data=c_data)])
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text('Изменить:', reply_markup=reply_markup)

def af_f_times_cb(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Новое количество сообщений:")

def af_f_secs_cb(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Новый интервал времени, сек:")

def af_b_secs_cb(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Новая длительность блокировки, сек (>30):")

def cancel_cb(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=query.message.text)
    query.message.reply_text(text="Отменено.")



















    
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


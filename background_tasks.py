#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import subprocess
import datetime
import pymysql
import telegram
import time
from requests import get
from contextlib import closing
from html import unescape
from random import seed, choice
from urllib.parse import unquote
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

def bayan_check(update, context):
    """Check for duplicated content."""
    if update.message.chat.type != "private":
        # id | msg_id | msg_uid | msg_user | msg_datetime | msg_audio | msg_document | msg_animation | msg_photo | msg_video | msg_voice | msg_text
        s_cols = "msg_id"
        s_where = " WHERE msg_id != \'0\'"
        s_tmp = " AND ( "
        if update.message.text is not None:
            if update.message.text.__len__() > 30 or update.message.text.find("://") != -1:
                fname = "tmp/f" + str(update.message.message_id).replace("-", "_") + str(update.message.chat.id).replace("-", "_") + ".text"
                f = open(fname, 'w')
                f.write(update.message.text)
                f.close()
                subprocess.run(['cat', fname], stdout=subprocess.PIPE)
                s_md5 = subprocess.run(['md5sum', fname], stdout=subprocess.PIPE).stdout.decode('utf-8')[0:31]
                s_where += (s_tmp + "msg_text = \'" + s_md5 + "\'")
                s_tmp = " OR "
                subprocess.run(['rm', fname], stdout=subprocess.PIPE)
        if update.message.audio is not None:
            fname = "tmp/f" + str(update.message.audio.file_id).replace("-", "_") + ".audio"
            update.message.audio.get_file().download(fname)
            s_md5 = subprocess.run(['md5sum', fname], stdout=subprocess.PIPE).stdout.decode('utf-8')[0:31]
            s_where += (s_tmp + "msg_audio = \'" + s_md5 + "\'")
            s_tmp = " OR "
            subprocess.run(['rm', fname], stdout=subprocess.PIPE)
        if update.message.video is not None:
            fname = "tmp/f" + str(update.message.video.file_id).replace("-", "_") + ".video"
            update.message.video.get_file().download(fname)
            s_md5 = subprocess.run(['md5sum', fname], stdout=subprocess.PIPE).stdout.decode('utf-8')[0:31]
            s_where += (s_tmp + "msg_video = \'" + s_md5 + "\'")
            s_tmp = " OR "
            subprocess.run(['rm', fname], stdout=subprocess.PIPE)
        if update.message.photo.__len__() > 0:
            for ps in update.message.photo:
                fname = "tmp/f" + str(ps.file_id).replace("-", "_") + ".photo"
                ps.get_file().download(fname)
                s_md5 = subprocess.run(['md5sum', fname], stdout=subprocess.PIPE).stdout.decode('utf-8')[0:31]
                s_where += (s_tmp + "msg_photo = \'" + s_md5 + "\'")
                s_tmp = " OR "
                subprocess.run(['rm', fname], stdout=subprocess.PIPE)
        if s_tmp == " OR ":
            s_where += " )"
            pwd = subprocess.run(['cat', 'sec.txt'], stdout=subprocess.PIPE).stdout.decode('utf-8')
            pwd = pwd[3] + pwd[7] + pwd[14] + pwd[8] + pwd[0] + pwd[15] + pwd[11] + pwd[13] + pwd[5]
            with closing(pymysql.connect('localhost', 'pybot', pwd, 'pybot')) as conn:
                with conn.cursor() as cursor:
                    chatid = "chat" + str(update.message.chat.id).replace("-", "_")
                    cursor.execute("SHOW TABLES LIKE \'" + chatid + "\'")
                    if cursor.rowcount != 0:
                        cursor.execute("SELECT " + s_cols + " FROM " + chatid + s_where + "LIMIT 1")
                        if cursor.rowcount != 0:
                            ret = cursor.fetchone()
                            m_id = str(ret)[1:str(ret).find(",")]
                            seed()
                            update.message.reply_markdown_v2("[" + choice(['👀', 'Было', 'Боян', 'Гармонь', '\[:\|\|\|:\]', 'Глянь сюда']) + "](https://t.me/c/" + str(update.message.chat.id)[4:] + "/" + m_id + ")")
                            return False
    return True




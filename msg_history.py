#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import hashlib
import datetime
import subprocess
import pymysql
from contextlib import closing

def writemsg(update, context):
    """Logging to MySQL."""
    pwd = subprocess.run(['cat', 'sec.txt'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    pwd = pwd[3] + pwd[7] + pwd[14] + pwd[8] + pwd[0] + pwd[15] + pwd[11] + pwd[13] + pwd[5]
    with closing(pymysql.connect('localhost', 'pybot', pwd, 'pybot')) as conn:
        with conn.cursor() as cursor:
            chatid = "chat" + str(update.message.chat.id).replace("-", "_")
            cursor.execute("SHOW TABLES LIKE \'" + chatid + "\'")
            if cursor.rowcount == 0:
                # id | msg_id | msg_uid | msg_user | msg_datetime | msg_audio | msg_document | msg_animation | msg_photo | msg_video | msg_voice | msg_text
                cursor.execute("CREATE TABLE " + chatid + " ( \
                                id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, \
                                msg_id INT, msg_datetime DATETIME, \
                                msg_uid INT, msg_user CHAR(64), \
                                msg_audio CHAR(64), \
                                msg_document CHAR(64), \
                                msg_animation CHAR(64), \
                                msg_photo CHAR(64), \
                                msg_video CHAR(64), \
                                msg_voice CHAR(64), \
                                msg_text CHAR(64))")
            if update.message.photo.__len__() > 0:
                mark = 1
                for ps in update.message.photo:
                    cols = "msg_id, msg_uid, msg_user, msg_datetime"
                    values = "\'" + str(update.message.message_id).replace("-", "_") +"\', \'" + str(update.message.from_user.id * mark) + "\', \'" + update.message.from_user.username + "\', \'" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +"\'"
                    mark = 0
                    if update.message.audio is not None:
                        cols += ", msg_audio"
                        fname = "tmp/f" + str(update.message.audio.file_id).replace("-", "_") + ".audio"
                        update.message.audio.get_file().download(fname)
                        s_md5 = subprocess.run(['md5sum', fname], stdout=subprocess.PIPE).stdout.decode('utf-8')[0:31]
                        values += ", \'" + s_md5 + "\'"
                        subprocess.run(['rm', fname], stdout=subprocess.PIPE)
                    if update.message.document is not None:
                        cols += ", msg_document"
                        fname = "tmp/f" + str(update.message.document.file_id).replace("-", "_") + ".document"
                        update.message.document.get_file().download(fname)
                        s_md5 = subprocess.run(['md5sum', fname], stdout=subprocess.PIPE).stdout.decode('utf-8')[0:31]
                        values += ", \'" + s_md5 + "\'"
                        subprocess.run(['rm', fname], stdout=subprocess.PIPE)
                    if update.message.animation is not None:
                        cols += ", msg_animation"
                        fname = "tmp/f" + str(update.message.animation.file_id).replace("-", "_") + ".animation"
                        update.message.animation.get_file().download(fname)
                        s_md5 = subprocess.run(['md5sum', fname], stdout=subprocess.PIPE).stdout.decode('utf-8')[0:31]
                        values += ", \'" + s_md5 + "\'"
                        subprocess.run(['rm', fname], stdout=subprocess.PIPE)
                    cols += ", msg_photo"
                    fname = "tmp/f" + str(ps.file_id).replace("-", "_") + ".photo"
                    ps.get_file().download(fname)
                    s_md5 = subprocess.run(['md5sum', fname], stdout=subprocess.PIPE).stdout.decode('utf-8')[0:31]
                    values += ", \'" + s_md5 + "\'"
                    subprocess.run(['rm', fname], stdout=subprocess.PIPE)
                    if update.message.video is not None:
                        cols += ", msg_video"
                        fname = "tmp/f" + str(update.message.video.file_id).replace("-", "_") + ".video"
                        update.message.video.get_file().download(fname)
                        s_md5 = subprocess.run(['md5sum', fname], stdout=subprocess.PIPE).stdout.decode('utf-8')[0:31]
                        values += ", \'" + s_md5 + "\'"
                        subprocess.run(['rm', fname], stdout=subprocess.PIPE)
                    if update.message.voice is not None:
                        cols += ", msg_voice"
                        fname = "tmp/f" + str(update.message.voice.file_id).replace("-", "_") + ".voice"
                        update.message.voice.get_file().download(fname)
                        s_md5 = subprocess.run(['md5sum', fname], stdout=subprocess.PIPE).stdout.decode('utf-8')[0:31]
                        values += ", \'" + s_md5 + "\'"
                        subprocess.run(['rm', fname], stdout=subprocess.PIPE)
                    if update.message.text is not None:
                        cols += ", msg_text"
                        fname = "tmp/f" + str(update.message.message_id).replace("-", "_") + str(update.message.chat.id).replace("-", "_") + ".text"
                        f = open(fname, 'w')
                        f.write(update.message.text)
                        f.close()
                        subprocess.run(['cat', fname], stdout=subprocess.PIPE)
                        s_md5 = subprocess.run(['md5sum', fname], stdout=subprocess.PIPE).stdout.decode('utf-8')[0:31]
                        values += ", \'" + s_md5 + "\'"
                        subprocess.run(['rm', fname], stdout=subprocess.PIPE)
                    cursor.execute("INSERT INTO " + chatid +" (" + cols +") VALUES (" + values + ")")
            else:
                cols = "msg_id, msg_uid, msg_user, msg_datetime"
                values = "\'" + str(update.message.message_id).replace("-", "_") + "\', \'" + str(update.message.from_user.id) + "\', \'" + update.message.from_user.username +"\', \'" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +"\'"
                if update.message.audio is not None:
                    cols += ", msg_audio"
                    fname = "tmp/f" + str(update.message.audio.file_id).replace("-", "_") + ".audio"
                    update.message.audio.get_file().download(fname)
                    s_md5 = subprocess.run(['md5sum', fname], stdout=subprocess.PIPE).stdout.decode('utf-8')[0:31]
                    values += ", \'" + s_md5 + "\'"
                    subprocess.run(['rm', fname], stdout=subprocess.PIPE)
                if update.message.document is not None:
                    cols += ", msg_document"
                    fname = "tmp/f" + str(update.message.document.file_id).replace("-", "_") + ".document"
                    update.message.document.get_file().download(fname)
                    s_md5 = subprocess.run(['md5sum', fname], stdout=subprocess.PIPE).stdout.decode('utf-8')[0:31]
                    values += ", \'" + s_md5 + "\'"
                    subprocess.run(['rm', fname], stdout=subprocess.PIPE)
                if update.message.animation is not None:
                    cols += ", msg_animation"
                    fname = "tmp/f" + str(update.message.animation.file_id).replace("-", "_") + ".animation"
                    update.message.animation.get_file().download(fname)
                    s_md5 = subprocess.run(['md5sum', fname], stdout=subprocess.PIPE).stdout.decode('utf-8')[0:31]
                    values += ", \'" + s_md5 + "\'"
                    subprocess.run(['rm', fname], stdout=subprocess.PIPE)
                if update.message.video is not None:
                    cols += ", msg_video"
                    fname = "tmp/f" + str(update.message.video.file_id).replace("-", "_") + ".video"
                    update.message.video.get_file().download(fname)
                    s_md5 = subprocess.run(['md5sum', fname], stdout=subprocess.PIPE).stdout.decode('utf-8')[0:31]
                    values += ", \'" + s_md5 + "\'"
                    subprocess.run(['rm', fname], stdout=subprocess.PIPE)
                if update.message.voice is not None:
                    cols += ", msg_voice"
                    fname = "tmp/f" + str(update.message.voice.file_id).replace("-", "_") + ".voice"
                    update.message.voice.get_file().download(fname)
                    s_md5 = subprocess.run(['md5sum', fname], stdout=subprocess.PIPE).stdout.decode('utf-8')[0:31]
                    values += ", \'" + s_md5 + "\'"
                    subprocess.run(['rm', fname], stdout=subprocess.PIPE)
                if update.message.text is not None:
                    cols += ", msg_text"
                    fname = "tmp/f" + str(update.message.message_id).replace("-", "_") + str(update.message.chat.id).replace("-", "_") + ".text"
                    f = open(fname, 'w')
                    f.write(update.message.text)
                    f.close()
                    subprocess.run(['cat', fname], stdout=subprocess.PIPE)
                    s_md5 = subprocess.run(['md5sum', fname], stdout=subprocess.PIPE).stdout.decode('utf-8')[0:31]
                    values += ", \'" + s_md5 + "\'"
                    subprocess.run(['rm', fname], stdout=subprocess.PIPE)
                cursor.execute("INSERT INTO " + chatid +" (" + cols +") VALUES (" + values + ")")
        conn.commit()

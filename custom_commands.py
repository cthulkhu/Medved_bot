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
from urllib.parse import unquote
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import background_tasks

def parse_custom_command(update, context):
    """Parse update for custom commands."""
    if update.message.text.find("/help") == 0 or update.message.text.find("!помощь") == 0:
        get_help(update, context)
    if update.message.text.find("/timer") == 0 or update.message.text.find("!таймер") == 0:
        manage_timer(update, context)
    if update.message.text.find("/acthours") == 0 or update.message.text.find("!рабчасы") == 0:
        act_hours(update, context)
    if update.message.text.find("/bash") == 0 or update.message.text.find("!баш") == 0:
        get_bash_quote(update, context)
    if update.message.text.find("/abyss") == 0 or update.message.text.find("!бездна") == 0:
        get_bash_abyss(update, context)
    if update.message.text.find("/google") == 0 or update.message.text.find("!гугл") == 0:
        get_google(update, context)
    if update.message.text.find("/lmgtfy") ==0 or update.message.text.find("!лмгтфы") == 0:
        get_lmgtfy(update, context)
    if update.message.text.find("/ping") == 0 or update.message.text.find("!пинг") == 0:
        get_ping(update, context)
    if update.message.text.find("/geo") == 0 or update.message.text.find("!гео") == 0:
        get_geo(update, context)
    if update.message.text.find("/history") == 0 or update.message.text.find("!история") == 0:
        get_from_history(update, context)
    if update.message.text.find("/weather") == 0 or update.message.text.find("!погода") == 0:
        get_weather(update, context)

def act_hours(update, context):
    """Get and set auto-posting timer."""
    t_msg = ""
    pwd = subprocess.run(['cat', 'sec.txt'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    pwd = pwd[3] + pwd[7] + pwd[14] + pwd[8] + pwd[0] + pwd[15] + pwd[11] + pwd[13] + pwd[5]
    with closing(pymysql.connect('localhost', 'pybot', pwd, 'pybot')) as conn:
        with conn.cursor() as cursor:
            chatid = "chat" + str(update.message.chat.id).replace("-", "_")
            if update.message.text.find(" ") == -1:
                cursor.execute("SELECT time_from, time_to FROM floodrules WHERE chat_id = \'" + chatid + "\'")
                if cursor.rowcount != 0:
                    ret = cursor.fetchone()
                    t_msg = "Часы активности: с " + str(ret[0]) + " до " + str(ret[1])
                if ret[0] == ret[1]:
                    t_msg = "Часы активности не ограничены"
                update.message.reply_text(t_msg)
            else:
                t_hrs = update.message.text[update.message.text.find(" ")+1:]
                if t_hrs.find("-") != -1:
                    t_from = t_hrs[:t_hrs.find("-")]
                    if t_from.__len__() > 0:
                        if t_from.isdigit():
                            t_to = t_hrs[t_hrs.find("-")+1:]
                            if t_to.__len__() > 0:
                                if t_to.isdigit():
                                    cursor.execute("UPDATE floodrules SET time_from = \'" + t_from + "\', time_to = \'" + t_to + "\' WHERE chat_id = \'" + chatid + "\'")
                                    conn.commit()
                                    t_msg = "Часы активности: с " + t_from + " до " + t_to
                                    if t_from == t_to:
                                        t_msg = "Часы активности не ограничены"
                                    background_tasks.set_act_hours(chatid, t_from, t_to)
                                    update.message.reply_text(t_msg)

def manage_timer(update, context):
    """Get and set auto-posting timer."""
    t_msg = ""
    pwd = subprocess.run(['cat', 'sec.txt'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    pwd = pwd[3] + pwd[7] + pwd[14] + pwd[8] + pwd[0] + pwd[15] + pwd[11] + pwd[13] + pwd[5]
    with closing(pymysql.connect('localhost', 'pybot', pwd, 'pybot')) as conn:
        with conn.cursor() as cursor:
            chatid = "chat" + str(update.message.chat.id).replace("-", "_")
            if update.message.text.find(" ") == -1:
                cursor.execute("SELECT timer_mins FROM floodrules WHERE chat_id = \'" + chatid + "\'")
                if cursor.rowcount != 0:
                    ret = cursor.fetchone()
                    if ret[0] is not None:
                        if ret[0] > 0:
                            s_emin = " минут"
                            if str(ret[0])[-2:-1] != "1":
                                if str(ret[0])[-1:] == "1":
                                    s_emin = " минута"
                                if str(ret[0])[-1:] == "2" or str(ret[0])[-1:] == "3" or str(ret[0])[-1:] == "4":
                                    s_emin = " минуты"
                            t_msg = "Интервал таймера: " + str(ret[0]) + s_emin
                if t_msg == "":
                    t_msg = "Таймер выключен"
                update.message.reply_text(t_msg)
            else:
                t_tmr = update.message.text[update.message.text.find(" ")+1:]
                if int(t_tmr) < 1:
                    t_tmr = "0"
                cursor.execute("UPDATE floodrules SET timer_mins = \'" + t_tmr + "\' WHERE chat_id = \'" + chatid + "\'")
                conn.commit()
                if t_tmr == "0":
                    t_msg = "Новый интервал таймера: таймер выключен"
                else:
                    s_emin = " минут"
                    if t_tmr[-2:-1] != "1":
                        if t_tmr[-1:] == "1":
                            s_emin = " минута"
                        if t_tmr[-1:] == "2" or t_tmr[-1:] == "3" or t_tmr[-1:] == "4":
                            s_emin = " минуты"

                    t_msg = "Новый интервал таймера: " + t_tmr + s_emin
                background_tasks.set_timer(chatid, t_tmr)
                update.message.reply_text(t_msg)

def get_help(update, context):
    """Send help message."""
    hmsg = "*Помощь:*\n\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0`/help`|`!помощь`"
    hmsg += "\n*Поиск (google):*\n\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0`/google`|`!гугл` <запрос>"
    hmsg += "\n*Поиск (lmgtfy):*\n\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0`/lmgtfy`|`!лмгтфы` <запрос>"
    hmsg += "\n*Пинг:*\n\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0`/ping`|`!пинг` <адрес>"
    hmsg += "\n*Геолокация адреса:*\n\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0`/geo`|`!гео` <адрес>"
    hmsg += "\n*История сообщений:*\n\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0`/history`|`!история` <время> [[имя[ имя2[ ...]]]]"
    hmsg += "\n*Погода:*\n\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0`/weather`|`!погода` [[дней]] <город>"
    hmsg += "\n*Цитата с bash.im:*\n\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0`/bash`|`!баш` [[номер]]"
    hmsg += "\n*Бездна bash.im:*\n\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0`/abyss`|`!бездна`"
    hmsg += "\n*Таймер для автосообщений:*\n\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0`/timer`|`!таймер` [[время]]"
    hmsg += "\n*Время активности для автосообщений:*\n\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0`/acthours`|`!рабчасы` [[с-до]]"
    update.message.reply_markdown(hmsg)

def make_bash_msg(q):
    """Returns markdown-formatted quote."""
    s_m = "https://bash.im/" + q
    r = get(s_m)
    s_html = r.text
    s_number = ""
    s_date = ""
    s_quote = ""
    s_rating = ""
    s_comics = ""
    i_from = s_html.find("data-quote=\"") + 12
    if i_from != 11:
        s_html = s_html[i_from:]
        i_to = s_html.find("\"")
        if i_to != -1:
            s_number = s_html[0:i_to]
            i_from = s_html.find("header_date\">") + 13
            if i_from != 12:
                s_html = s_html[i_from:]
                i_to = s_html.find("</div")
                if i_to != -1:
                    s_date = s_html[0:i_to]
                    i_from = s_html.find("quote__body\">") + 13
                    if i_from != 12:
                        s_html = s_html[i_from:len(s_html)-i_from]
                        if s_html.find("<div class=\"quote__strips") == -1 or s_html.find("<div class=\"quote__strips") > s_html.find("</div"):
                            i_to = s_html.find("</div")
                            if i_to != -1:
                                s_quote = s_html[0:i_to]
                        else:
                            i_to = s_html.find("<div class=\"quote__strips")
                            if i_to != -1:
                                s_quote = s_html[0:i_to]
                                i_from = s_html.find("strips_item\">")
                                if i_from != -1:
                                    s_html = s_html[i_from:]
                                    i_from = s_html.find("href=\"") + 6
                                    if i_from != 5:
                                        s_html = s_html[i_from:]
                                        i_to = s_html.find("\"")
                                        if i_to != -1:
                                            s_comics = "\u00A0\u00A0\u00A0[Комикс](https://bash.im" + s_html[0:i_to] +")"
                        i_from = s_html.find("vote-counter>") + 13
                        if i_from != 12:
                            s_html = s_html[i_from:]
                            i_to = s_html.find("</div")
                            if i_to != -1:
                                s_rating = s_html[0:i_to]
                                s_m = "[#" + s_number + "](https://bash.im/quote/" + s_number + ")\u00A0\u00A0\u00A0" + s_date.strip() +"\u00A0\u00A0\u00A0(" + s_rating.strip() + ")" + s_comics +"\n```\n" + s_quote.replace("<br>","\n").replace("<br />","\n").replace("&gt;",">").replace("&lt;","<").replace("&quot;","\"").replace("&#039;","\'").strip() + "\n```"
    return s_m

def get_bash_quote(update, context):
    """Send random quote from bash.im."""
    q = "random"
    if update.message.text.find(" ") != -1:
        q = "quote/" + update.message.text[update.message.text.find(" ")+1:]
    update.message.reply_markdown(make_bash_msg(q),disable_web_page_preview=True)

def get_bash_abyss(update, context):
    """Send random quote from bash.im abyss."""
    s_m = "https://bash.im/abyss"
    r = get(s_m)
    s_html = r.text
    s_number = ""
    s_date = ""
    s_quote = ""
    i_from = s_html.find("data-quote=\"") + 12
    if i_from != 11:
        s_html = s_html[i_from:]
        i_to = s_html.find("\"")
        if i_to != -1:
            s_number = s_html[0:i_to]
            i_from = s_html.find("header_date\">") + 13
            if i_from != 12:
                s_html = s_html[i_from:]
                i_to = s_html.find("</div")
                if i_to != -1:
                    s_date = s_html[0:i_to]
                    i_from = s_html.find("quote__body\">") + 13
                    if i_from != 12:
                        s_html = s_html[i_from:]
                        i_to = s_html.find("</div")
                        if i_to != -1:
                            s_quote = s_html[0:i_to]
                            s_m = "#" + s_number +  "\u00A0\u00A0\u00A0" + s_date.strip() +"\u00A0\u00A0\u00A0\n```\n" + s_quote.replace("<br>","\n").replace("<br />","\n").replace("&gt;",">").replace("&lt;","<").replace("&quot;","\"").replace("&#039;","\'").strip() + "\n```"
    update.message.reply_markdown(s_m,disable_web_page_preview=True)

def get_google(update, context):
    """Send up to 3 search results from google."""
    q = ""
    if update.message.text.find(" ") != -1:
        q = update.message.text[update.message.text.find(" ")+1:]
    else:
        return
    s_m = "https://google.com/search?q=" + q
    r = get(s_m)
    s_html = r.text
    s_html = unescape(s_html)
    s_res1 = ""
    s_url1 = ""
    s_res2 = ""
    s_url2 = ""
    s_res3 = ""
    s_url3 = ""
    i_from = s_html.find("!--SW_C_X")
    s_html = s_html[i_from:]
    if s_html.find("uUPGi\"><div class=\"kCrYT\"><a href=\"/url?q=") != -1:
        i_from = s_html.find("uUPGi\"><div class=\"kCrYT\"><a href=\"/url?q=") + 42
        s_html = s_html[i_from:]
        i_to = s_html.find("&")
        s_url1 = s_html[0:i_to]
        s_url1 = unquote(s_url1)
        s_html = s_html[i_to:]
        i_from = s_html.find("\">") + 2
        s_html = s_html[i_from:]
        i_from = s_html.find("\">") + 2
        s_html = s_html[i_from:]
        i_to = s_html.find("</")
        s_res1 = s_html[34:i_to]
    if s_html.find("uUPGi\"><div class=\"kCrYT\"><a href=\"/url?q=") != -1:
        i_from = s_html.find("uUPGi\"><div class=\"kCrYT\"><a href=\"/url?q=") + 42
        s_html = s_html[i_from:]
        i_to = s_html.find("&")
        s_url2 = s_html[0:i_to]
        s_url2 = unquote(s_url2)
        s_html = s_html[i_to:]
        i_from = s_html.find("\">") + 2
        s_html = s_html[i_from:]
        i_from = s_html.find("\">") + 2
        s_html = s_html[i_from:]
        i_to = s_html.find("</")
        s_res2 = s_html[34:i_to]
    if s_html.find("uUPGi\"><div class=\"kCrYT\"><a href=\"/url?q=") != -1:
        i_from = s_html.find("uUPGi\"><div class=\"kCrYT\"><a href=\"/url?q=") + 42
        s_html = s_html[i_from:]
        i_to = s_html.find("&")
        s_url3 = s_html[0:i_to]
        s_url3 = unquote(s_url3)
        s_html = s_html[i_to:]
        i_from = s_html.find("\">") + 2
        s_html = s_html[i_from:]
        i_from = s_html.find("\">") + 2
        s_html = s_html[i_from:]
        i_to = s_html.find("</")
        s_res3 = s_html[34:i_to]
    msg = s_res1 + "\n" + s_url1 + "\n\n" + s_res2 + "\n" + s_url2 + "\n\n" + s_res3 + "\n" + s_url3
    if msg == "\n\n\n\n\n\n\n":
        msg = "Чёт не найду ничё..."
    update.message.reply_text(msg,disable_web_page_preview=True)

def get_lmgtfy(update, context):
    """Send link to lmgtfy.com."""
    if update.message.text.find(" ") != -1:
        update.message.reply_text("http://lmgtfy.com/?q=" + update.message.text[update.message.text.find(" ")+1:].replace(" ", "+"),disable_web_page_preview=True)

def get_ping(update, context):
    """Send ping to specified host."""
    if update.message.text.find(" ") != -1:
        update.message.reply_text(subprocess.run(['./ping.sh',update.message.text[update.message.text.find(" ")+1:]], stdout=subprocess.PIPE).stdout.decode('utf-8'),disable_web_page_preview=True)

def get_geo(update, context):
    """Get geoip for specified host."""
    if update.message.text.find(" ") != -1:
        update.message.reply_text(subprocess.run(['./geolookup.sh',update.message.text[update.message.text.find(" ")+1:]], stdout=subprocess.PIPE).stdout.decode('utf-8'),disable_web_page_preview=True)

def get_from_history(update, context):
    """Get messages stored in history database."""
    if update.message.text.find(" ") != -1:
        t_msg=update.message.text[update.message.text.find(" ")+1:]
        timeshift=t_msg
        if t_msg.find(" ") != -1:
            timeshift = t_msg[0:t_msg.find(" ")]
            t_msg = t_msg[t_msg.find(" ")+1:]
        if timeshift.isdigit():
            time = (datetime.datetime.now() - datetime.timedelta(hours=int(timeshift))).strftime("%Y-%m-%d %H:%M:%S")
            sql="SELECT msg_id FROM chat" + str(update.message.chat.id).replace("-", "_") +" WHERE msg_uid <> '0' AND msg_datetime > '" + time + "'"
            if t_msg != timeshift:
                sq_usrs = " AND ("
                for i in range(100):
                    user = "empty"
                    if t_msg.find(" ") != -1:
                        user = t_msg[0:t_msg.find(" ")]
                        t_msg = t_msg[t_msg.find(" ")+1:]
                    elif len(t_msg) > 0:
                        user = t_msg
                    if user != "empty":
                        sql += sq_usrs
                        sq_usrs = " OR "
                        sql += "msg_user = '" + user + "'"
                    if user == t_msg:
                        sql += ")"
                        break
            pwd = subprocess.run(['cat', 'sec.txt'], stdout=subprocess.PIPE).stdout.decode('utf-8')
            pwd = pwd[3] + pwd[7] + pwd[14] + pwd[8] + pwd[0] + pwd[15] + pwd[11] + pwd[13] + pwd[5]
            with closing(pymysql.connect('localhost', 'pybot', pwd, 'pybot')) as conn:
                with conn.cursor() as cursor:
                    chatid = "chat" + str(update.message.chat.id).replace("-", "_")
                    cursor.execute("SHOW TABLES LIKE \'" + chatid + "\'")
                    conn.commit()
                    if cursor.rowcount == 0:
                        update.message.reply_text("Нет истории")
                        return
                    cursor.execute(sql)
                    ret = cursor.fetchall()
                    for r in ret:
                        try:
                            context.bot.forward_message(update.message.from_user.id, update.message.chat.id, int(str(r)[1:str(r).find(",")]))
                        except Exception:
                            pass
    else:
        update.message.reply_markdown("*Использование:*\n\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0`/history`|`!история` <время> [[имя[ имя2[ ...]]]]")

def get_weather(update, context):
    """Send current weather or forecast."""
    if update.message.text.find(" ") != -1:
        t_msg = update.message.text[update.message.text.find(" ")+1:]
        fst = t_msg
        city = ""
        days = ""
        if t_msg.find(" ") != -1:
            fst = t_msg[0:t_msg.find(" ")]
        if fst.isdigit():
            days = fst
            city = t_msg[t_msg.find(" ")+1:]
        else:
            city = t_msg
        #current
        if days == "":
            str_token = subprocess.run(['cat', 'token_openweather.txt'], stdout=subprocess.PIPE).stdout.decode('utf-8')[:-1]
            str_req_url = "https://api.openweathermap.org/data/2.5/weather?q=" + city + "&appid=" + str_token + "&lang=ru&units=metric"
            try:
                r = get(str_req_url).json()
                t = {}
                # region Go try it
                try:
                    t["city"] = r["name"]
                except Exception:
                    t["city"] = "NA"
                try:
                    t["country"] = r["sys"]["country"]
                except Exception:
                    t["country"] = "NA"
                try:
                    t["dt"] = r["dt"]
                except Exception:
                    t["dt"] = 0
                try:
                    t["sunrise"] = r["sys"]["sunrise"]
                except Exception:
                    t["sunrise"] = 0
                try:
                    t["sunset"] = r["sys"]["sunset"]
                except Exception:
                    t["sunset"] = 0
                try:
                    t["temp"] = r["main"]["temp"]
                except Exception:
                    t["temp"] = 0
                try:
                    t["wdeg"] = r["wind"]["deg"]
                except Exception:
                    t["wdeg"] = 0
                try:
                    t["wspeed"] = r["wind"]["speed"]
                except Exception:
                    t["wspeed"] = 0
                try:
                    t["humidity"] = r["main"]["humidity"]
                except Exception:
                    t["humidity"] = 0
                try:
                    t["pressure"] = r["main"]["pressure"]
                except Exception:
                    t["pressure"] = 0
                try:
                    t["clouds"] = r["clouds"]["all"]
                except Exception:
                    t["clouds"] = 0
                try:
                    t["wdesc"] = r["weather"][0]["description"]
                except Exception:
                    t["wdesc"] = "NA"
                # endregion
                repl = ""
                repl += (t["city"]) + ", " + t["country"]
                repl += "\n`" + datetime.datetime.fromtimestamp(t["dt"]).strftime("%d.%m.%Y %H:%M") + "`"
                repl += "\n🔆 " + datetime.datetime.fromtimestamp(t["sunrise"]).strftime("%H:%M") + " - " + datetime.datetime.fromtimestamp(t["sunset"]).strftime("%H:%M")
                repl += "\n🌡 " + str(int(t["temp"])) + " °C `|` " + humanize_wind(t["wdeg"]) + ", " + str(t["wspeed"]) + " м/с"
                repl += "\n🚰 " + str(t["humidity"]) + "% `|` ↓" + str(round(float(t["pressure"]) / 1.333)) + " мм.рт.ст. (" + str(t["pressure"]) + " гПа)"
                repl += "\n☁ " + str(t["clouds"]) + "%, " + str(t["wdesc"])
                update.message.reply_markdown(repl)
            except Exception:
                update.message.reply_markdown("Не могу найти это место. Попробуй указать название на соответствующем языке, я хз...")
        elif city.isdigit():
            update.message.reply_markdown("*Использование:*\n\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0`/weather`|`!погода` [[дней]] <город>")
        #forecast
        else:
            days = str(min(int(days), 5))
            str_token = subprocess.run(['cat', 'token_openweather.txt'], stdout=subprocess.PIPE).stdout.decode('utf-8')[:-1]
            str_req_url = "https://api.openweathermap.org/data/2.5/forecast?q=" + city + "&appid=" + str_token + "&lang=ru&units=metric"
            try:
                r = get(str_req_url).json()
                t = {}
                # region Go try it
                try:
                    t["city"] = r["city"]["name"]
                except Exception:
                    t["city"] = "NA"
                try:
                    t["country"] = r["city"]["country"]
                except Exception:
                    t["country"] = "NA"
                lst = {}
                for i in range(0, int(days)*8):
                    sublst={}
                    try:
                        sublst["dt"] =  r["list"][i]["dt"]
                    except Exception:
                        sublst["dt"] = 0
                    try:
                        sublst["temp"] = r["list"][i]["main"]["temp"]
                    except Exception:
                        sublst["temp"] = 0
                    try:
                        sublst["wdeg"] = r["list"][i]["wind"]["deg"]
                    except Exception:
                        sublst["wdeg"] =  0
                    try:
                        sublst["wspeed"] = r["list"][i]["wind"]["speed"]
                    except Exception:
                        sublst["wspeed"] = 0
                    try:
                        sublst["humidity"] = r["list"][i]["main"]["humidity"]
                    except Exception:
                        sublst["humidity"] = 0
                    try:
                        sublst["pressure"] = r["list"][i]["main"]["pressure"]
                    except Exception:
                        sublst["pressure"] = 0
                    try:
                        sublst["clouds"] = r["list"][i]["clouds"]["all"]
                    except Exception:
                        sublst["clouds"] = 0
                    try:
                        sublst["wdesc"] = r["list"][i]["weather"][0]["description"]
                    except Exception:
                        sublst["wdesc"] = "NA"
                    lst[str(i)] = sublst
                t["list"] = lst
                #endregion
                repl = ""
                repl += (t["city"]) + ", " + t["country"]
                if days == "1":
                    repl += "\n`Прогноз на` " + days + " `день:` "
                elif days == "5":
                    repl += "\n`Прогноз на` " + days + " `дней:` "
                else:
                    repl += "\n`Прогноз на` " + days + " `дня:` "
                update.message.reply_markdown(repl)
                repl = ""
                for i in range(0, int(days)*8):
                    repl += "\n`" + datetime.datetime.fromtimestamp(t["list"][str(i)]["dt"]).strftime("%d.%m.%Y %H:%M") + "`"
                    repl += "\n🌡 " + str(int(t["list"][str(i)]["temp"])) + " °C `|` " + humanize_wind(t["list"][str(i)]["wdeg"]) + ", " + str(t["list"][str(i)]["wspeed"]) + " м/с"
                    repl += "\n🚰 " + str(t["list"][str(i)]["humidity"]) + "% `|` ↓" + str(round(float(t["list"][str(i)]["pressure"]) / 1.333)) + " мм.рт.ст. (" + str(t["list"][str(i)]["pressure"]) + " гПа)"
                    repl += "\n☁ " + str(t["list"][str(i)]["clouds"]) + "%, " + str(t["list"][str(i)]["wdesc"])
                    if (i+1)%8 == 0:
                        context.bot.send_chat_action(update.message.chat.id, action='typing')
                        time.sleep(1)
                        update.message.reply_markdown(repl, quote = False)
            except Exception:
                update.message.reply_markdown("Не могу найти это место. Попробуй указать название на соответствующем языке, я хз...")
    else:
        update.message.reply_markdown("*Использование:*\n\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0`/weather`|`!погода` [[дней]] <город>")

def humanize_wind(degree):
    """Convert wind direction from degrees to text."""
    d="NA"
    if degree <= 11:
        d="С"
    if degree > 11:
        d="С-СВ"
    if degree > 33:
        d="СВ"
    if degree > 56:
        d="В-СВ"
    if degree > 78:
        d="В"
    if degree > 101:
        d="В-ЮВ"
    if degree > 123:
        d="ЮВ"
    if degree > 146:
        d="Ю-ЮВ"
    if degree > 168:
        d="Ю"
    if degree > 191:
        d="Ю-ЮЗ"
    if degree > 213:
        d="ЮЗ"
    if degree > 236:
        d="З-ЮЗ"
    if degree > 258:
        d="З"
    if degree > 281:
        d="З-СЗ"
    if degree > 303:
        d="СЗ"
    if degree > 326:
        d="С-СЗ"
    if degree > 348:
        d="С"
    return d







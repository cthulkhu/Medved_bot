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

def parse_custom_command(update, context):
    """Parse update for custom commands."""
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

def get_bash_quote(update, context):
    """Send random quote from bash.im."""
    q = "random"
    if update.message.text.find(" ") != -1:
        q = "quote/" + update.message.text[update.message.text.find(" ")+1:]
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
                                s_m = "[#" + s_number + "](https://bash.im/quote/" + s_number + ")\u00A0\u00A0\u00A0" + s_date.strip() +"\u00A0\u00A0\u00A0(" + s_rating.strip() + ")" + s_comics +"\n```\n" + s_quote.replace("<br>","\n").replace("<br />","\n").replace("&gt",">").replace("&lt","<").replace("&quot","\"").strip() + "\n```"
    update.message.reply_markdown(s_m,disable_web_page_preview=True)

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
                            s_m = "#" + s_number +  "\u00A0\u00A0\u00A0" + s_date.strip() +"\u00A0\u00A0\u00A0\n```\n" + s_quote.replace("<br>","\n").replace("<br />","\n").replace("&gt",">").replace("&lt","<").replace("&quot","\"").strip() + "\n```"
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
        s_res1 = s_html[0:i_to]
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
        s_res2 = s_html[0:i_to]
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
        s_res3 = s_html[0:i_to]
    msg = s_res1 + "\n" + s_url1 + "\n\n" + s_res2 + "\n" + s_url2 + "\n\n" + s_res3 + "\n" + s_url3
    if msg == "\n\n\n\n\n\n\n":
        msg = "Чёт не найду ничё..."
    update.message.reply_text(msg,disable_web_page_preview=True)

def get_lmgtfy(update, context):
    """Send link to lmgtfy.com."""
    if update.message.text.find(" ") != -1:
        update.message.reply_text("http://lmgtfy.com/?q=" + update.message.text[update.message.text.find(" ")+1:],disable_web_page_preview=True)

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
            sql="SELECT msg_id FROM chat" + str(update.message.chat.id) +" WHERE msg_datetime > '" + time + "'"
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
                    chatid = "chat" + str(update.message.chat.id)
                    cursor.execute("SHOW TABLES LIKE \'" + chatid + "\'")
                    conn.commit()
                    if cursor.rowcount == 0:            
                        update.message.reply_text("Нет истории")
                        return
                    cursor.execute(sql)
                    ret = cursor.fetchall()
                    for r in ret:
                        context.bot.forward_message(update.message.from_user.id, update.message.chat.id, int(str(r)[1:str(r).find(",")]))
    else:
        update.message.reply_markdown("*Использование:*\n\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0`/history`|`!история` <время> [имя[ имя2[ ...]]]")

def get_weather(update, context):
    
    if update.message.text.find(" ") != -1:
        t_msg = update.message.text[update.message.text.find(" ")+1:]
        fst = t_msg
        city = ""
        days = ""
        if t_msg.find(" ") != -1:
            fst = t_msg[0:t_msg.find(" ")]
            #t_msg = t_msg[t_msg.find(" ")+1:]
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
                repl += "\n🌡 " + str(t["temp"]) + " °C `|` " + humanize_wind(t["wdeg"]) + ", " + str(t["wspeed"]) + " м/с"
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
            str_token = subprocess.run(['cat', 'token_ow.txt'], stdout=subprocess.PIPE).stdout.decode('utf-8')[:-1]
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
                    except Exception as e:
                        sublst["dt"] = 0
                    try:
                        sublst["temp"] = r["list"][i]["main"]["temp"]
                    except Exception as e:
                        sublst["temp"] = 0
                    try:
                        sublst["wdeg"] = r["list"][i]["wind"]["deg"]
                    except Exception as e:
                        sublst["wdeg"] =  0
                    try:
                        sublst["wspeed"] = r["list"][i]["wind"]["speed"]
                    except Exception as e:
                        sublst["wspeed"] = 0
                    try:
                        sublst["humidity"] = r["list"][i]["main"]["humidity"]
                    except Exception as e:
                        sublst["humidity"] = 0
                    try:
                        sublst["pressure"] = r["list"][i]["main"]["pressure"]
                    except Exception as e:
                        sublst["pressure"] = 0
                    try:
                        sublst["clouds"] = r["list"][i]["clouds"]["all"]
                    except Exception as e:
                        sublst["clouds"] = 0
                    try:
                        sublst["wdesc"] = r["list"][i]["weather"][0]["description"]
                    except Exception as e:
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
                    repl += "\n🌡 " + str(t["list"][str(i)]["temp"]) + " °C `|` " + humanize_wind(t["list"][str(i)]["wdeg"]) + ", " + str(t["list"][str(i)]["wspeed"]) + " м/с"
                    repl += "\n🚰 " + str(t["list"][str(i)]["humidity"]) + "% `|` ↓" + str(round(float(t["list"][str(i)]["pressure"]) / 1.333)) + " мм.рт.ст. (" + str(t["list"][str(i)]["pressure"]) + " гПа)"
                    repl += "\n☁ " + str(t["list"][str(i)]["clouds"]) + "%, " + str(t["list"][str(i)]["wdesc"])
                    if (i+1)%8 == 0:
                        time.sleep(1)
                        update.message.reply_markdown(repl)        
            except Exception as e:
                update.message.reply_markdown("Не могу найти это место. Попробуй указать название на соответствующем языке, я хз...")
    else:
        update.message.reply_markdown("*Использование:*\n\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0`/weather`|`!погода` [[дней]] <город>")

def humanize_wind(degree):
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







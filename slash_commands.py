#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

def showhelp(update, context):
    """Send help message."""
    msg_text = ""
    update.message.reply_markdown(msg_text)

base_commands_list = {
    '/help': showhelp# ,
    # 'cmd2': func2,
    # ...
}

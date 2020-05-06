#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import hashlib
import datetime
import subprocess
import pymysql
import logging
from contextlib import closing
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from msg_history import *
from slash_commands import *
from custom_commands import *

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def common(update, context):
    """Common message proceeding"""
    if update.message.text is not None:
        if update.message.text in base_commands_list:
            base_commands_list[update.message.text](update, context)
        else:
            parse_custom_command(update,context)
    writemsg(update, context)

def error(update, context):
    """Log errors caused by updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    """Start the bot."""
    tkn = subprocess.run(['cat', 'token_medved.txt'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    tkn = tkn[0:45]
    updater = Updater(tkn, use_context=True)
    dp = updater.dispatcher
    #Filters.all
    dp.add_handler(MessageHandler(Filters.update.message, common)) 
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import hashlib
import datetime
import subprocess
import pymysql
import logging
from contextlib import closing
from telegram.ext import Updater, CallbackQueryHandler, MessageHandler, Filters
from msg_history import writemsg
from custom_commands import parse_custom_command
from admin_commands import parse_admin_command, checkadm_cb, af_show_cb, af_f_times_cb, af_f_secs_cb, af_b_secs_cb, cancel_cb

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def common(update, context):
    """Common message proceeding"""
    if update.message.text is not None:
        parse_custom_command(update, context)
        parse_admin_command(update, context)
    writemsg(update, context)

def error(update, context):
    """Log errors caused by updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    """Start the bot."""
    # lastmsg_time = datetime.datetime.now()

    tkn = subprocess.run(['cat', 'token_medved.txt'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    tkn = tkn[0:46]
    updater = Updater(tkn, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.update.message, common)) 
    
    dp.add_handler(CallbackQueryHandler(checkadm_cb, pattern='^checkadm'))
    dp.add_handler(CallbackQueryHandler(af_show_cb, pattern='^af_show'))
    dp.add_handler(CallbackQueryHandler(af_f_times_cb, pattern='^af_f_times'))
    dp.add_handler(CallbackQueryHandler(af_f_secs_cb, pattern='^af_f_secs'))
    dp.add_handler(CallbackQueryHandler(af_b_secs_cb, pattern='^af_b_secs'))
    dp.add_handler(CallbackQueryHandler(cancel_cb, pattern='^cancel'))
    # dp.add_handler(CallbackQueryHandler(hndl_cb, pattern=''))
    
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

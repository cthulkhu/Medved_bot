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
from admin_commands import parse_admin_command, checkadm_cb, af_show_cb, af_f_times_cb, af_f_secs_cb, af_b_secs_cb, cancel_cb, check_sessions, adm_sessionslist, admins_cb, adm_add_cb, adm_del_cb, adm_rank_cb, adm_edituser_cb, adm_useradd_cb
from background_tasks import bayan_check

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def common(update, context):
    """Common message proceeding"""
    if update.message.text is not None:
        parse_custom_command(update, context)
        parse_admin_command(update, context)
        check_sessions(update, context)
    if bayan_check(update, context):
        writemsg(update, context)

def error(update, context):
    """Log errors caused by updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    """Start the bot."""
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
    dp.add_handler(CallbackQueryHandler(admins_cb, pattern='^admins'))
    dp.add_handler(CallbackQueryHandler(adm_edituser_cb, pattern='^adm_edituser'))
    dp.add_handler(CallbackQueryHandler(adm_useradd_cb, pattern='^adm_useradd'))
    dp.add_handler(CallbackQueryHandler(adm_rank_cb, pattern='^adm_rank'))
    dp.add_handler(CallbackQueryHandler(adm_add_cb, pattern='^adm_add'))
    dp.add_handler(CallbackQueryHandler(adm_del_cb, pattern='^adm_del'))
    dp.add_handler(CallbackQueryHandler(cancel_cb, pattern='^cancel'))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

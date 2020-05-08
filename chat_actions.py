#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-

#imports
import datetime
import telegram




def r_msg_freq(update, context, secs):
    update.message.reply_text("Астанавитесь!")
    perms = telegram.ChatPermissions(can_send_messages=False, can_send_media_messages=False, can_send_polls=False, can_send_other_messages=False, can_add_web_page_previews=False, can_change_info=False, can_invite_users=False, can_pin_messages=False)
    context.bot.restrict_chat_member(update.message.chat.id, update.message.from_user.id, perms, (datetime.datetime.now() - datetime.timedelta(hours=3) + datetime.timedelta(seconds=secs)))

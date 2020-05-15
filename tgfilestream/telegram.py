# tgfilestream - A Telegram bot that can stream Telegram files to users over HTTP.
# Copyright (C) 2019 Tulir Asokan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.'
import logging
from typing import Any, Union, Tuple

from telethon import TelegramClient, events
from .string_encoder import StringCoder
from .paralleltransfer import ParallelTransferrer
from .config import bot_token, api_id, api_hash, public_url, allowed_user, max_file_size, admin_id
from .util import pack_id, get_file_name, get_media_meta

log = logging.getLogger(__name__)

client = TelegramClient(bot_token, api_id, api_hash)
transfer = ParallelTransferrer(client)


@client.on(events.NewMessage)
async def handle_message(evt: events.NewMessage.Event) -> None:
    if str(evt.from_id) not in allowed_user:
        log.info(f'user {evt.from_id} not allowed to use this bot')
        return
    if not evt.file:
        log.info('not evt.file')
        return

    try:
        ret = get_media_meta(evt.media)
        if ret[0] and ret[1] and ret[2] <= max_file_size:
            middle_x = StringCoder.encode(f"{evt.chat_id}|{evt.id}|{1 if evt.is_group else 0}|{1 if evt.is_channel else 0}")
            log.debug(f"{evt.chat_id}|{evt.id}|{1 if evt.is_group else 0}|{1 if evt.is_channel else 0}")
            # url = public_url / str(pack_id(evt)) / get_file_name(evt)
            url = public_url / middle_x / get_file_name(evt)
            await evt.reply(f'[{url}]({url})')
            log.debug(f'Link to {evt.id} in {evt.chat_id}: {url}')
        else:
            if admin_id == evt.from_id and ret[0]:
                middle_x = StringCoder.encode(f"{evt.chat_id}|{evt.id}|{1 if evt.is_group else 0}|{1 if evt.is_channel else 0}")
                log.debug(f"{evt.chat_id}|{evt.id}|{1 if evt.is_group else 0}|{1 if evt.is_channel else 0}")
                # url = public_url / str(pack_id(evt)) / get_file_name(evt)
                url = public_url / middle_x / get_file_name(evt)
                await evt.reply(f'[{url}]({url})')
                log.debug(f'Link to {evt.id} in {evt.chat_id}: {url}')
    except Exception as exp:
        await evt.reply(str(exp))
        pass

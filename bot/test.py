import asyncio
from telethon import TelegramClient, sync, events

# Use your own values from my.telegram.org
api_id = 15723016
api_hash = 'fd10c198eaa94bc4fe3f82415eb46ee6'
client = TelegramClient('Pulchrum', api_id, api_hash, system_version="4.16.30-vxASPA")

async with client:
    async for dialog in client.iter_dialogs():
        if dialog.is_channel:
            # print(dialog)
            print(f'{dialog.id}:{dialog.title}')
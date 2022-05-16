from dotenv import load_dotenv,find_dotenv
from pyrogram import Client
from pyrogram.enums import ChatType
from os import environ
from pyrogram.errors import MessageIdInvalid
import logging
import asyncio

logging.basicConfig(encoding='utf-8', level=logging.DEBUG,
                    format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


async def select_group():
    try:
        groups = []
        async for dialog in app.get_dialogs():
            if dialog.chat.type == ChatType.SUPERGROUP:
                groups.append(dialog)
        for index,group in enumerate(groups):
            name_group = group.chat.title
            t = f'[{index}] {name_group}'
            print(t)
        num_group = int(input('Select group: '))
        return groups[num_group]
    except Exception as e:
        logging.exception(f'Something went wrong {e}')
        input()
        exit(1)


async def get_last_msgids(chat:str, limit:int):
    history = app.get_chat_history(chat_id=chat, limit=limit)
    msgids = []
    async for msg in history:
        msgid = msg.id
        msgids.append(str(msgid))
    return msgids

async def reactions(chat:int, msgid:int, chat_name:str, emojis:str):
    count_wheel = 5
    lapota = f'[{chat_name}/{msgid}]'
    logging.info(f'{lapota} start task')
    for _ in range(count_wheel):
        for emoji in emojis:
            if emoji == '\ufe0f': continue
            try:
                await app.send_reaction(chat_id = chat,
                                message_id = msgid,
                                emoji = emoji)
                logging.info(f'{lapota} put reaction, sleep...')
            except MessageIdInvalid:
                logging.exception('Something went wrong with indentificator message')
            except Exception as e:
                logging.exception(f'{lapota} Something went wrong {e}')
            await asyncio.sleep(1.4)
        logging.info(f'{lapota} put all reactions, sleep...')
        await asyncio.sleep(3)
    logging.info(f'{lapota} complete {count_wheel} cycles, complete the task')

async def main():
    try:
        last_msg = int(input('Enter the last count messages (1-6): '))
        assert last_msg > 0 and last_msg <= 6
    except:
        logging.exception('Enter of 1 to 6')
        input()
        exit(1)
    async with app:
        emojis = environ.get('emojis')
        logging.info('Start scanning groups, please wait...')
        selected_chat = await select_group()
        chat = int(selected_chat.chat.id)
        name_chat = selected_chat.chat.title
        logging.info(f'[{name_chat}] Start auto reaction on {last_msg} the last messages')
        while True:
            try:
                ids_msg = await get_last_msgids(chat, last_msg)
                tasks = []
                for msgid in ids_msg:
                    task = asyncio.ensure_future(reactions(chat, int(msgid), name_chat, emojis))
                    tasks.append(task)
                    await asyncio.sleep(1)
                await asyncio.wait(tasks)
            except Exception as e:
                logging.exception(f'Something went wrong {e}')

if __name__ == '__main__':
    dotenv_file = find_dotenv()
    load_dotenv(dotenv_file)
    api_hash = environ.get('api_hash')
    api_id = environ.get('api_id')

    path_session = r'./session'
    app = Client(
                path_session,
                api_id=api_id,
                api_hash=api_hash
            )
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())

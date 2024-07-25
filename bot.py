import logging
import aiohttp
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from bs4 import BeautifulSoup
import json
import os

API_TOKEN = '7273240656:AAHf4w5fsQfB9vC43ty6f0X7SYw2nuxu2nY'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


async def fetch_latest_post(recording):
    async with aiohttp.ClientSession() as session:
        async with session.get(recording['url']) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                posts = soup.find_all('div', class_='items-i')
                posts = ['https://bina.az' + post.find('a').get('href') + '\n' for post in posts]
                
                data_path = rf'data/{recording["username"]}_{recording["chat_id"]}.json'
                
                with open(data_path, 'r') as f:
    
                    data = json.load(f)

                    diff = list(set(posts) - set(data['posts']))
                    
                    if diff:
                        for item in diff:
                            data['posts'].append(item)
                        
                                    
                with open(data_path, 'w') as f:
                    json.dump(data, f, indent=4)
                                    
                return diff
                
            else:
                logging.error(f"Failed to fetch {recording['url']} with status {response.status}")
                return None


@dp.message_handler(commands=["quit"])
async def quit_(message: types.Message):

    chat_id = message.chat.id
    username = message.from_user.username

    path_for_del = rf'data/{username}_{chat_id}.json'

    if os.path.exists(path_for_del):
        os.remove(path_for_del)

    await message.reply("Bot deaktiv edildi!")



# Start
@dp.message_handler(commands=["start"])
async def start_(message: types.Message):
    url = message.get_args()
    
    if url == '':
        await message.reply("strat komandası ilə url'i daxil edin")
    else:
        chat_id = message.chat.id
        username = message.from_user.username
        recording = {'username': username,
                     'chat_id': chat_id,
                     'posts': [], 
                     'url': url}
        
        data_path = rf'data/{username}_{chat_id}.json'
        
        if not os.path.exists(data_path):
            with open(data_path, 'w') as f:
                json.dump(recording, f, indent=4)
        else:
            with open(data_path, 'r') as f:
                user_data = json.load(f)
                print(user_data)                   ######
                user_data['url'] = url
            with open(data_path, 'w') as f:
                json.dump(user_data, f, indent=4)

        
        
        await message.reply("Bot aktivdir! Monitorinq başladı!")
        
        
        while True:
            if url:
                for user_file in os.listdir('data'):
                    with open(rf'data/{user_file}', 'r') as f:
                        rec = json.load(f)

                    new_posts = await fetch_latest_post(rec)

                    if new_posts:
                        new_posts = ['• ' + i.strip('\n') for i in new_posts]
                        
                        formatted_string = '\n'.join(new_posts)
                        
                        await bot.send_message(chat_id=rec['chat_id'], text=f"Yeni evler: \n\n{formatted_string}")
                        
                await asyncio.sleep(60)
    

if __name__ == '__main__':
    from aiogram.contrib.middlewares.logging import LoggingMiddleware
    dp.middleware.setup(LoggingMiddleware())
    executor.start_polling(dp)

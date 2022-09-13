import ploupy
import os
from dotenv import load_dotenv

from src.behaviour import BotBehaviour

load_dotenv()

BOT_KEY = os.environ["PROD_BOT_KEY2"]

bot = ploupy.Bot(bot_key=BOT_KEY, behaviour_class=BotBehaviour)

if __name__ == "__main__":
    bot.run()

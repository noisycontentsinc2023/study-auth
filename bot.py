import discord
import bs4
import asyncio
import os
import urllib
from discord import Embed
from discord.ext import tasks, commands
from discord.utils import get
from urllib.request import Request

naver_client_id = 'iuWr9aAAyKxNnRsRSQIt'
naver_client_secret = 'bkfPugeyIa'


TOKEN = os.environ['TOKEN']
PREFIX = os.environ['PREFIX']

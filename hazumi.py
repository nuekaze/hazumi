import discord

import transformers
from transformers import utils, pipeline, set_seed
import torch

import threading
import time
import asyncio
import re

TOKEN = ''
MY_NAME = 'Hazumi'
MODEL_NAME = "facebook/opt-125m"
CHANNEL = 0000000000000000000

history = open("history.txt", 'r').readlines()
history = list(map(str.strip, history))

intents = discord.Intents.none()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

generator = pipeline('text-generation',
                     model=MODEL_NAME,
                     do_sample=True,
                     max_new_tokens=100,
                     torch_dtype=torch.float)

channel = None

async def send_message(message):
  await channel.send(message)

def remove_emotes(message):
    words = message.split(' ')
    new = []
    for w in words:
        if re.search("<:(.)*:([0-9])*>", w) or re.search("<a:(.)*:([0-9]*>)", w):
            new.append(w.split(':')[1])
        else:
            new.append(w)
    return ' '.join(new)

def make_response():
    global history
    global wait
    while 1:
        if wait:
            input_text = "\n".join(history)
            set_seed(32)
            response = generator(input_text,
                                 num_beams=1, 
                                 num_return_sequences=1
                                 )[0]['generated_text']

            try:
                #print('\n'+'\n'.join(response.split('\n')[len(history):len(history)+6])+'\n')
                response = response.split('\n')[len(history):len(history)+6]
                for i in range(5):
                    if response[i].split(': ')[0] == MY_NAME and "http" not in response[i].split(': ')[1]:
                        asyncio.run_coroutine_threadsafe(send_message(response[i].split(': ')[1]), client.loop)
                        if response[i+1].split(': ')[0] == MY_NAME and "http" not in response[i+1].split(': ')[1]:
                            time.sleep(2)
                            asyncio.run_coroutine_threadsafe(send_message(response[i+1].split(': ')[1]), client.loop)
                        break
            except IndexError:
                pass

            wait = 0

        time.sleep(5)
            
wait = 0

@client.event
async def on_message(ctx):
    global history
    global wait
    global channel
    if ctx.channel.id == CHANNEL and "http" not in ctx.content:
        message = remove_emotes(ctx.content)
        channel = ctx.channel
        history.append("%s: %s" % (str(ctx.author).split('#')[0], message))
        if len(history) > 100:
            history = history[100:]
        open("history.txt", 'a').write("%s: %s\n" % (str(ctx.author).split('#')[0], message))
        print("%s: %s" % (str(ctx.author).split('#')[0], message))
        if wait == 0 and "%s" % str(ctx.author).split('#')[0] != MY_NAME:
            wait = 1

responder_thread = threading.Thread(target=make_response)
responder_thread.start()
client.run(TOKEN)

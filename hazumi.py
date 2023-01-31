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

next_force_response = 5
force_response = 0

def make_response():
    global history
    global wait
    global next_force_response
    global force_response
    while 1:
        if wait:
            input_text = "\n".join(history)
            set_seed(32)
            response = generator(input_text,
                                num_beams=1, 
                                num_return_sequences=1
                                )[0]['generated_text']

            try:
                response = response.split('\n')[len(history):len(history)+6]
                for i in range(5):
                    if response[i].split(': ')[0] == MY_NAME and "http" not in response[i].split(': ')[1]:
                        asyncio.run_coroutine_threadsafe(
                                send_message(response[i].split(': ')[1]), client.loop)
                        
                        next_force_response = random.randint(3, 10)
                        force_response = 0

                        if response[i+1].split(': ')[0] == MY_NAME and "http" not in response[i+1].split(': ')[1]:
                            time.sleep(2)
                            asyncio.run_coroutine_threadsafe(
                                    send_message(response[i+1].split(': ')[1]), client.loop)
                        break

                if force_response >= next_force_response:
                    if "http" not in response[0].split(': ')[1] and "Hazuki" not in response[0].split(': ')[1]:
                        asyncio.run_coroutine_threadsafe(
                                send_message(response[0].split(': ')[1]), client.loop)
                    force_response = 0
                    next_force_response = random.randint(3, 10)
                    
                else:
                    force_response += 1

            except IndexError:
                pass

            wait = 0

        time.sleep(3)
            
wait = 0

@client.event
async def on_message(ctx):
    global history
    global wait
    global channel
    
    if ctx.channel.id == CHANNEL and "http" not in ctx.content:
        message = remove_emotes(ctx.content)
        channel = ctx.channel
        author = str(ctx.author).split('#')[0]

        history.append("%s: %s" % (author, message))
        open("history.txt", 'a').write("%s: %s\n" % (author, message))
        history = history[-100:]

        print("%s: %s" % (author, message))

        if wait == 0 and "%s" % author != MY_NAME:
            wait = 1

responder_thread = threading.Thread(target=make_response)
responder_thread.start()
client.run(TOKEN)

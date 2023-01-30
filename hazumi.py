import discord

import transformers
from transformers import utils, pipeline, set_seed
import torch

TOKEN = '' # Discord bot token.
MY_NAME = 'Hazuki#0000' # Discord bot user ID.
CHANNEL = 0000000000000000000 # Discord channel to read messages from.

HISTORY_LENGTH = 100 # The amount of history the bot will remember.
history = open("history.txt", 'r').readlines()
history = list(map(str.strip, history))

intents = discord.Intents.none()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

MODEL_NAME = "facebook/opt-125m"
generator = pipeline('text-generation',
                     model=MODEL_NAME,
                     do_sample=True,
                     torch_dtype=torch.float)

def make_response():
    global history
    input_text = "\n".join(history)
    set_seed(32)
    response = generator(input_text,
                         max_length=len(input_text)+100/2.6,
                         num_beams=1, 
                         num_return_sequences=1
                         )[0]['generated_text']
    
    # Just generate some future chat and pick whatever Hazumi would have said and return it.
    response = response.split('\n')[len(history):len(history)+5]
    #print(response)
    for r in response:
        if r.split(': ')[0] == MY_NAME:
            return r.split(': ')[1]

    return None
            
wait = 0

@client.event
async def on_message(ctx):
    global history
    global wait
    if ctx.channel.id == CHANNEL:
        history.append("%s: %s" % (ctx.author, ctx.content))
        if len(history) > HISTORY_LENGTH:
            history = history[HISTORY_LENGTH:]
            
        open("history.txt", 'a').write("%s: %s\n" % (ctx.author, ctx.content)) # Save history on the go.
        #print("%s: %s" % (ctx.author, ctx.content))
        
        if wait == 0 and "%s" % ctx.author != MY_NAME: # Don't try respond to new messages if we are already working out a response.
            wait = 1
            # This will probably need to go into its own thread at some point. It hangs the Discord connection until a resonse is made.
            response = make_response()

            if response:
                #print(response)
                #print(ctx.channel)
                await ctx.channel.send(response)
        wait = 0

client.run(TOKEN)

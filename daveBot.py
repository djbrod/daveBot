#!/usr/bin/python3
import json
import os
import sys

import discord
from discord.ext import commands

jsonKey = 'queue'
filename = 'queue.json'
daveBotCommandPrefix = '!'


def get_empty_json():
    return {jsonKey: []}


def load_student_queue():
    file_json_data = get_empty_json()

    if os.path.exists(filename):
        with open(filename) as f:
            file_json_data = json.load(f)

    return file_json_data


def save_student_queue(obj):
    if not isinstance(obj, dict):
        print("Please check type of object - should be of type 'dict'", file=sys.stderr)
    else:
        if jsonKey not in obj.keys():
            print("Please check type of object being saved, should include json 'key' for the queue", file=sys.stderr)
        else:
            with open(filename, 'w') as outfile:
                json.dump(obj, outfile, indent=4)


# Create Discord Bot
client = commands.Bot(command_prefix=daveBotCommandPrefix)


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await client.change_presence(status=discord.Status.online,
                                 activity=discord.Activity(type=discord.ActivityType.listening, name='your commands'))


@client.command(help='Add yourself to the queue for office hours')
async def joinQ(ctx):
    await ctx.channel.purge(limit=1)

    student_name = ctx.author.display_name

    queue_json = load_student_queue()
    student_queue = queue_json[jsonKey]

    if student_name in student_queue:
        await ctx.send(f'{student_name}, you\'re already in the queue knucklehead!')
    else:
        student_queue_position = len(queue_json[jsonKey]) + 1
        await ctx.send(f'{student_name} is \\#{student_queue_position} in line')
        student_queue.append(student_name)
        save_student_queue(queue_json)


@client.command(help='Dequeue the next student', hidden=True)
@commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def whosNext(ctx):
    await ctx.channel.purge(limit=1)

    msg = 'Now serving:\t'
    embed = discord.Embed(title="Now Serving:")

    queue_json = load_student_queue()
    student_queue = queue_json[jsonKey]

    if len(student_queue) > 0:
        msg += student_queue[0]
        embed.add_field(name='\U0001F9D1\u200D\U0001F393', value=student_queue[0], inline=True)
        student_queue.pop(0)
        save_student_queue(queue_json)

    await ctx.send(embed=embed)


# @client.command()
# async def clear(ctx, amount=5):
#    await ctx.channel.purge(limit=amount)

@client.command(help='Clears the queue', hidden=True)
@commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def imDone(ctx):
    await ctx.channel.purge(limit=1)
    await ctx.send('You don\'t have to go home but you can\'t stay here. Dave quits.')
    save_student_queue(get_empty_json())


@client.command(help='Displays the queue')
async def whosHere(ctx):
    await ctx.channel.purge(limit=1)
    embed = discord.Embed(title="These are the people in your neighborhood:")

    queue_json = load_student_queue()
    if jsonKey in queue_json:
        student_queue = queue_json[jsonKey]
    else:
        student_queue = []

    if len(student_queue) > 0:
        msg = ''
        for qPos in range(len(student_queue)):
            msg = msg + str(qPos + 1) + '. ' + student_queue[qPos] + '\n'
    else:
        msg = 'Nobody! :) Join the voice channel'

    embed.add_field(name='\U0001F393', value=msg, inline=False)

    await ctx.send(embed=embed)


@client.command(help='Remove yourself from the queue')
async def leaveQ(ctx):
    await ctx.channel.purge(limit=1)

    student_name = ctx.author.display_name

    msg = 'Peace out shorty!\t @' + student_name

    queue_json = load_student_queue()
    student_queue = queue_json[jsonKey]

    if student_name in student_queue:
        student_queue.remove(student_name)
        await ctx.send(msg)
        save_student_queue(queue_json)
    else:
        await ctx.send(f'{student_name}, you\'re not in the queue yet knucklehead!')


@client.command(help='Poll for pain faces', hidden=True)
async def pollFaces(ctx):
    await ctx.channel.purge(limit=1)
    msg = await ctx.send(file=discord.File('scaleFaces.png'))
    await msg.add_reaction('\u0030\uFE0F\u20E3')  # add 0
    await msg.add_reaction('\u0031\uFE0F\u20E3')  # add 1
    await msg.add_reaction('\u0032\uFE0F\u20E3')  # add 2
    await msg.add_reaction('\u0033\uFE0F\u20E3')  # add 3
    await msg.add_reaction('\u0034\uFE0F\u20E3')  # add 4
    await msg.add_reaction('\u0035\uFE0F\u20E3')  # add 5


@client.command(help='Poll for Questions, Answers, Ice Cream?', hidden=True)
async def pollQAI(ctx):
    await ctx.channel.purge(limit=1)

    embed = discord.Embed(title="Poll")
    embed.add_field(name='\u2754', value="Questions?", inline=True)
    embed.add_field(name='\U0001F4A1', value="Answers?", inline=True)
    embed.add_field(name='\U0001F366', value="Ice Cream?", inline=True)
    msg = await ctx.send(embed=embed)

    await msg.add_reaction('\u2754')  # add question mark
    await msg.add_reaction('\U0001F4A1')  # add light bulb
    await msg.add_reaction('\U0001F366')  # add ice cream


discordKey = os.getenv("DAVEBOT")
client.run(discordKey)

# generic poll command
# multiple servers aka peterBot

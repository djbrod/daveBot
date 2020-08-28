#!/usr/bin/python3

import json
import os
import sys
import re
import random
import datetime

import discord
from discord.ext import commands

daveBotCommandPrefix = '!'


def get_sanitized_identifier(string_to_sanitize):
    pattern = re.compile('[\W_]+')
    return pattern.sub('', string_to_sanitize)


def get_empty_json(keyName):
    return {keyName: []}


# noinspection PyShadowingNames
def get_server_queue(ctx):
    name_of_queue = get_sanitized_identifier(ctx.channel.guild.name)
    all_queues = load_queue()
    if name_of_queue in all_queues:
        return all_queues[name_of_queue]
    else:
        return []


# noinspection PyShadowingNames
def update_server_queue(ctx, queue):
    name_of_queue = get_sanitized_identifier(ctx.channel.guild.name)
    all_queues = load_queue()
    all_queues[name_of_queue] = queue
    save_queue(all_queues)


def load_json(data_type, default):
    file_json_data = default

    if os.path.exists(data_type + '.json'):
        with open(data_type + '.json') as f:
            file_json_data = json.load(f)

    return file_json_data


def save_json(data_type, obj):
    if not isinstance(obj, dict):
        print("Please check type of object - should be of type 'dict'", file=sys.stderr)
    else:
        with open(data_type + '.json', 'w') as outfile:
            json.dump(obj, outfile, indent=4)


def save_queue(obj):
    save_json('queue', obj)


def load_queue():
    return load_json('queue', get_empty_json('queue'))


def save_roll(obj):
    save_json('roll', obj)


def load_roll():
    return load_json('roll', get_empty_json('roll'))


def save_bingo(obj):
    save_json('bingo', obj)


def load_bingo():
    return load_json('bingo', get_empty_json('bingo'))


# Create Discord Bot
client = commands.Bot(command_prefix=daveBotCommandPrefix)


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await client.change_presence(status=discord.Status.online,
                                 activity=discord.Activity(type=discord.ActivityType.listening, name='your commands'))

    all_queues = load_queue()

    for guild in client.guilds:
        sanitized_name = get_sanitized_identifier(guild.name)
        queue_found = False
        for queue in all_queues:
            if sanitized_name in queue:
                queue_found = True

        if not queue_found:
            all_queues[sanitized_name] = []
            print("Adding a server:" + sanitized_name)

    save_queue(all_queues)


@client.command(help='Add yourself to the queue for office hours')
async def joinQ(ctx):
    await ctx.channel.purge(limit=1)

    student_name = ctx.author.display_name
    student_queue = get_server_queue(ctx)

    if student_name in student_queue:
        await ctx.send(f'{student_name}, you\'re already in the queue knucklehead!')
    else:
        student_queue_position = len(student_queue) + 1
        await ctx.send(f'{student_name} is \\#{student_queue_position} in line')
        student_queue.append(student_name)
        update_server_queue(ctx, student_queue)


@client.command(help='Dequeue the next student', hidden=True)
@commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def whosNext(ctx):
    await ctx.channel.purge(limit=1)

    msg = 'Now serving:\t'
    embed = discord.Embed(title="Now Serving:")

    student_queue = get_server_queue(ctx)

    if len(student_queue) > 0:
        msg += student_queue[0]
        embed.add_field(name='\U0001F9D1\u200D\U0001F393', value=student_queue[0], inline=True)
        student_queue.pop(0)
        update_server_queue(ctx, student_queue)

    await ctx.send(embed=embed)


@client.command(help='Clears a number of previous messages', hidden=True)
@commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount + 1)


@client.command(help='Clears the queue', hidden=True)
@commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def imDone(ctx):
    await ctx.channel.purge(limit=1)
    await ctx.send('You don\'t have to go home but you can\'t stay here. Dave quits.')
    update_server_queue(ctx, [])


@client.command(help='Displays the queue')
async def whosHere(ctx):
    await ctx.channel.purge(limit=1)
    embed = discord.Embed(title="These are the people in your neighborhood:")

    student_queue = get_server_queue(ctx)
    if len(student_queue) > 0:
        msg = ''
        for qPos in range(len(student_queue)):
            msg = msg + str(qPos + 1) + '. ' + student_queue[qPos] + '\n'
    else:
        msg = 'Nobody in ' + ctx.channel.guild.name + '! :) Join the voice channel'

    embed.add_field(name='\U0001F393', value=msg, inline=False)

    await ctx.send(embed=embed)


@client.command(help='Remove yourself from the queue')
async def leaveQ(ctx):
    await ctx.channel.purge(limit=1)

    student_name = ctx.author.display_name

    msg = 'Peace out shorty!\t @' + student_name

    student_queue = get_server_queue(ctx)

    if student_name in student_queue:
        student_queue.remove(student_name)
        await ctx.send(msg)
        update_server_queue(ctx, student_queue)
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


@client.command(help='Banish students to breakout rooms.', hidden=True)
@commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def breakout(ctx, numberOfRooms=3):
    await ctx.channel.purge(limit=1)

    breakouts = []
    breakoutCategory = await ctx.guild.create_category('Breakout Rooms')
    for roomNumber in range(numberOfRooms):
        breakouts.append(await ctx.guild.create_voice_channel('Breakout', category=breakoutCategory))

    channels = [channel for channel in client.get_all_channels() if
                (channel.name == 'Classroom') & (channel.guild.name == ctx.guild.name)]
    classroomMembers = [member for member in channels[0].members if
                        "professor" not in [role.name for role in member.roles]]
    random.shuffle(classroomMembers)
    for memberNumber in range(len(classroomMembers)):
        await classroomMembers[memberNumber].move_to(breakouts[memberNumber % numberOfRooms])


@client.command(help='Remove breakout rooms and breakout room category ', hidden=True)
@commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def cleanBreakouts(ctx):
    await ctx.channel.purge(limit=1)

    breakouts = [channel for channel in client.get_all_channels() if
                 (channel.name == 'Breakout') & (channel.guild.name == ctx.guild.name)]
    for room in breakouts:
        await room.delete()

    breakoutCategory = [category for category in ctx.guild.categories if
                        (category.name == 'Breakout Rooms') & (category.guild.name == ctx.guild.name)]
    for category in breakoutCategory:
        await category.delete()


@client.command(help='Call students back from breakout rooms', hidden=True)
@commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def callBack(ctx):
    await ctx.channel.purge(limit=1)

    channels = [channel for channel in client.get_all_channels() if
                (channel.name == 'Classroom') & (channel.guild.name == ctx.guild.name)]
    classroom = channels[0]

    breakouts = [channel for channel in client.get_all_channels() if
                 (channel.name == 'Breakout') & (channel.guild.name == ctx.guild.name)]
    for room in breakouts:
        for member in room.members:
            await member.move_to(classroom)

    await cleanBreakouts(ctx)


@client.command(help='Record roll from Classroom Voice Channel', hidden=True)
@commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def callRoll(ctx, course=None):
    await ctx.channel.purge(limit=1)
    if course is None:
        course = ctx.guild.name
    course = course.upper()

    roll = load_roll()
    if course not in roll.keys():
        # noinspection PyTypeChecker
        roll[course] = {}

    channels = [channel for channel in client.get_all_channels() if
                (channel.name == 'Classroom') & (channel.guild.name == ctx.guild.name)]
    classroomMembers = [member for member in channels[0].members if
                        "professor" not in [role.name for role in member.roles]]
    for member in classroomMembers:
        if member.name not in roll[course].keys():
            roll[course][member.name] = []
        if str(datetime.date.today()) not in roll[course][member.name]:
            roll[course][member.name].append(str(datetime.date.today()))
    save_roll(roll)


@client.command(help='Randomly choose one student from the Classroom', hidden=True)
@commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def bingo(ctx):
    await ctx.channel.purge(limit=1)

    channels = [channel for channel in client.get_all_channels() if
                (channel.name == 'Classroom') & (channel.guild.name == ctx.guild.name)]
    classroomMembers = [member.name for member in channels[0].members if
                        "professor" not in [role.name for role in member.roles]]

    previously_asked = load_bingo()

    still_not_asked = list(set(classroomMembers)-set(previously_asked['bingo']))

    if len(still_not_asked) > 0:
        the_chosen_one = random.choice(still_not_asked)
        previously_asked['bingo'].append(the_chosen_one)
        save_bingo(previously_asked)

        msg = await ctx.send(f'Tag, {the_chosen_one}, you\'re it!')
        await msg.add_reaction('\U0001F929')  # add star struck
    else:
        await ctx.send(f'No one left in the classroom to ask!')
        save_bingo(get_empty_json('bingo'))


@client.command(help='Clear the persisted bingo list', hidden=True)
@commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def bingoClear(ctx):
    await ctx.channel.purge(limit=1)
    save_bingo(get_empty_json('bingo'))

discordKey = os.getenv("DAVEBOT")
client.run(discordKey)

# generic poll command
# queue metrics

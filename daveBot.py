#!/usr/bin/python3

import datetime
import random
import discord
from utilities.general import *

daveBotCommandPrefix = '!'

# Create Discord Bot
client = commands.Bot(command_prefix=daveBotCommandPrefix)


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await client.change_presence(status=discord.Status.online,
                                 activity=discord.Activity(type=discord.ActivityType.listening, name='your commands'))

    server_store = load_server_store()

    for guild in client.guilds:
        name_of_queue = get_sanitized_identifier(guild.name)

        queue_found = False
        for queue in server_store:
            if name_of_queue in queue:
                queue_found = True

        if not queue_found:
            server_store[name_of_queue] = []
            print(f"Adding Server: '{name_of_queue}' to Server Store")

    save_server_store(server_store)


@client.command(help='Add yourself to the queue for office hours')
async def joinQ(ctx: commands.Context):
    await ctx.message.delete()
    # await ctx.channel.purge(limit=1)

    student_name = ctx.author.display_name
    student_queue = get_server_queue(ctx)

    if student_name in student_queue:
        await ctx.send(f'<@{ctx.author.id}>, you\'re already in the queue knucklehead!')
    else:
        position_in_queue = len(student_queue) + 1
        await ctx.send(f'<@{ctx.author.id}> is \\#{position_in_queue} in line')

        student_queue.append(student_name)
        update_server_queue(ctx, student_queue)


@client.command(help='Dequeue the next student', hidden=True)
@commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def whosNext(ctx: commands.Context):
    await ctx.message.delete()
    # await ctx.channel.purge(limit=1)

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
async def clear(ctx: commands.Context, amount=5):
    await ctx.channel.purge(limit=amount + 1)


@client.command(help='Clears the queue', hidden=True)
@commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def imDone(ctx: commands.Context):
    await ctx.message.delete()
    # await ctx.channel.purge(limit=1)
    await ctx.send('You don\'t have to go home but you can\'t stay here. Dave quits.')
    update_server_queue(ctx, [])


@client.command(help='Displays the queue')
async def whosHere(ctx: commands.Context):
    await ctx.message.delete()
    # await ctx.channel.purge(limit=1)
    embed = discord.Embed(title="These are the people in your neighborhood:")

    student_queue = get_server_queue(ctx)
    if len(student_queue) > 0:
        msg = ""
        for index in range(len(student_queue)):
            student_name = student_queue[index]
            msg += f"{index + 1}. {student_name}\n"
    else:
        msg = f"Nobody in {ctx.channel.guild.name}! :) Join the voice channel"

    embed.add_field(name='\U0001F393', value=msg, inline=False)

    await ctx.send(embed=embed)


@client.command(help='Remove yourself from the queue')
async def leaveQ(ctx: commands.Context):
    await ctx.message.delete()
    # await ctx.channel.purge(limit=1)

    student_name = ctx.author.display_name

    msg = f'Peace out shorty!\t <@{ctx.author.id}>'

    student_queue = get_server_queue(ctx)

    if student_name in student_queue:
        student_queue.remove(student_name)
        await ctx.send(msg)
        update_server_queue(ctx, student_queue)
    else:
        await ctx.send(f'<@{ctx.author.id}>, you\'re not in the queue yet knucklehead!')


@client.command(help='Poll for pain faces', hidden=True)
async def pollFaces(ctx: commands.Context):
    await ctx.message.delete()
    # await ctx.channel.purge(limit=1)
    msg = await ctx.send(file=discord.File('scaleFaces.png'))
    await msg.add_reaction('\u0030\uFE0F\u20E3')  # add 0
    await msg.add_reaction('\u0031\uFE0F\u20E3')  # add 1
    await msg.add_reaction('\u0032\uFE0F\u20E3')  # add 2
    await msg.add_reaction('\u0033\uFE0F\u20E3')  # add 3
    await msg.add_reaction('\u0034\uFE0F\u20E3')  # add 4
    await msg.add_reaction('\u0035\uFE0F\u20E3')  # add 5


@client.command(help='Poll for Questions, Answers, Ice Cream?', hidden=True)
async def pollQAI(ctx: commands.Context):
    await ctx.message.delete()
    # await ctx.channel.purge(limit=1)

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
async def breakout(ctx: commands.Context, numberOfRooms=3):
    await ctx.message.delete()
    # await ctx.channel.purge(limit=1)

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
async def cleanBreakouts(ctx: commands.Context):
    await ctx.message.delete()
    # await ctx.channel.purge(limit=1)

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
async def callBack(ctx: commands.Context):
    await ctx.message.delete()
    # await ctx.channel.purge(limit=1)

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
async def callRoll(ctx: commands.Context, course=None):
    await ctx.message.delete()
    # await ctx.channel.purge(limit=1)

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
async def bingo(ctx: commands.Context):
    await ctx.message.delete()
    # await ctx.channel.purge(limit=1)

    channels = [channel for channel in client.get_all_channels() if
                (channel.name == 'Classroom') & (channel.guild.name == ctx.guild.name)]

    classroomMembers = [member.display_name for member in channels[0].members if
                        "professor" not in [role.name for role in member.roles]]

    previously_asked = load_bingo()

    still_not_asked = list(set(classroomMembers) - set(previously_asked['bingo']))

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
async def bingoClear(ctx: commands.Context):
    await ctx.message.delete()
    # await ctx.channel.purge(limit=1)
    save_bingo(get_empty_json('bingo'))


discordKey = os.getenv("DAVEBOT")
client.run(discordKey)

# generic poll command
# queue metrics

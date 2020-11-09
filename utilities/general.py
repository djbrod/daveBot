import json
import os
import re
import sys

from discord.ext import commands

_mentionRegex = re.compile(r"^<@(?P<msgSyntax>[!#&]?)(?P<memberId>\d+)>$")


def get_member_id(name: str):
    mention_match = _mentionRegex.search(name)

    member_id = None

    if mention_match is not None:
        match_dict = mention_match.groupdict()
        member_id = int(match_dict['memberId'])

    return member_id


def get_sanitized_identifier(string_to_sanitize: str):
    pattern = re.compile(r"[\W_]+")
    return pattern.sub('', string_to_sanitize)


def get_empty_json(keyName: str):
    return {keyName: []}


def get_server_queue(ctx: commands.Context):
    name_of_queue = get_sanitized_identifier(ctx.channel.guild.name)

    server_store = load_server_store()

    if name_of_queue in server_store:
        return server_store[name_of_queue]
    else:
        return []


def update_server_queue(ctx: commands.Context, queue: list):
    name_of_queue = get_sanitized_identifier(ctx.channel.guild.name)

    server_store = load_server_store()
    server_store[name_of_queue] = queue

    save_server_store(server_store)


def load_json_from_file(file_name: str, default_value: dict):
    file_json_data = default_value

    complete_file_name = file_name + '.json'

    if os.path.exists(complete_file_name):
        with open(complete_file_name) as f:
            file_json_data = json.load(f)

    return file_json_data


def save_json_to_file(file_name: str, data: dict):
    if not isinstance(data, dict):
        print("Please check type of object - should be of type 'dict'", file=sys.stderr)
    else:
        with open(file_name + '.json', 'w') as outfile:
            json.dump(data, outfile, indent=4)


def _save_data(file_name: str, data: dict):
    save_json_to_file(file_name, data)


def _load_data(file_name: str):
    return load_json_from_file(file_name, get_empty_json(file_name))


def save_server_store(data: dict):
    _save_data(file_name='queue', data=data)


def load_server_store():
    return _load_data('queue')


def save_roll(data: dict):
    _save_data('role', data)


def load_roll():
    return _load_data('roll')


def save_bingo(data: dict):
    _save_data('bingo', data)


def load_bingo():
    return _load_data('bingo')

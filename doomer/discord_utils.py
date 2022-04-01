import datetime
import re

from doomer import settings
import discord


def is_number_str(string):
    return bool(re.match("^\\d+$", string))


def set_if_not_set(dick, attr, val):
    if attr not in dick:
        dick[attr] = val
    return dick


def get_nick(obj):
    if hasattr(obj, "nick") and obj.nick is not None:
        return obj.nick
    else:
        return obj.name


async def send_message(ctx, messageObj):
    message = insert_emoji(ctx.guild, str(messageObj))
    messages = [message[i : i + 2000] for i in range(0, len(message), 2000)]
    for m in messages:
        await ctx.send(m)


async def get_channel(ctx, channel_name):
    try:
        channel = next(
            filter(lambda c: channel_name in c.name, ctx.guild.text_channels)
        )
        return channel
    except StopIteration:
        await send_message(ctx, "Channel `" + channel_name + "` does not exist")
        return None


async def not_a_number(ctx, n):
    return await ctx.send("You think `" + n + "` is a number, you dumb idiot?")


def format_messages(messages, emoji_names=True, emphasize_names=True):
    pre = ""
    post = ""
    if emphasize_names:
        pre = "**["
        post = "]**"

    return "\n".join(
        map(
            lambda msg: pre
            + msg.created_at.strftime("%I:%M:%S %p")
            + " "
            + get_nick(msg.author)
            + post
            + ": "
            + fix_emoji(msg.clean_content)
            + get_emoji_strings(msg, emoji_names),  # + format_embeds(msg),
            messages,
        )
    )


def get_emoji_strings(message, emoji_names=True, colons=False):
    reacts = list(
        map(
            lambda react: get_emoji_string(react.emoji, emoji_names),
            filter(lambda m: not m.me, message.reactions),
        )
    )

    if len(reacts) > 0:
        return " (" + " ".join(reacts) + ")"
    else:
        return ""


def get_emoji_string(emoji, emoji_names=True, colons=True):
    if hasattr(emoji, "name"):
        if emoji_names:
            return emoji.name
        else:
            return str(emoji.id)
    else:
        return emoji


def insert_emoji(guild, s):
    splits = s.split(":")
    with_emoji = ""
    for s in splits:
        lookup = discord.utils.get(guild.emojis, name=s)
        if lookup:
            with_emoji += "<" + ":" + lookup.name + ":" + str(lookup.id) + ">"
        else:
            with_emoji += s + ":;:"

    return with_emoji.replace(":;:<", "<").replace(":;:", ":").strip(":")


def fix_emoji(in_str):
    return re.sub(r"<(:\w+:)\d+>", "\\1", in_str)


async def get_messages(
    channel,
    num_messages,
    time=None,
    carry_messages=[],
    iteration=0,
    from_user=None,
    other_filter=None,
    filter_bot=True,
):
    if time is None:
        time = datetime.datetime.utcnow()

    num_to_fetch = 100

    raw_messages = await channel.history(
        limit=num_to_fetch, oldest_first=False, before=time
    ).flatten()
    filtered_messages = list(
        filter(
            lambda msg: (
                (not msg.author.bot or not filter_bot)
                and not msg.clean_content.startswith(settings.COMMAND_PREFIX)
            )
            and (from_user is None or from_user in msg.author.name.lower()),
            raw_messages,
        )
    )
    filtered_messages.reverse()
    if bool(other_filter):
        filtered_messages = other_filter(filtered_messages)
    new_message_count = len(filtered_messages)
    filtered_messages.extend(carry_messages)

    if (
        (num_messages - new_message_count) > 0 or new_message_count == 0
    ) and iteration < 20:
        time = raw_messages[0].created_at
        new_result = await get_messages(
            channel,
            num_messages,
            time,
            filtered_messages,
            iteration + 1,
            from_user,
            other_filter,
        )
        return new_result
    else:
        return filtered_messages[-num_messages:]


def find_questions_and_answers(input_messages):
    results = []
    preserve_next = False
    qa = []
    for message in input_messages:
        is_question = (
            bool(
                re.match(
                    "(\\?\\s)|(who)|(what)|(when)|(where)|(why)|(can (you|i|we|they))",
                    message.clean_content.lower(),
                )
            )
            or message.clean_content.endswith("?")
        )
        if preserve_next:
            qa.append(message)
            results.append(qa)
            preserve_next = False
            qa = []

        if is_question:
            preserve_next = True
            qa.append(message)

    return list(filter(lambda l: len(l) == 2, results))


def hundo_to_float(n):
    return float(n) / 100


async def handle_error(ctx, error):
    send_message(ctx, str(error))


def pythonify(json_data):

    correctedDict = {}

    for key, value in json_data.items():
        if isinstance(value, list):
            value = [
                pythonify(item) if isinstance(item, dict) else item for item in value
            ]
        elif isinstance(value, dict):
            value = pythonify(value)
        try:
            key = int(key)
        except Exception:
            pass
        correctedDict[key] = value

    return correctedDict


def curlify(request):
    command = "curl -X {method} -H {headers} -d '{data}' '{uri}'"
    method = request.method
    uri = request.url
    data = request.body
    headers = ['"{0}: {1}"'.format(k, v) for k, v in request.headers.items()]
    headers = " -H ".join(headers)
    return command.format(method=method, headers=headers, data=data, uri=uri)

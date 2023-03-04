import chatbot
from graia.ariadne.app import Ariadne
from graia.ariadne.connection.config import HttpClientConfig, WebsocketClientConfig
from graia.ariadne.connection.config import config as ConnectionConfig
from graia.ariadne.message import Source
from graia.ariadne.message.chain import MessageChain, At
from graia.ariadne.message.parser.base import MentionMe
from graia.ariadne.model import Friend, Group, Member
import asyncio
import functools
import contextvars
import requests
import re
import openai
import yaml

with open("config.yml", "r") as f:
    class Dict(dict):
        __setattr__ = dict.__setitem__
        __getattr__ = dict.__getitem__

    def Dict2Obj(dict_obj):
        if not isinstance(dict_obj, dict):
            return dict_obj
        d = Dict()
        for k, v in dict_obj.items():
            d[k] = Dict2Obj(v)
        return d
    config = Dict2Obj(yaml.safe_load(f))

openai.api_key = config.openai.api_key


# 获取百度AI access_token
def get_access_token():
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": config.baiduai.api_key,
        "client_secret": config.baiduai.secret_key
    }
    result = requests.post(url, params=params).json()
    return str(result.get("access_token"))


if config.baiduai.enable:
    access_token = get_access_token()


# 内容审核
def check_message_safe(message: str):
    if not config.baiduai.enable:
        return True  # safe
    url = "https://aip.baidubce.com/rest/2.0/solution/v1/text_censor/v2/user_defined?access_token=" + access_token

    payload = {"text": message}
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)

    if response.json().get("conclusionType") != 1:
        return False  # unsafe
    return True  # safe


async def to_thread(func, /, *args, **kwargs):
    loop = asyncio.get_running_loop()
    ctx = contextvars.copy_context()
    func_call = functools.partial(ctx.run, func, *args, **kwargs)
    return await loop.run_in_executor(None, func_call)


# 将ChatGPT返回的信息转换成MessageChain
def make_chain(message: str):
    pattern = r'@[0-9]+'

    matches = re.findall(pattern, message)
    result_list = re.split(pattern, message)

    chain = MessageChain("")
    for i in range(len(matches)):
        chain = chain + MessageChain(result_list[i])
        chain = chain + MessageChain(At(target=int(matches[i][1:])))
    chain = chain + MessageChain(result_list[len(matches)])
    return chain


if not hasattr(asyncio, 'to_thread'):
    asyncio.to_thread = to_thread

app = Ariadne(
    ConnectionConfig(
        config.mirai.qq,
        config.mirai.api_key,
        HttpClientConfig(host=config.mirai.http_url),
        WebsocketClientConfig(host=config.mirai.ws_url),
    ),
)


def sensitive_check(message):
    for x in config.sensitive_list:
        if x in message.lower():
            return True


def handle_message(bot_id, message, group_id=None, user_id=None):
    if message.strip() == '':
        return
    if sensitive_check(message):
        return "Blocked"
    if message.strip() in ["重置会话"]:
        chatbot.reset_bot(bot_id)
        return "已重置"

    if message.strip().startswith("周报:") or message.strip().startswith("周报："):
        prompt_pre = "请帮我把以下的工作内容填充为一篇完整的周报,用 markdown 格式以分点叙述的形式输出:"
        try:
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt_pre + message[3:],
                temperature=0.7,
                max_tokens=1536,
                stream=False
            )
            return response['choices'][-1]['text']
        except Exception as e:
            return "Error" + str(e)

    if group_id is None:
        response, usage = chatbot.get_bot(bot_id).ask(message)
        if sensitive_check(response) or not check_message_safe(response):
            return "Blocked"
        return response + '\n\ncost:' + str(usage.total_tokens)
    else:
        message = f"@{user_id}:{message}"
        response, usage = chatbot.get_bot(bot_id, group=True).ask(message)
        if sensitive_check(response) or not check_message_safe(response):
            return "Blocked"
        return response + '\n\ncost:' + str(usage.total_tokens)


@app.broadcast.receiver("FriendMessage")
async def on_friend_message(app: Ariadne, friend: Friend, chain: MessageChain):
    if friend.id == app.account:
        return
    response = await asyncio.to_thread(
        handle_message,
        bot_id=f"user-{friend.id}",
        message=chain.display
    )
    await app.send_message(friend, response)


@app.broadcast.receiver("GroupMessage", decorators=[MentionMe()])
async def on_group_mention_me(group: Group, member: Member, source: Source, chain: MessageChain = MentionMe()):
    # 限制启用Bot的群聊
    if len(config.group_list) and group.id not in config.group_list:
        return
    response = await asyncio.to_thread(
        handle_message,
        bot_id=f"group-{group.id}",
        group_id=group.id,
        user_id=member.id,
        message=chain.display
    )
    chain = make_chain(response)
    await app.send_message(group, chain, quote=source)


@app.broadcast.receiver("TempMessage", decorators=[MentionMe()])
async def on_temp_message(group: Group, member: Member, chain: MessageChain = MentionMe()):
    response = await asyncio.to_thread(
        handle_message,
        bot_id=f"user-{member.id}",
        message=chain.display
    )
    await app.send_message(member, response)


app.launch_blocking()


import openai
import tiktoken

ENCODER = tiktoken.get_encoding("gpt2")

bot_list = {}

GroupBotPrompt = "你是一个群聊助手，在后面的对话中会有多个人一块和你聊天，给你发的消息的开头由'@'+由数字组成的uid+':'组成，表示说话的人是哪个用户，':'后面是这个用户说的话，在用户说的话中中提到某人也是用'@'+uid表示"


def get_bot(uid: str, group: bool = False, system_prompt: str = None):
    if bot_list.get(uid, None) is None:
        if group:
            system_prompt = system_prompt or GroupBotPrompt
            bot_list[uid] = Chatbot(system_prompt=system_prompt)
        else:
            system_prompt = system_prompt or ""
            bot_list[uid] = Chatbot(system_prompt=system_prompt)

    return bot_list[uid]


def reset_bot(uid: str):
    if uid in bot_list:
        del bot_list[uid]


class Chatbot:
    def __init__(
        self,
        max_tokens: int = 4000,
        system_prompt: str = "",
    ) -> None:
        self.conversation: list = [
            {
                "role": "system",
                "content": system_prompt,
            },
        ]
        self.max_tokens = max_tokens

        initial_conversation = "\n".join([x["content"] for x in self.conversation])
        if len(ENCODER.encode(initial_conversation)) > self.max_tokens:
            raise Exception("System prompt is too long")

    def __add_to_conversation(self, message: str, role: str):
        self.conversation.append({"role": role, "content": message})

    def __truncate_conversation(self):
        while True:
            full_conversation = "\n".join([x["content"] for x in self.conversation])
            if (
                len(ENCODER.encode(full_conversation)) > self.max_tokens
                and len(self.conversation) > 1
            ):
                self.conversation.pop(1)
            else:
                break

    def ask(self, prompt: str):
        self.__add_to_conversation(prompt, "user")
        self.__truncate_conversation()
        result = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.conversation,
        )
        message = result.choices[0].message
        usage = result.usage
        self.__add_to_conversation(message.content, message.role)
        return message.content, usage

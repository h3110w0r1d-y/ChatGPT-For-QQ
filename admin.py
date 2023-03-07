from config import Config, get_baidu_access_token


def baiduAI():
    if Config.baiduai.enable:
        Config.baiduai.enable = False
        return "已关闭百度内容审核"
    else:
        Config.baiduai.enable = True
        get_baidu_access_token()
        return "已开启百度内容审核"


def showTokens():
    if Config.show_cost_tokens:
        Config.show_cost_tokens = False
        return "已隐藏Tokens"
    else:
        Config.show_cost_tokens = True
        return "已显示Tokens"


def add_group(group_id: int):
    if Config.group_list is None:
        Config.group_list = []
    if group_id in Config.group_list:
        return "群聊已存在"
    Config.group_list.append(group_id)
    return "已添加群聊"


def del_group(group_id: int):
    if Config.group_list is None:
        return "群聊列表为空"
    if group_id not in Config.group_list:
        return "群聊不存在"
    Config.group_list.remove(group_id)
    return "已删除群聊"


def get_group_list():
    if Config.group_list is None:
        return "群聊列表为空,所有群聊都会启用"
    return "启用群聊:\n" + '\n'.join([str(x) for x in Config.group_list])


Menu = {
    "menu":
        "=====  菜  单  =====\n"
        "1. 功能开关\n"
        "2. 群聊控制\n"
        "0. 退出",
    '1': {
        "menu":
            "===== 功能开关 =====\n"
            "1. 开启/关闭百度内容审核\n"
            "2. 显示/隐藏花费Tokens\n"
            "0. 返回",
        '1': baiduAI,
        '2': showTokens,
        '0': 'exit',
    },
    '2': {
        "menu":
            "===== 群聊控制 =====\n"
            "1. 增加群聊\n"
            "2. 删除群聊\n"
            "3. 查看启用群聊\n"
            "0. 返回",
        '1': {
            'desc': "请发送要增加的群号(发送0取消操作)",
            'func': add_group,
            '0': 'exit',
        },
        '2': {
            'desc': "请发送要删除的群号(发送0取消操作)",
            'func': del_group,
            '0': 'exit',
        },
        '3': get_group_list,
        '0': 'exit',
    },
    '0': 'exit',
}


class Admin:
    def __init__(self):
        self.in_menu = False
        self.menu_pos = []

    def get_current_menu(self):
        menu = Menu
        for i in self.menu_pos:
            menu = menu[i]
        return menu

    def get_menu(self):
        if not self.in_menu:
            return ""
        menu = self.get_current_menu()
        if 'desc' in menu:
            return menu['desc']
        if 'menu' in menu:
            return menu['menu']
        return "未知菜单:" + str(self.menu_pos)

    def exec(self, cmd: str):
        menu = self.get_current_menu()

        if not isinstance(menu, dict):
            return "未知菜单类型:" + str(type(menu))

        # 当前在普通多级菜单中
        if "menu" in menu:
            if cmd not in menu:
                return "无效指令"
            # 调用菜单中的exit
            if isinstance(menu[cmd], str):
                if menu[cmd] == 'exit':
                    if len(self.menu_pos) != 0:
                        self.menu_pos.pop()
                        return None
                    if len(self.menu_pos) == 0:
                        self.in_menu = False
                        return "退出菜单"
            # 调用菜单中的函数
            if callable(menu[cmd]):
                return menu[cmd]()
            # 进入下一级菜单
            if isinstance(menu[cmd], dict):
                self.menu_pos.append(cmd)
                return None
            # 其他情况
            return "无效指令"

        # 当前在func菜单中
        if 'func' in menu and callable(menu['func']):
            if cmd in menu and menu[cmd] == 'exit':
                self.menu_pos.pop()
                return None
            self.menu_pos.pop()
            response = menu['func'](cmd)
            return response

        if callable(menu[cmd]):
            return menu[cmd]()

        return "无效菜单项:" + str(menu)

    def handle_message(self, message: str):
        message = message.strip()
        if not self.in_menu:
            if not message.startswith("#"):
                return None

        if message == "#菜单":
            self.in_menu = True
            response = self.get_menu()
            return response
        else:
            response = self.exec(message)
            if response == '' or response is None:
                return self.get_menu()
            menu = self.get_menu()
            if menu is None or menu == '':
                return response
            return response + "\n\n" + self.get_menu()

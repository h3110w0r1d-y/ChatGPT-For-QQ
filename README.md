ChatGPT For QQ
================
将ChatGPT接入QQ

## 画饼
- [x] 接入百度智能云内容审核
- [x] 支持自定义敏感词
- [x] 对指定群聊开启Bot功能
- [x] 完善周报(prompt来自[这里](https://github.com/guaguaguaxia/weekly_report))
- [x] 管理员账号控制各项功能
- [ ] 将部分配置放入数据库

## 搭建方法
准备好🪜
- 安装[MCL](https://github.com/iTXTech/mirai-console-loader)
- 安装[mirai-api-http](https://github.com/project-mirai/mirai-api-http)插件
- `git clone https://github.com/h3110w0r1d-y/ChatGPT-for-QQ`
- `pip install -r requirements.txt`
- 复制`config.example.yml`为`config.yml`, 并修改配置
- `python main.py`

## 食用方法

### 申请OpenAI API_KEY

可以在[https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)获取api_key

### 接入百度智能云内容审核

可以在百度智能云免费申请5w次接口调用次数，获取key后修改配置文件即可

### 支持自定义敏感词 && 对指定群聊开启Bot功能

修改配置文件

### 完善周报

发送`周报:修复xxxbug等等`

### 管理员账号控制以上功能

修改配置文件 admin_qq，使用管理员QQ发送`#菜单`进入菜单。如果想自己加功能，可以直接修改`admin.py`中的`Menu`字典，可以继续往下嵌套菜单。目前仅实现了三种类型的菜单，不过感觉已经足够用了。

<details>
<summary>管理员菜单使用样例</summary>

![3498f8d9d3d9fd41cbcc1d34ea22008e](https://user-images.githubusercontent.com/52311174/223122619-b099065b-0883-4648-afdd-3b05e5d8f114.jpeg)

</details>


## 其他
功能很简单，没几行代码，欢迎Fork、提PR改进

<style>
img[alt="3498f8d9d3d9fd41cbcc1d34ea22008e"]{
  width:400px;
}
</style>
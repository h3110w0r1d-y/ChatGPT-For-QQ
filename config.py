import requests
import yaml


# 读取配置文件
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

    config_dict = yaml.safe_load(f)
    Config = Dict2Obj(config_dict)


# 获取百度AI access_token
def get_baidu_access_token():
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": Config.baiduai.api_key,
        "client_secret": Config.baiduai.secret_key
    }
    result = requests.post(url, params=params).json()
    Config.baiduai.access_token = str(result.get("access_token"))


if Config.baiduai.enable:
    get_baidu_access_token()

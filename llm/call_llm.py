'''
将各个大模型的接口封装为一个
'''

import openai
import json
import requests
import _thread as thread
import base64
import datetime
import os

from typing import Dict
from dotenv import load_dotenv, find_dotenv

def parse_llm_api_key(model:str, env_file:dict=None):
    """通过model和envfile来解析平台的参数

    Parameters
    ----------
    model : str
        哪个平台的模型
    env_file : Dict, optional
        配置文件, by default None
    """
    if env_file == None:
        _ = load_dotenv(find_dotenv())
        env_file = os.environ
    if model == "openai":
        return env_file["OPENAI_API_KEY"]
    elif model == "wenxin":
        return env_file["wenxin_api_key"], 
    else:
        raise ValueError(f"model{model} not support!!!")

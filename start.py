import requests
import os
import time
import json
import configuration
import qweather
from log import logger


config = configuration.config
key_words_dict = {}


def update_keyword():
    """更新关键词字典
    """
    global key_words_dict
    key_words_dict = {
        "北京天气": "北京当前气温为{}°C 天气为{}".format(
            *qweather.get_location_weather_info(
                qweather._get_location_id("北京"),
                ["temp", "text"]
            )
        ),
        "上海天气": "上海当前气温为{}°C 天气为{}".format(
            *qweather.get_location_weather_info(
                qweather._get_location_id("上海"),
                ["temp", "text"]
            )
        )
    }


def replace_keyword(content: str) -> str:
    """替换文本中的关键词

    :param content: 原始文本
    :return: 替换后的文本
    """
    for key, value in key_words_dict.items():
        if content.count("{" + key + "}") != 0:
            content = content.replace("{" + key + "}", value)
    return content


def send_notification(uuid: str, title: str, content: str) -> bool:
    """发送通知到设备

    :param uuid: 设备id
    :param title: 通知标题
    :param content: 通知内容

    :return: 是否成功推送
    """
    url = config.get("bark", "url")
    if uuid == "":
        return False
    url += uuid

    if title != "":
        url += "/" + title

    if content == "":
        return False
    url += "/" + content

    rsp = requests.get(url)
    rsp_code = rsp.status_code

    if rsp_code != 200:
        logger.warning("发送notification的请求异常 " + url)
        return False

    rsp_json = json.loads(rsp.text)
    if rsp_json.get("message") != "success":
        logger.warning("发送notification失败 " + url)
        return False

    return True


def start():
    current_time = time.strftime("%H%M", time.localtime())
    if not os.path.isfile("./messages.json"):
        temp_f = open("./messages.json", "w")
        temp_f.close()
    with open("./messages.json", "r") as config_file:
        config = config_file.read()
        if not config:
            logger.warning("配置文件为空")
            return False

    try:
        config = json.loads(config)
    except:
        logger.error("载入json错误")
        return False

    items = config.get(current_time)
    if items != None:
        update_keyword()
        for item in items:
            uuid, title, content = item.values()
            content = replace_keyword(content)
            if send_notification(uuid, title, content):
                logger.info(f"向 {uuid} 发送消息成功")
            else:
                logger.warning(f"向 {uuid} 发送消息失败")
    else:
        logger.info(f"{current_time}: 该时间段无配置")


if __name__ == "__main__":
    start()
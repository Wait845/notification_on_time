# 介绍
一个可以定时向设备发送通知消息的项目

其中，发送消息部分是基于开源项目[Bark](https://github.com/Finb/Bark)

目前仅支持IOS, Ipad OS 以及 Mac OS

<br/>

# 配置

## 1. 更改config/config.ini
该文件包含程序运行过程中需要使用的一些变量，

如：外部API的URL,外部API的key等等
```
[qweather]
key = 和风天气KEY
geoapi_url = https://geoapi.qweather.com/v2/city/lookup?
weather_url = https://devapi.qweather.com/v7/weather/now?

[bark]
url = https://api.day.app/
```

## 2. 发送消息的内容配置
该配置主要包含1.)发送消息的时间 2.)消息内容

其中，消息内容还包含发送到的设备UUID,通知的标题(可选),通知的内容

并且，同一时间下可以配置多条消息内容
```json
# message.json
{
    "2209": [
        {
            "uuid": "替换成自己的uuid",
            "title": "hello",
            "content": "{北京天气}"
        },
        {
            "uuid": "另一个uuid",
            "title": "hello",
            "content": "括号外的字不会被替换{上海天气}"
        }
    ],
    "1000": [
        {
            "uuid": "替换成自己的uuid",
            "title": "hello",
            "content": "另一个时间段的消息"
        }
    ]
}
```

<br/>

# 消息替换规则
```Python3
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
```
通过代码可以看到，消息替换部分由'replace_keyword'函数完成。在messages.json文件消息内容的'content'字段，用大括号'{}'包含关键词，则该关键词就会被识别到并替换。

而key_words_dict则定义了关键词对应的文本，在这里我通过调用和风天气API对‘北京天气’和‘上海天气’这两个关键词进行了替换，使它们能够动态更新最新的数据

<br/>

# 启动
为了减小服务器的压力，本脚步不会在后台常驻，而是通过每分钟调用的方法启动

如在Linux环境下，可以使用crontab的方式启动
```
* * * * * python3 start.py
```
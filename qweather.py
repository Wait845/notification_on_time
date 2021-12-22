import json
import requests
import configuration
from log import logger


config = configuration.config
qweather_key = config.get("qweather", "key")
geoapi_url = config.get("qweather", "geoapi_url")
weather_url = config.get("qweather", "weather_url")


def _get_location_id(location_name: str, adm: str = "", range_: str = "") -> str:
    """获取城市的location_id

    :param city_name: 需要查询地区的名称，支持文字、以英文逗号分隔的经度,纬度坐标（十进制，最多支持小数点后两位）、LocationID或Adcode（仅限中国城市）。例如 location=北京 或 location=116.41,39.92
    :param adm: 城市的上级行政区划，默认不限定行政区划。 可设定只在某个行政区划范围内进行搜索，用于排除重名城市或对结果进行过滤。例如 adm=beijing
    :param range_: 搜索范围，可设定只在某个国家范围内进行搜索，国家名称需使用ISO 3166 所定义的国家代码。
    :return: location_id
    """
    url = geoapi_url
    url += "location={location_name}&key={qweather_key}".format(
        location_name = location_name,
        qweather_key = qweather_key
    )
    if adm:
        url += f"&adm={adm}"
    if range_:
        url += f"&range={range_}"

    rsp = requests.get(url)
    if rsp.status_code != 200:
        logger.warning(f"获取location_id的请求异常{url}")
        return ""

    rsp_json = json.loads(rsp.text)
    rsp_code = rsp_json.get("code")
    if rsp_code != "200":
        logger.warning(f"获取location_id的结果异常:{rsp_json} {url}")
        return ""

    location_id = rsp_json.get("location")[0].get("id")
    logger.info("获取location_id成功")
    return location_id


def _get_location_weather(location_id: str, unit: str = "") -> dict:
    """获取地区实时天气

    :param location_id: 需要查询地区的LocationID或以英文逗号分隔的经度,纬度坐标（十进制，最多支持小数点后两位），LocationID可通过函数get_location_id获取。例如 location=101010100 或 location=116.41,39.92
    :param unit: 度量衡单位参数选择，例如温度选摄氏度或华氏度、公里或英里。默认公制单位
        m 公制单位，默认
        i 英制单位
    :return: 字典形式的实况天气
    """
    url = weather_url
    url += "location={location_id}&key={key}".format(
        location_id = location_id,
        key = qweather_key
    )
    if unit:
        url += f"&unit={unit}"

    rsp = requests.get(url)
    if rsp.status_code != 200:
        logger.warning("获取location_weather的请求异常")
        return {}

    rsp_json = json.loads(rsp.text)
    rsp_code = rsp_json.get("code")
    if rsp_code != "200":
        logger.warning("获取location_weather的结果异常")
        return {}

    logger.info("获取location_weather成功")
    return rsp_json


def get_location_weather_info(location_id: str, rec_types: list, unit: str = "") -> list:
    """列表形式 获取地区实时天气的信息

    :param location_id: 地区id, 可通过函数 _get_location_id 获取
    :param rec_types: 需要的信息类型，可选的有
        ("obsTime", "temp", "feelsLike", "icon", "text",
            "wind360", "windDir", "windScale", "windSpeed",
            "humidity", "precip", "pressure", "vis", "cloud", "dew")
        对应为
        ("数据观测时间", "温度", "体感温度", "天气状况和图标的代码", "天气状况的文字描述",
            "风向360角度", "风向", "风力等级", "风速，公里/小时", "相对湿度，百分比数值",
            "当前小时累计降水量，默认单位：毫米", "大气压强，默认单位：百帕", "能见度，默认单位：公里",
            "云量，百分比数值。可能为空", "露点温度。可能为空", )
    :param unit: 度量衡单位参数选择，例如温度选摄氏度或华氏度、公里或英里。默认公制单位
        m 公制单位，默认
        i 英制单位
    :return: 指定信息的具体值，顺序为rec_types的顺序
    """
    if not location_id or not rec_types:
        logger.warning("location_info接受到了异常参数")
        return []

    location_weather = _get_location_weather(location_id, unit)
    if not location_weather:
        return []

    result = []
    location_weather = location_weather.get("now")
    for rec_type in rec_types:
        rec_info = location_weather.get(rec_type)
        if rec_info:
            result.append(rec_info)

    logger.info("location_info执行成功")
    return result


# 示例
# print(get_location_weather_info(
#     _get_location_id("北京"),
#     ["temp", "feelsLike"]
# ))


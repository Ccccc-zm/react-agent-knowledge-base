import os
import requests
from utils.logger_handler import logger
from langchain_core.tools import tool
from rag.rag_service import RagSummarizeService
import random
from utils.config_handler import agent_conf
from utils.path_tool import get_abs_path

rag = RagSummarizeService()

user_ids = ["1001", "1002", "1003", "1004", "1005", "1006", "1007", "1008", "1009", "1010",]
month_arr = ["2025-01", "2025-02", "2025-03", "2025-04", "2025-05", "2025-06",
             "2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2025-12", ]

external_data = {}


@tool(description="从向量存储中检索参考资料")
def rag_summarize(query: str) -> str:
    return rag.rag_summarize(query)


@tool(description="获取指定城市的天气，以消息字符串的形式返回")
def get_weather(city: str) -> str:
    api_host = os.getenv("QWEATHER_API_HOST")
    api_key = os.getenv("QWEATHER_API_KEY")

    if not api_host:
        return "错误：未配置和风天气API Host，请在.env文件中设置。"
    if not api_key:
        return "错误：未配置和风天气API Key，请在.env文件中设置。"

    # 1. 获取城市ID
    # ★ 关键修改：路径调整为 /geo/v2/city/lookup
    geo_url = f"https://{api_host}/geo/v2/city/lookup?location={city}&key={api_key}"

    print(f"[DEBUG] 城市查询请求 URL: {geo_url}")

    try:
        resp = requests.get(geo_url, timeout=10)
        print(f"[DEBUG] 城市查询响应状态码: {resp.status_code}")

        geo_res = resp.json()
        if geo_res.get("code") == "200" and geo_res.get("location"):
            location_id = geo_res["location"][0]["id"]
            print(f"[DEBUG] 成功获取城市 ID: {location_id}")
        else:
            error_msg = f"未找到城市'{city}'，API返回：{geo_res}"
            print(f"[DEBUG] 失败：{error_msg}")
            return error_msg
    except Exception as e:
        print(f"[DEBUG] 查询城市ID时发生异常：{e}")
        return f"查询城市ID时出错: {e}"

    # 2. 获取实时天气
    weather_url = f"https://{api_host}/v7/weather/now?location={location_id}&key={api_key}"
    print(f"[DEBUG] 天气查询请求 URL: {weather_url}")

    try:
        resp = requests.get(weather_url, timeout=10)
        print(f"[DEBUG] 天气查询响应状态码: {resp.status_code}")

        weather_res = resp.json()
        if weather_res.get("code") == "200":
            w = weather_res["now"]
            result = f"{city}当前天气：{w['text']}，气温{w['temp']}℃，体感温度{w['feelsLike']}℃，{w['windDir']}{w['windScale']}级，相对湿度{w['humidity']}%。"
            print(f"[DEBUG] 成功获取天气：{result}")
            return result
        else:
            error_msg = f"获取天气失败，API返回错误：{weather_res}"
            print(f"[DEBUG] 失败：{error_msg}")
            return error_msg
    except Exception as e:
        print(f"[DEBUG] 查询天气时发生异常：{e}")
        return f"查询天气时出错: {e}"


@tool(description="获取用户所在城市的名称，以纯字符串形式返回")
def get_user_location() -> str:
    return random.choice(["深圳", "合肥", "杭州"])


@tool(description="获取用户的ID，以纯字符串形式返回")
def get_user_id() -> str:
    return random.choice(user_ids)


@tool(description="获取当前月份，以纯字符串形式返回")
def get_current_month() -> str:
    return random.choice(month_arr)


def generate_external_data():
    """
    {
        "user_id": {
            "month" : {"特征": xxx, "效率": xxx, ...}
            "month" : {"特征": xxx, "效率": xxx, ...}
            "month" : {"特征": xxx, "效率": xxx, ...}
            ...
        },
        "user_id": {
            "month" : {"特征": xxx, "效率": xxx, ...}
            "month" : {"特征": xxx, "效率": xxx, ...}
            "month" : {"特征": xxx, "效率": xxx, ...}
            ...
        },
        "user_id": {
            "month" : {"特征": xxx, "效率": xxx, ...}
            "month" : {"特征": xxx, "效率": xxx, ...}
            "month" : {"特征": xxx, "效率": xxx, ...}
            ...
        },
        ...
    }
    :return:
    """
    if not external_data:
        external_data_path = get_abs_path(agent_conf["external_data_path"])

        if not os.path.exists(external_data_path):
            raise FileNotFoundError(f"外部数据文件{external_data_path}不存在")

        with open(external_data_path, "r", encoding="utf-8") as f:
            for line in f.readlines()[1:]:
                arr: list[str] = line.strip().split(",")

                user_id: str = arr[0].replace('"', "")
                feature: str = arr[1].replace('"', "")
                efficiency: str = arr[2].replace('"', "")
                consumables: str = arr[3].replace('"', "")
                comparison: str = arr[4].replace('"', "")
                time: str = arr[5].replace('"', "")

                if user_id not in external_data:
                    external_data[user_id] = {}

                external_data[user_id][time] = {
                    "特征": feature,
                    "效率": efficiency,
                    "耗材": consumables,
                    "对比": comparison,
                }


@tool(description="从外部系统中获取指定用户在指定月份的使用记录，以纯字符串形式返回， 如果未检索到返回空字符串")
def fetch_external_data(user_id: str, month: str) -> str:
    generate_external_data()

    try:
        return external_data[user_id][month]
    except KeyError:
        logger.warning(f"[fetch_external_data]未能检索到用户：{user_id}在{month}的使用记录数据")
        return ""


@tool(description="无入参，无返回值，调用后触发中间件自动为报告生成的场景动态注入上下文信息，为后续提示词切换提供上下文信息")
def fill_context_for_report():
    return "fill_context_for_report已调用"

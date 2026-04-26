"""
天气查询工具插件
用于查询指定城市的实时天气和预报信息
"""

import requests
from .base import ToolPlugin


# 工具定义
GET_WEATHER_DEFINITION = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "查询指定城市的实时天气和预报信息。当用户询问天气情况但未指定城市时，先使用此工具并提示用户提供城市名称。",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "要查询天气的城市名称,例如:杭州、北京、上海等"
                }
            },
            "required": ["city"]
        }
    }
}


def _handle_get_weather(arguments):
    """处理天气查询"""
    city = arguments.get('city', '').strip()
    if not city:
        return {
            "success": False,
            "message": "请提供要查询天气的城市名称"
        }
    
    # 调用 wttr.in API 获取天气数据,format=j1 返回 JSON 格式
    url = f"https://wttr.in/{city}?format=j1"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    weather_data = response.json()
    
    # 提取当前天气信息
    current = weather_data.get('current_condition', [{}])[0]
    location = weather_data.get('nearest_area', [{}])[0]
    
    city_name = location.get('areaName', [{}])[0].get('value', city)
    region = location.get('region', [{}])[0].get('value', '')
    country = location.get('country', [{}])[0].get('value', '')
    
    temp_c = current.get('temp_C', 'N/A')
    feels_like_c = current.get('FeelsLikeC', 'N/A')
    weather_desc = current.get('weatherDesc', [{}])[0].get('value', 'N/A')
    humidity = current.get('humidity', 'N/A')
    wind_speed = current.get('windspeedKmph', 'N/A')
    wind_dir = current.get('winddir16Point', 'N/A')
    uv_index = current.get('uvIndex', 'N/A')
    visibility = current.get('visibility', 'N/A')
    
    # 构建友好的天气报告文本
    weather_report = f"📍 {city_name} ({region}, {country}) 实时天气:\n"
    weather_report += f"🌡 温度: {temp_c}°C (体感 {feels_like_c}°C)\n"
    weather_report += f"☁ 天气: {weather_desc}\n"
    weather_report += f"💧 湿度: {humidity}%\n"
    weather_report += f"🌬 风速: {wind_speed} km/h, 风向: {wind_dir}\n"
    weather_report += f"☀ 紫外线指数: {uv_index}\n"
    weather_report += f"👁 能见度: {visibility} km"
    
    return {
        "success": True,
        "data": weather_data,
        "report": weather_report
    }


# 创建工具实例
weather_tool = ToolPlugin(
    name="get_weather",
    definition=GET_WEATHER_DEFINITION,
    handler=_handle_get_weather
)
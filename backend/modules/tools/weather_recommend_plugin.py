"""
天气推荐景点工具插件
根据天气情况推荐适合的旅游景点
"""

from .base import ToolPlugin


# 天气推荐景点映射
weather_recommend = {
    "晴": ["户外公园、爬山、城市漫步"],
    "多云": ["古镇、城市景点、博物馆"],
    "雨": ["室内博物馆、咖啡馆、书店"],
    "雪": ["滑雪场、温泉、室内乐园"]
}


# 工具定义
WEATHER_RECOMMEND_DEFINITION = {
    "type": "function",
    "function": {
        "name": "weather_recommend",
        "description": "根据给定的天气状况推荐适合的旅游景点。此工具不查询天气，仅根据传入的天气参数返回推荐。当用户已知天气并询问适合去哪里玩时使用此工具。",
        "parameters": {
            "type": "object",
            "properties": {
                "weather": {
                    "type": "string",
                    "description": "天气状况，例如:晴、多云、雨、雪"
                }
            },
            "required": ["weather"]
        }
    }
}


def _handle_weather_recommend(arguments):
    """处理天气推荐景点"""
    weather = arguments.get('weather', '').strip()
    if not weather:
        return {
            "success": False,
            "message": "请提供天气状况，例如:晴、多云、雨、雪"
        }
    
    # 查找推荐景点
    recommendations = weather_recommend.get(weather)
    if recommendations:
        report = f"🌤 天气状况: {weather}\n"
        report += f"🎯 推荐景点: {', '.join(recommendations)}"
        return {
            "success": True,
            "data": recommendations,
            "report": report
        }
    else:
        # 如果没有匹配的天气，提供通用建议
        all_options = []
        for w, spots in weather_recommend.items():
            all_options.extend(spots)
        report = f"🌤 天气状况: {weather}\n"
        report += f"🎯 当前天气没有特定推荐，可参考以下选项: {', '.join(set(all_options))}"
        return {
            "success": True,
            "data": list(set(all_options)),
            "report": report
        }


# 创建工具实例
weather_recommend_tool = ToolPlugin(
    name="weather_recommend",
    definition=WEATHER_RECOMMEND_DEFINITION,
    handler=_handle_weather_recommend
)

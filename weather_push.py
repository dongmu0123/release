import requests
import json
import os
from datetime import datetime

# ============ 配置区域 ============
# 这些值从 GitHub Secrets 或环境变量读取
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN", "189669d152b74e6288eb4274904079df")       # PushPlus Token
CITY = os.environ.get("CITY", "东莞")                        # 城市名
CUSTOM_TEXT = os.environ.get("CUSTOM_TEXT", "今天也要开心！") # 每日自定义文字
TOPIC = os.environ.get("TOPIC", "")                              # 群组编码（向别人推送时需要）
# ==================================


def get_weather(city):
    """从 wttr.in 获取天气数据（免费，无需API Key）"""
    url = f"https://wttr.in/{city}?format=j1&lang=zh"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    # 当前天气
    current = data["current_condition"][0]
    temp = current["temp_C"]
    feels_like = current["FeelsLikeC"]
    humidity = current["humidity"]
    wind_speed = current["windspeedKmph"]
    # wttr.in 中文天气描述在 lang_zh 字段
    weather_desc = current.get("lang_zh", [{}])
    if isinstance(weather_desc, list) and weather_desc:
        weather_desc = weather_desc[0].get("value", current["weatherDesc"][0]["value"])
    else:
        weather_desc = current["weatherDesc"][0]["value"]

    # 今日预报
    today_forecast = data["weather"][0]
    max_temp = today_forecast["maxtempC"]
    min_temp = today_forecast["mintempC"]

    # 日出日落
    astronomy = today_forecast.get("astronomy", [{}])[0]
    sunrise = astronomy.get("sunrise", "N/A")
    sunset = astronomy.get("sunset", "N/A")

    # 降雨概率（取全天最高值）和紫外线指数
    hourly = today_forecast.get("hourly", [])
    rain_chance = 0
    uv_index = 0
    for h in hourly:
        rain_chance = max(rain_chance, int(h.get("chanceofrain", 0)))
        uv_index = max(uv_index, int(h.get("uvIndex", 0)))

    return {
        "temp": temp,
        "feels_like": feels_like,
        "humidity": humidity,
        "wind_speed": wind_speed,
        "weather_desc": weather_desc,
        "max_temp": max_temp,
        "min_temp": min_temp,
        "sunrise": sunrise,
        "sunset": sunset,
        "rain_chance": rain_chance,
        "uv_index": uv_index,
    }


def get_life_tips(weather):
    """根据天气生成穿衣、带伞、防晒建议"""
    feels = int(weather["feels_like"])
    rain = weather["rain_chance"]
    uv = weather["uv_index"]

    # 穿衣建议
    if feels >= 33:
        clothing = "很热！穿短袖短裤、裙子，注意防暑"
    elif feels >= 28:
        clothing = "天气炎热，穿轻薄透气的衣服"
    elif feels >= 23:
        clothing = "温暖舒适，穿T恤、薄衬衫即可"
    elif feels >= 18:
        clothing = "微凉，建议穿长袖或薄外套"
    elif feels >= 12:
        clothing = "有点冷，穿外套或卫衣"
    elif feels >= 5:
        clothing = "挺冷的，穿厚外套、毛衣"
    else:
        clothing = "非常冷！穿羽绒服、围巾、手套"

    # 带伞建议
    if rain >= 70:
        umbrella = "降雨概率很高，一定要带伞！"
    elif rain >= 40:
        umbrella = "可能会下雨，建议带把伞"
    elif rain >= 20:
        umbrella = "有小概率降雨，可以备一把伞"
    else:
        umbrella = "不用带伞，放心出门"

    # 防晒建议
    if uv >= 8:
        sunscreen = "紫外线很强！一定要涂防晒霜，戴帽子和墨镜"
    elif uv >= 6:
        sunscreen = "紫外线较强，记得涂防晒霜"
    elif uv >= 3:
        sunscreen = "紫外线中等，建议涂防晒"
    else:
        sunscreen = "紫外线较弱，可以不涂防晒"

    return clothing, umbrella, sunscreen


def build_message(city, weather, custom_text):
    """构建推送消息内容（HTML格式）"""
    today = datetime.now().strftime("%Y年%m月%d日 %A")
    weekday_map = {
        "Monday": "星期一", "Tuesday": "星期二", "Wednesday": "星期三",
        "Thursday": "星期四", "Friday": "星期五", "Saturday": "星期六", "Sunday": "星期日"
    }
    for en, zh in weekday_map.items():
        today = today.replace(en, zh)

    clothing, umbrella, sunscreen = get_life_tips(weather)

    html = f"""
    <div style="font-family: 'Microsoft YaHei', sans-serif; max-width: 400px; margin: 0 auto; padding: 20px;">
        <h2 style="text-align:center; color:#333;">🌤 {city} 今日天气</h2>
        <p style="text-align:center; color:#888; font-size:14px;">{today}</p>
        <hr style="border: none; border-top: 1px solid #eee;">
        <table style="width:100%; font-size:15px; line-height:2;">
            <tr><td>🌡 当前温度</td><td style="text-align:right;"><b>{weather['temp']}°C</b></td></tr>
            <tr><td>🤔 体感温度</td><td style="text-align:right;">{weather['feels_like']}°C</td></tr>
            <tr><td>📊 今日温度</td><td style="text-align:right;">{weather['min_temp']}°C ~ {weather['max_temp']}°C</td></tr>
            <tr><td>☁ 天气状况</td><td style="text-align:right;">{weather['weather_desc']}</td></tr>
            <tr><td>💧 湿度</td><td style="text-align:right;">{weather['humidity']}%</td></tr>
            <tr><td>🌬 风速</td><td style="text-align:right;">{weather['wind_speed']} km/h</td></tr>
            <tr><td>🌂 降雨概率</td><td style="text-align:right;">{weather['rain_chance']}%</td></tr>
            <tr><td>☀ 紫外线指数</td><td style="text-align:right;">{weather['uv_index']}</td></tr>
            <tr><td>🌅 日出</td><td style="text-align:right;">{weather['sunrise']}</td></tr>
            <tr><td>🌇 日落</td><td style="text-align:right;">{weather['sunset']}</td></tr>
        </table>
        <hr style="border: none; border-top: 1px solid #eee;">
        <div style="margin-top:15px; padding:15px; background:#fff8f0; border-radius:10px; font-size:14px; line-height:1.8;">
            <p style="margin:5px 0;">👗 <b>穿衣：</b>{clothing}</p>
            <p style="margin:5px 0;">🌂 <b>带伞：</b>{umbrella}</p>
            <p style="margin:5px 0;">🧴 <b>防晒：</b>{sunscreen}</p>
        </div>
        <hr style="border: none; border-top: 1px solid #eee;">
        <div style="text-align:center; margin-top:15px; padding:15px; background:#f0f8ff; border-radius:10px;">
            <p style="font-size:16px; color:#e74c3c; margin:0;">💌 {custom_text}</p>
        </div>
    </div>
    """
    return html


def push_to_wechat(token, title, content):
    """通过 PushPlus 推送消息到微信"""
    url = "https://www.pushplus.plus/send"
    payload = {
        "token": token,
        "title": title,
        "content": content,
        "template": "html",
    }
    if TOPIC:
        payload["topic"] = TOPIC
    resp = requests.post(url, json=payload, timeout=10)
    result = resp.json()
    if result.get("code") == 200:
        print(f"✅ 推送成功！消息ID: {result.get('data')}")
    else:
        print(f"❌ 推送失败: {result.get('msg')}")
        raise Exception(f"PushPlus error: {result.get('msg')}")


def main():
    if not PUSHPLUS_TOKEN:
        print("❌ 请设置 PUSHPLUS_TOKEN 环境变量")
        return

    print(f"📍 城市: {CITY}")
    print(f"📝 自定义文字: {CUSTOM_TEXT}")

    weather = get_weather(CITY)
    print(f"🌡 当前温度: {weather['temp']}°C, {weather['weather_desc']}")

    content = build_message(CITY, weather, CUSTOM_TEXT)
    title = f"🌤 {CITY}今日天气 | {weather['temp']}°C {weather['weather_desc']}"

    push_to_wechat(PUSHPLUS_TOKEN, title, content)


if __name__ == "__main__":
    main()

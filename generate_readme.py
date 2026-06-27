import json
from datetime import datetime, timezone, timedelta

wib = timezone(timedelta(hours=7))

def get_wind_dir(deg):
    dirs = ["N","NE","E","SE","S","SW","W","NW"]
    return dirs[round(deg / 45) % 8]

def unix_to_wib(ts):
    return datetime.fromtimestamp(ts, tz=wib).strftime("%H:%M")

with open("weather.json") as f:
    w = json.load(f)

try:
    with open("air.json") as f:
        a = json.load(f)
    aqi_num = a["list"][0]["main"]["aqi"]
except:
    aqi_num = None

temp      = round(w["main"]["temp"])
feels     = round(w["main"]["feels_like"])
temp_min  = round(w["main"]["temp_min"])
temp_max  = round(w["main"]["temp_max"])
humidity  = w["main"]["humidity"]
pressure  = w["main"]["pressure"]
wind_speed= w["wind"]["speed"]
wind_dir  = get_wind_dir(w["wind"].get("deg", 0))
clouds    = w["clouds"]["all"]
visibility= round(w.get("visibility", 0) / 1000, 1)
condition = w["weather"][0]["description"].title()
rain_1h   = w.get("rain", {}).get("1h", None)
rain_str  = f"{rain_1h} mm" if rain_1h else "—"
sunrise   = unix_to_wib(w["sys"]["sunrise"])
sunset    = unix_to_wib(w["sys"]["sunset"])

updated   = datetime.now(tz=wib).strftime("%d %B %Y, %H:%M WIB")
day_name  = datetime.now(tz=wib).strftime("%A, %d %B %Y")

aqi_labels = {1:"Good 🟢", 2:"Fair 🟡", 3:"Moderate 🟠", 4:"Poor 🔴", 5:"Very Poor 🟣"}
aqi_label  = aqi_labels.get(aqi_num, "Unknown") if aqi_num else "Unknown"
aqi_str    = f"{aqi_label} (AQI {aqi_num})" if aqi_num else "—"

readme = f"""# 🌦️ Jakarta Weather Tracker

> Jakarta weather auto-updated via [OpenWeatherMap](https://openweathermap.org/) · Updates: 07:00 – 22:00 WIB

<div align="center">

![Jakarta Weather](./card.svg)

</div>

---

## 📊 {condition} — {day_name}

| | | | |
|:---:|:---|:---:|:---|
| 🌡️ | **Temperature** &nbsp; `{temp}°C` *(feels like {feels}°C)* | 💧 | **Humidity** &nbsp; `{humidity}%` |
| 🌡️ | **Min / Max** &nbsp; `{temp_min}° / {temp_max}°` | ☁️ | **Cloud Cover** &nbsp; `{clouds}%` |
| 🌬️ | **Wind** &nbsp; `{wind_speed} m/s` from `{wind_dir}` | 👁️ | **Visibility** &nbsp; `{visibility} km` |
| 🌫️ | **Pressure** &nbsp; `{pressure} hPa` | 🌧️ | **Rain (1h)** &nbsp; `{rain_str}` |
| 🌅 | **Sunrise** &nbsp; `{sunrise} WIB` | 🌇 | **Sunset** &nbsp; `{sunset} WIB` |
| 🏭 | **Air Quality** &nbsp; {aqi_str} | 🕗 | **Updated** &nbsp; `{updated}` |

---

## 📂 Data & Log

| File | Description |
|:---|:---|
| 📄 [weather.json](./weather.json) | Latest raw weather data from API |
| 🎨 [card.svg](./card.svg) | Weather card (SVG) |
| 📁 [history/](./history) | Weather snapshots per session |

---

<sub>⚙️ Automated by [GitHub Actions](../../actions) · Source: OpenWeatherMap API</sub>
"""

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)

print("README.md generated successfully")

import json
import sys
from datetime import datetime, timezone, timedelta

wib = timezone(timedelta(hours=7))

def get_wind_dir(deg):
    dirs = ["N","NE","E","SE","S","SW","W","NW"]
    return dirs[round(deg / 45) % 8]

def unix_to_wib(ts):
    return datetime.fromtimestamp(ts, tz=wib).strftime("%H:%M")

# Load weather
with open("weather.json") as f:
    w = json.load(f)

# Load air quality
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
day_only  = datetime.now(tz=wib).strftime("%A")

aqi_labels = {1:"Good", 2:"Fair", 3:"Moderate", 4:"Poor", 5:"Very Poor"}
aqi_colors = {1:"brightgreen", 2:"yellowgreen", 3:"yellow", 4:"orange", 5:"red"}
aqi_emojis = {1:"🟢", 2:"🟡", 3:"🟠", 4:"🔴", 5:"🟣"}

aqi_label = aqi_labels.get(aqi_num, "Unknown") if aqi_num else "Unknown"
aqi_color = aqi_colors.get(aqi_num, "lightgrey") if aqi_num else "lightgrey"
aqi_emoji = aqi_emojis.get(aqi_num, "") if aqi_num else ""

def enc(s):
    return str(s).replace(" ", "%20").replace(",", "%2C").replace("/", "%2F").replace("(", "%28").replace(")", "%29").replace("°", "%C2%B0").replace("—", "-")

readme = f"""# 🌦️ Jakarta Weather Tracker

> Cuaca Jakarta diperbarui otomatis via [OpenWeatherMap](https://openweathermap.org/) · Update: 07:00 – 22:00 WIB

<div align="center">

![Jakarta Weather](./card.svg)

</div>

---

## 📊 {condition} — {day_only}

<div align="center">

![Suhu](https://img.shields.io/badge/🌡️%20Suhu-{enc(f"{temp}°C (terasa {feels}°C)")}-ff6b35?style=for-the-badge)
![Min Max](https://img.shields.io/badge/🌡️%20Min%20/%20Max-{enc(f"{temp_min}°C / {temp_max}°C")}-ff8c42?style=for-the-badge)
![Kelembapan](https://img.shields.io/badge/💧%20Kelembapan-{humidity}%25-4fc3f7?style=for-the-badge)
![Angin](https://img.shields.io/badge/🌬️%20Angin-{enc(f"{wind_speed} m/s dari {wind_dir}")}-81d4fa?style=for-the-badge)
![Awan](https://img.shields.io/badge/☁️%20Tutupan%20Awan-{clouds}%25-90a4ae?style=for-the-badge)
![Jarak Pandang](https://img.shields.io/badge/👁️%20Jarak%20Pandang-{enc(f"{visibility} km")}-78909c?style=for-the-badge)
![Tekanan](https://img.shields.io/badge/🌫️%20Tekanan%20Udara-{enc(f"{pressure} hPa")}-ab47bc?style=for-the-badge)
![Hujan](https://img.shields.io/badge/🌧️%20Hujan%20(1%20jam)-{enc(rain_str)}-1e88e5?style=for-the-badge)
![AQI](https://img.shields.io/badge/🏭%20Kualitas%20Udara-{enc(f"{aqi_label} {aqi_emoji}")}-{aqi_color}?style=for-the-badge)
![Sunrise](https://img.shields.io/badge/🌅%20Matahari%20Terbit-{enc(f"{sunrise} WIB")}-ffca28?style=for-the-badge)
![Sunset](https://img.shields.io/badge/🌇%20Matahari%20Terbenam-{enc(f"{sunset} WIB")}-ff7043?style=for-the-badge)
![Updated](https://img.shields.io/badge/🕗%20Diperbarui-{enc(updated)}-informational?style=for-the-badge)

</div>

---

## 📂 Data & Log

| File | Deskripsi |
|:---|:---|
| 📄 [weather.json](./weather.json) | Raw data cuaca terbaru dari API |
| 🎨 [card.svg](./card.svg) | Weather card (SVG) |
| 📁 [history/](./history) | Snapshot cuaca per sesi |

---

<sub>⚙️ Dijalankan otomatis oleh [GitHub Actions](../../actions) · Sumber: OpenWeatherMap API</sub>
"""

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)

print("README.md generated successfully")

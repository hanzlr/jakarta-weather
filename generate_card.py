import json
import sys
from datetime import datetime
import math

def get_wind_dir(deg):
    dirs = ["N","NE","E","SE","S","SW","W","NW"]
    return dirs[round(deg / 45) % 8]

def get_aqi_label(aqi):
    labels = {1: ("Good", "#22c55e", "#dcfce7"), 2: ("Fair", "#84cc16", "#f0fdf4"),
              3: ("Moderate", "#f59e0b", "#fef3c7"), 4: ("Poor", "#ef4444", "#fee2e2"),
              5: ("Very Poor", "#dc2626", "#fee2e2")}
    return labels.get(aqi, ("Unknown", "#888", "#f3f4f6"))

def get_weather_emoji(weather_id):
    if weather_id < 300: return "⛈️"
    elif weather_id < 400: return "🌦️"
    elif weather_id < 500: return "🌧️"
    elif weather_id < 600: return "🌧️"
    elif weather_id < 700: return "❄️"
    elif weather_id < 800: return "🌫️"
    elif weather_id == 800: return "☀️"
    elif weather_id == 801: return "🌤️"
    elif weather_id == 802: return "⛅"
    else: return "🌥️"

def unix_to_wib(ts):
    from datetime import timezone, timedelta
    wib = timezone(timedelta(hours=7))
    return datetime.fromtimestamp(ts, tz=wib).strftime("%H:%M")

# Load weather data
with open("weather.json") as f:
    w = json.load(f)

# Load air quality data
try:
    with open("air.json") as f:
        a = json.load(f)
    aqi = a["list"][0]["main"]["aqi"]
except:
    aqi = None

# Parse fields
temp = round(w["main"]["temp"])
feels = round(w["main"]["feels_like"])
temp_min = round(w["main"]["temp_min"])
temp_max = round(w["main"]["temp_max"])
humidity = w["main"]["humidity"]
pressure = w["main"]["pressure"]
wind_speed = w["wind"]["speed"]
wind_dir = get_wind_dir(w["wind"].get("deg", 0))
clouds = w["clouds"]["all"]
visibility = round(w.get("visibility", 0) / 1000, 1)
condition = w["weather"][0]["description"].title()
weather_id = w["weather"][0]["id"]
emoji = get_weather_emoji(weather_id)
sunrise = unix_to_wib(w["sys"]["sunrise"])
sunset = unix_to_wib(w["sys"]["sunset"])
rain_1h = w.get("rain", {}).get("1h", None)

from datetime import timezone, timedelta
wib = timezone(timedelta(hours=7))
updated = datetime.now(tz=wib).strftime("%d %b %Y, %H:%M WIB")
day_name = datetime.now(tz=wib).strftime("%A, %d %B %Y")

aqi_label, aqi_color, aqi_bg = get_aqi_label(aqi) if aqi else ("—", "#888", "#f3f4f6")
rain_str = f"{rain_1h} mm" if rain_1h else "—"

# SVG dimensions
W = 540
H = 320

def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&amp;display=swap');
      * {{ font-family: 'Inter', -apple-system, sans-serif; }}
    </style>
  </defs>

  <!-- Background -->
  <rect width="{W}" height="{H}" rx="16" fill="#0f172a"/>

  <!-- Subtle top gradient bar -->
  <rect x="0" y="0" width="{W}" height="4" rx="2" fill="#3b82f6" opacity="0.6"/>

  <!-- Header: location + date -->
  <text x="24" y="36" font-size="13" fill="#94a3b8" font-weight="400">📍 Jakarta, Indonesia</text>
  <text x="{W-24}" y="36" font-size="13" fill="#64748b" text-anchor="end">{esc(day_name)}</text>

  <!-- Big emoji -->
  <text x="24" y="100" font-size="56">{emoji}</text>

  <!-- Big temperature -->
  <text x="100" y="85" font-size="52" font-weight="600" fill="#f1f5f9">{temp}°C</text>
  <text x="102" y="108" font-size="13" fill="#64748b">terasa {feels}°C · {temp_min}°–{temp_max}°</text>

  <!-- Condition -->
  <text x="102" y="130" font-size="15" font-weight="500" fill="#94a3b8">{esc(condition)}</text>

  <!-- Divider -->
  <line x1="24" y1="148" x2="{W-24}" y2="148" stroke="#1e293b" stroke-width="1"/>

  <!-- Metrics grid: 3 columns x 3 rows -->
'''

metrics = [
    ("💧 Humidity",   f"{humidity}%",          ""),
    ("🌬️ Wind",       f"{wind_speed} m/s",      f"dari {wind_dir}"),
    ("👁️ Visibility", f"{visibility} km",       ""),
    ("☁️ Clouds",     f"{clouds}%",             ""),
    ("🌫️ Pressure",   f"{pressure} hPa",        ""),
    ("🌧️ Rain (1h)",  rain_str,                 ""),
    ("🌅 Sunrise",    sunrise,                  "WIB"),
    ("🌇 Sunset",     sunset,                   "WIB"),
    ("🏭 Air Quality", aqi_label,               f"AQI {aqi}" if aqi else ""),
]

cols = 3
cell_w = (W - 48) // cols
cell_h = 46
start_y = 162

for i, (label, val, sub) in enumerate(metrics):
    col = i % cols
    row = i // cols
    x = 24 + col * cell_w
    y = start_y + row * cell_h

    # Cell background
    svg += f'  <rect x="{x}" y="{y}" width="{cell_w-8}" height="{cell_h-6}" rx="8" fill="#1e293b"/>\n'

    # Special AQI color
    if label == "🏭 Air Quality" and aqi:
        svg += f'  <rect x="{x+2}" y="{y+2}" width="3" height="{cell_h-10}" rx="1.5" fill="{aqi_color}"/>\n'

    svg += f'  <text x="{x+10}" y="{y+16}" font-size="10" fill="#475569">{esc(label)}</text>\n'
    svg += f'  <text x="{x+10}" y="{y+32}" font-size="14" font-weight="500" fill="#e2e8f0">{esc(val)}</text>\n'
    if sub:
        svg += f'  <text x="{x+10+len(str(val))*8+4}" y="{y+32}" font-size="10" fill="#475569">{esc(sub)}</text>\n'

svg += f'''
  <!-- Footer -->
  <text x="{W//2}" y="{H-12}" font-size="11" fill="#334155" text-anchor="middle">⚙️ Auto-updated via GitHub Actions · {esc(updated)}</text>

</svg>'''

with open("card.svg", "w", encoding="utf-8") as f:
    f.write(svg)

print("card.svg generated successfully")

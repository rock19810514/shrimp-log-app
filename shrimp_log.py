import streamlit as st
import pandas as pd
import requests
import os
from datetime import datetime
from pathlib import Path

st.set_page_config(page_title="釣蝦紀錄 App", page_icon="🦐", layout="wide")
st.title("🦐 釣蝦紀錄 App")

# 日期
date = st.date_input("📅 日期", value=datetime.today())

# 座釣時間
start_time = st.time_input("🎣 座釣開始時間")
end_time = st.time_input("🎣 座釣結束時間")

# 座釣時長（手動填寫）
duration = st.text_input("🕒 座釣時長（例如 3 小時）")

# 場地與類別
place = st.text_input("📍 釣蝦場地點")
shrimp_type = st.selectbox("🦐 釣蝦類別", ["公蝦", "綜合蝦", "母蝦", "其它(可自行填寫)"])

# 配方與備註
bait = st.text_input("🧂 配方")
note = st.text_input("📝 備註")

# 釣獲量分成斤與兩
col1, col2 = st.columns(2)
with col1:
    jin = st.number_input("🎣 釣獲量（斤）", min_value=0, step=1)
with col2:
    liang = st.number_input("🎣 釣獲量（兩）", min_value=0, step=1, max_value=15)

# 自動抓取 GPS
lat = st.text_input("📍 緯度 (Latitude)")
lon = st.text_input("📍 經度 (Longitude)")
if st.button("📍 自動填入GPS位置"):
    try:
        res = requests.get("https://ipinfo.io/json")
        if res.status_code == 200:
            data = res.json()
            loc = data["loc"].split(",")
            lat = loc[0]
            lon = loc[1]
            st.success(f"取得位置成功：{lat}, {lon}")
        else:
            st.warning("無法取得 GPS 資訊")
    except Exception as e:
        st.error(f"發生錯誤：{e}")

# 抓取天氣資料（含氣壓）
weather_info = {}
def get_weather(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&current="
        f"temperature_2m,relative_humidity_2m,precipitation,pressure_msl&timezone=auto"
    )
    try:
        res = requests.get(url)
        if res.status_code == 200:
            current = res.json().get("current", {})
            return {
                "氣溫": f"{current.get('temperature_2m')}°C",
                "濕度": f"{current.get('relative_humidity_2m')}%",
                "降雨": f"{current.get('precipitation')} mm",
                "氣壓": f"{current.get('pressure_msl')} hPa"
            }
    except:
        return {}
    return {}

if lat and lon:
    weather_info = get_weather(lat, lon)
    if weather_info:
        st.info("🌤️ 天氣資訊：" + ", ".join([f"{k}: {v}" for k, v in weather_info.items()]))
    else:
        st.warning("⚠️ 無法取得天氣資料")

# 儲存資料
def save_record():
    file_path = "shrimp_log.csv"
    record = {
        "日期": date.strftime("%Y/%m/%d"),
        "開始時間": start_time.strftime("%H:%M"),
        "結束時間": end_time.strftime("%H:%M"),
        "時長": duration,
        "釣蝦場地": place,
        "釣蝦類別": shrimp_type,
        "配方": bait,
        "釣獲量_斤": jin,
        "釣獲量_兩": liang,
        "備註": note,
        "緯度": lat,
        "經度": lon,
        **weather_info
    }
    df = pd.DataFrame([record])
    if os.path.exists(file_path):
        df.to_csv(file_path, mode='a', header=False, index=False)
    else:
        df.to_csv(file_path, index=False)

if st.button("💾 儲存紀錄"):
    save_record()
    st.success("✅ 已儲存紀錄！")

# 顯示歷史紀錄
if Path("shrimp_log.csv").exists():
    st.markdown("## 📊 所有釣蝦紀錄")
    df = pd.read_csv("shrimp_log.csv")
    st.dataframe(df)
import streamlit as st
import pandas as pd
import requests
import datetime
import matplotlib.pyplot as plt

st.set_page_config(page_title="釣蝦紀錄", layout="wide")

st.title("🦐 釣蝦紀錄 App")

# 初始化 CSV 路徑
file_path = "shrimp_log.csv"

# 初始化輸入欄位
with st.form("shrimp_form"):
    col1, col2 = st.columns(2)
    with col1:
        timestamp = st.date_input("日期", datetime.date.today())
        fishing_time = st.text_input("🎣 座釣時間（如 13:00~17:00）")
        location = st.text_input("📍 釣蝦場地點")
        shrimp_type = st.selectbox("🦐 釣蝦類別", ["公蝦", "綜合蝦", "母蝦", "其它"])
    with col2:
        bait_formula = st.text_input("🧪 配方")
        weight = st.number_input("📏 釣獲斤數", min_value=0.0, step=0.1)
        note = st.text_input("📝 備註")
        get_weather = st.form_submit_button("☁️ 取得天氣資料")

    # 經緯度輸入（手動）
    lat = st.text_input("緯度 (Latitude)", "")
    lon = st.text_input("經度 (Longitude)", "")

    # 取得天氣資料
    weather_info = {}
    if get_weather and lat and lon:
        api_key = "bfba88273a1a9d6d6530a5073cdf928f"
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&lang=zh_tw&appid={api_key}"
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            weather_info = {
                "天氣狀況": data["weather"][0]["description"],
                "溫度（°C）": data["main"]["temp"],
                "濕度（%）": data["main"]["humidity"],
                "氣壓（hPa）": data["main"]["pressure"]
            }
            st.success("✅ 成功取得天氣資料")
        else:
            st.error("❌ 天氣資料取得失敗，請檢查 API Key 或經緯度")

    submitted = st.form_submit_button("✅ 儲存紀錄")
    if submitted:
        new_data = {
            "時間": timestamp,
            "座釣時間": fishing_time,
            "地點": location,
            "釣蝦類別": shrimp_type,
            "配方": bait_formula,
            "斤數": weight,
            "備註": note
        }
        new_data.update(weather_info)
        df_new = pd.DataFrame([new_data])
        df_new.to_csv(file_path, mode='a', index=False, header=not Path(file_path).exists())
        st.success("✅ 已儲存紀錄")

# 顯示紀錄與圖表
st.markdown("---")
st.header("📊 所有釣蝦紀錄")
try:
    df_all = pd.read_csv(file_path)
    st.dataframe(df_all, use_container_width=True)

    if "斤數" in df_all.columns:
        df_all["時間"] = pd.to_datetime(df_all["時間"])
        df_grouped = df_all.groupby(df_all["時間"].dt.date)["斤數"].sum().reset_index()
        plt.figure(figsize=(10, 4))
        plt.plot(df_grouped["時間"], df_grouped["斤數"], marker="o")
        plt.title("每日釣獲斤數趨勢")
        plt.xlabel("日期")
        plt.ylabel("斤數")
        st.pyplot(plt)
except Exception as e:
    st.warning(f"⚠️ 無法讀取紀錄檔：{e}")

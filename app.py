import streamlit as st
import pandas as pd
import sqlite3
import altair as alt

# タイトル
st.title("Garminアクティビティビューア")

# データベース接続
conn = sqlite3.connect('garmin_activities.db')
df = pd.read_sql_query('SELECT * FROM activities', conn)
# dfからstart_rat,start_long,stop_lat,stop_longを削除
df.drop(columns=['start_lat', 'start_long', 'stop_lat', 'stop_long'], inplace=True)
# データプレビュー
if st.checkbox("データを表示する"):
    st.dataframe(df)

# 日付でフィルター
st.subheader("期間を選んでフィルター")
start_date = st.date_input("開始日", pd.to_datetime(df['start_time']).min())
end_date = st.date_input("終了日", pd.to_datetime(df['start_time']).max())

filtered_df = df[
    (pd.to_datetime(df['start_time']) >= pd.to_datetime(start_date)) &
    (pd.to_datetime(df['start_time']) <= pd.to_datetime(end_date))
]

# 距離グラフ
st.subheader("距離の推移")
chart = alt.Chart(filtered_df).mark_line().encode(
    x='start_time:T',
    y='distance:Q'
)
st.altair_chart(chart, use_container_width=True)


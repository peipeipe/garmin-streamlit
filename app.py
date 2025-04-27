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


# ランニングの月別距離グラフ
st.title("ランニング：月別走行距離")
# ランニングだけに絞る
running_df = df[df['sport'] == 'running']

# 月ごとの集計
running_df['start_time'] = pd.to_datetime(running_df['start_time'])
running_df['year_month'] = running_df['start_time'].dt.to_period('M')

monthly_distance = running_df.groupby('year_month')['distance'].sum().reset_index()

# 単位をkmに変換
monthly_distance['distance_km'] = monthly_distance['distance']
monthly_distance['year_month_str'] = monthly_distance['year_month'].astype(str)

# Altairで棒グラフ＋ラベル
chart = alt.Chart(monthly_distance).mark_bar().encode(
    x=alt.X('year_month_str:N', title='年月'),
    y=alt.Y('distance_km:Q', title='距離 (km)'),
    tooltip=['year_month_str', 'distance_km']
).properties(
    width=700,
    height=400
)

text = chart.mark_text(
    align='center',
    baseline='bottom',
    dy=-2
).encode(
    text=alt.Text('distance_km:Q', format=".1f")
)

st.altair_chart(chart + text, use_container_width=True)
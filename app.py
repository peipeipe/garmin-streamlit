import streamlit as st
import pandas as pd
import sqlite3
import altair as alt

# タイトル
st.title("peipeipe's Garmin Data Analysis")

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

# garmin_summary.db への接続
conn_summary = sqlite3.connect('garmin_summary.db')

# days_summary テーブルからデータ取得
weight_df = pd.read_sql_query('SELECT day, weight_avg FROM days_summary', conn_summary)

# 日付型に変換
weight_df['day'] = pd.to_datetime(weight_df['day'])

# 今日から過去60日間だけフィルタ
today = pd.to_datetime('today').normalize()
past_60_days = today - pd.Timedelta(days=60)
weight_df = weight_df[(weight_df['day'] >= past_60_days) & (weight_df['day'] <= today)]

# 日付をインデックスにして、全日付を補間
weight_df = weight_df.set_index('day').asfreq('D')

# 欠損値を線形補間（自然に繋ぐ）
weight_df['weight_avg'] = weight_df['weight_avg'].interpolate()

# インデックスを戻す
weight_df = weight_df.reset_index()

# Streamlitでグラフ表示
st.header("過去60日間の体重推移")

chart = alt.Chart(weight_df).mark_line().encode(
    x=alt.X('day:T', title='日付'),
    y=alt.Y('weight_avg:Q', title='体重 (kg)', scale=alt.Scale(domain=[50, 65])),
    tooltip=['day', 'weight_avg']
).properties(
    width=700,
    height=400
)

st.altair_chart(chart, use_container_width=True)
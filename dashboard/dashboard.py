import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Set style untuk seaborn
sns.set(style='dark')

# Fungsi untuk mendapatkan total count per jam
def get_total_count_by_hour_df(hour_df):
    hour_count_df = hour_df.groupby(by="hours").agg({"count": ["sum"]}).reset_index()
    return hour_count_df

# Fungsi untuk memfilter data untuk tahun 2011 dan 2012
def count_by_day_df(day_df):
    return day_df[(day_df['datetime'] >= "2011-01-01") & (day_df['datetime'] < "2013-01-01")]

# Fungsi untuk menghitung total pengguna terdaftar
def total_registered_df(day_df):
    reg_df = day_df.groupby(by="datetime").agg({"registered": "sum"}).reset_index()
    reg_df.rename(columns={"registered": "register_sum"}, inplace=True)
    return reg_df

# Fungsi untuk menghitung total pengguna kasual
def total_casual_df(day_df):
    cas_df = day_df.groupby(by="datetime").agg({"casual": "sum"}).reset_index()
    cas_df.rename(columns={"casual": "casual_sum"}, inplace=True)
    return cas_df

# Fungsi untuk menjumlahkan order per jam
def sum_order(hour_df):
    sum_order_items_df = hour_df.groupby("hours")["count"].sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

# Fungsi untuk mendapatkan total count per musim
def jenis_season(day_df):
    return day_df.groupby(by="season")["count"].sum().reset_index()

# Load datasets
days_df = pd.read_csv("day_clean.csv")
hours_df = pd.read_csv("hour_clean.csv")

# Konversi kolom datetime ke tipe datetime
days_df["datetime"] = pd.to_datetime(days_df["datetime"])
hours_df["datetime"] = pd.to_datetime(hours_df["datetime"])

# Urutkan nilai berdasarkan datetime
days_df.sort_values(by="datetime", inplace=True)
hours_df.sort_values(by="datetime", inplace=True)

# Sidebar untuk pemilihan tanggal
with st.sidebar:
    st.image("Foto BG merah.jpeg")
    
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=days_df["datetime"].min(),
        max_value=days_df["datetime"].max(),
        value=(days_df["datetime"].min(), days_df["datetime"].max())
    )

# Filter data berdasarkan tanggal yang dipilih
main_df_days = days_df[(days_df["datetime"] >= pd.Timestamp(start_date)) & 
                        (days_df["datetime"] <= pd.Timestamp(end_date))]
main_df_hour = hours_df[(hours_df["datetime"] >= pd.Timestamp(start_date)) & 
                         (hours_df["datetime"] <= pd.Timestamp(end_date))]

# Siapkan data untuk visualisasi
hour_count_df = get_total_count_by_hour_df(main_df_hour)
day_df_count_2011 = count_by_day_df(main_df_days)
reg_df = total_registered_df(main_df_days)
cas_df = total_casual_df(main_df_days)
sum_order_items_df = sum_order(main_df_hour)
season_df = jenis_season(main_df_days)

# Header dashboard
st.header('Bike Sharing :sparkles:')

# Tampilkan metrik
st.subheader('Daily Sharing')
col1, col2, col3 = st.columns(3)

with col1:
    total_orders = day_df_count_2011["count"].sum()
    st.metric("Total Sharing Bike", value=total_orders)

with col2:
    total_registered = reg_df.register_sum.sum()
    st.metric("Total Registered", value=total_registered)

with col3:
    total_casual = cas_df.casual_sum.sum()
    st.metric("Total Casual", value=total_casual)

# Jumlah Pelanggan per Musim
st.subheader("Jumlah Pelanggan per Musim")

# Grouping terhadap season dan count
seasonal_counts = jenis_season(main_df_days)
seasonal_counts.sort_values(by='count', ascending=False, inplace=True)

# Warna untuk setiap musim
colors = {'fall': 'grey', 'summer': 'blue', 'winter': 'green', 'spring': 'grey'}

# Visualisasi
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x='season', y='count', data=seasonal_counts, palette=colors, ax=ax)
ax.set_title('Jumlah Pelanggan per Musim', loc='center', fontsize=20)
ax.set_ylabel('Jumlah Pelanggan')
ax.set_xlabel('Season')
st.pyplot(fig)

# Menampilkan musim dengan pelanggan terbanyak dan tersedikit
most_customers_season = seasonal_counts['season'].iloc[0]
least_customers_season = seasonal_counts['season'].iloc[-1]

st.write(f"Musim dengan pelanggan terbanyak: **{most_customers_season}**")
st.write(f"Musim dengan pelanggan tersedikit: **{least_customers_season}**")

# Perbandingan Data Pelanggan Tahun 2011 dan 2012
st.subheader("Perbandingan Data Pelanggan Tahun 2011 dan 2012")

# Agregasi data pelanggan per tahun
yearly_counts = days_df.groupby(days_df['datetime'].dt.year)['count'].sum()

# Data untuk pie chart
labels = yearly_counts.index.astype(str)
sizes = yearly_counts.values

# Membuat pie chart
fig1, ax1 = plt.subplots(figsize=(8, 8))
ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
ax1.axis('equal')
plt.title('Perbandingan Data Pelanggan Tahun 2011 dan 2012')
st.pyplot(fig1)

# Menampilkan penyewaan sepeda berdasarkan jam
st.subheader("Penyewaan Sepeda Berdasarkan Jam")

# Membuat bar chart untuk penyewaan sepeda berdasarkan jam
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

# Barplot untuk penyewa sepeda terbanyak
sns.barplot(x="hours", y="count", data=sum_order_items_df.head(5),
            hue="hours", palette=["#D3D3D3", "#D3D3D3", "#000000", "#D3D3D3", "#D3D3D3"], ax=ax[0], legend=False)
ax[0].set_ylabel(None)
ax[0].set_xlabel("Hours (PM)", fontsize=30)
ax[0].set_title("Jam dengan banyak penyewa sepeda", loc="center", fontsize=30)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

# Barplot untuk penyewa sepeda terdikit
sns.barplot(x="hours", y="count", data=sum_order_items_df.tail(5),
            hue="hours", palette=["#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#000000"], ax=ax[1], legend=False)
ax[1].set_ylabel(None)
ax[1].set_xlabel("Hours (AM)", fontsize=30)
ax[1].set_title("Jam dengan sedikit penyewa sepeda", loc="center", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

# Menampilkan plot
st.pyplot(fig)

# Kode RFM dimulai di sini
# Buat kolom baru untuk RFM
days_df['recency'] = (days_df['datetime'].max() - days_df['datetime']).dt.days

# Buat DataFrame RFM
rfm_df = days_df.groupby('instant').agg({'recency': 'min', 'datetime': 'count', 'count': 'sum'})
rfm_df.rename(columns={'datetime': 'frequency', 'count': 'monetary'}, inplace=True)

# Tentukan kuartil untuk setiap metrik RFM
quantiles = rfm_df.quantile(q=[0.25, 0.5, 0.75])

# Fungsi untuk memberi skor RFM
def RScore(x, p, d):
    if x <= d[p][0.25]:
        return 4
    elif x <= d[p][0.50]:
        return 3
    elif x <= d[p][0.75]:
        return 2
    else:
        return 1

def FMScore(x, p, d):
    if x <= d[p][0.25]:
        return 1
    elif x <= d[p][0.50]:
        return 2
    elif x <= d[p][0.75]:
        return 3
    else:
        return 4

# Beri skor RFM
rfm_df['r_quartile'] = rfm_df['recency'].apply(RScore, args=('recency', quantiles,))
rfm_df['f_quartile'] = rfm_df['frequency'].apply(FMScore, args=('frequency', quantiles,))
rfm_df['m_quartile'] = rfm_df['monetary'].apply(FMScore, args=('monetary', quantiles,))

# Gabungkan skor RFM menjadi satu kolom
rfm_df['RFMScore'] = rfm_df.r_quartile.map(str) + rfm_df.f_quartile.map(str) + rfm_df.m_quartile.map(str)

# Tampilkan DataFrame RFM
st.dataframe(rfm_df)

'''
Saya menggunakan dataset **superstore**, kemudian saya 
lakukan pengcekan data. Kemudian didapatkan hasil observasi sebagai berikut:
1. Dataset memiliki 21 kolom dan 9994 baris.
2. Pada kolom Order Date dan Ship Date terdapat ketidaksesuaian Dtype.
3. Tidak terdapat data duplikat dan missing value.
4. Terdapat outliers pada kolom Sales dan Profit.
5. Handling outliers dilakukan karena ketika kita memvalidasi dengan visualisasi (box plot) 
terlihat banyak sekali outliers dan bentuk dari box plot seperti dipadatkan.

Saya lakukan data cleaning pada dataset **superstore**, kemudian saya simpan dan beri nama 
datasetnya menjadi **sample_superstore**.
'''

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly. graph_objects as go
from datetime import datetime, timedelta

# Konfigurasi halaman
st.set_page_config(
    page_title="Dashboard Analisis Penjualan",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fungsi load data
@st.cache_data
def load_data():
    return pd.read_csv("dataset/sample_superstore.csv")

# Load data penjualan
df_sales=load_data()
df_sales.columns = df_sales.columns.str.lower().str.replace(' ', '_') # ubah jadi lower case
df_sales['order_date'] = pd.to_datetime(df_sales['order_date']) # ubah ke datetime
df_sales['ship_date'] = pd.to_datetime(df_sales['ship_date']) # ubah ke datetime

# Judul dashboard
st.title("Marketing Analisis Toko Superstore Online")
st.markdown("Marketing Analasis ini memberikan informasi gambaran umum **performa penjualan**, **trend**, dan distribusi berdasarkan berbagai macam dimensi")

st.sidebar.header("Filter & Navigasi")
pilihan_halaman = st.sidebar.radio(
    "Pilihan Halaman:",
    ("Overview Dashboard", "Prediksi Penjualan")
)

# Filter (yang akan muncul hanya di halaman Overview Dashboard)
if pilihan_halaman == "Overview Dashboard":
    st.sidebar.markdown("### Filter Data Dashboard")

    # Filter tanggal
    min_date = df_sales['order_date'].min().date()
    max_date = df_sales['order_date'].max().date()

    date_order = st.sidebar.date_input(
        "Pilih Order Date:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if len(date_order) == 2:
        start_date_filter = pd.to_datetime(date_order[0])
        end_date_filter = pd.to_datetime(date_order[1])

        filtered_df = df_sales[(df_sales['order_date'] >= start_date_filter) & 
                               (df_sales['order_date'] <= end_date_filter)]
    else:
        filtered_df = df_sales
    
    # Filter berdasarkan region
    selected_regions=st.sidebar.multiselect(
        "Pilih region:",
        options=df_sales['region'].unique().tolist(),
        default=df_sales["region"].unique().tolist()
    )
    filtered_df=filtered_df[filtered_df["region"].isin(selected_regions)]

    # Filter berdasarkan segment
    selected_segments=st.sidebar.multiselect(
        "Pilih segment:",
        options=df_sales['segment'].unique().tolist(),
        default=df_sales["segment"].unique().tolist()
    )
    filtered_df=filtered_df[filtered_df["segment"].isin(selected_segments)]

    # Filter berdasarkan ship_mode
    selected_ship_modes=st.sidebar.multiselect(
        "Pilih ship_mode:",
        options=df_sales['ship_mode'].unique().tolist(),
        default=df_sales["ship_mode"].unique().tolist()
    )
    filtered_df=filtered_df[filtered_df["ship_mode"].isin(selected_ship_modes)]

    # Filter berdasarkan category
    selected_categories=st.sidebar.multiselect(
        "Pilih category:",
        options=df_sales['category'].unique().tolist(),
        default=df_sales["category"].unique().tolist()
    )
    filtered_df=filtered_df[filtered_df["category"].isin(selected_categories)]

else:
    filtered_df = df_sales.copy()

# Konten halaman utama 
if pilihan_halaman == "Overview Dashboard":
    # Metrics utama
    st.subheader("Ringkasan Performa Penjualan")

    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 3, 3])

    total_sales = filtered_df['sales'].sum()
    total_profit= filtered_df['profit'].sum()
    total_orders = filtered_df['order_id'].nunique()
    total_products_sold = filtered_df['quantity'].sum()
    total_customers = filtered_df['customer_id'].nunique()
    
    with col1:
        st.metric(label="Jumlah Pelanggan", value=f"{total_customers:,}")
    with col2:
        st.metric(label="Jumlah Pesanan", value=f"{total_orders:,}")
    with col3:
        st.metric(label="Jumlah Produk Terjual", value=f"{total_products_sold:,}")
    with col4:
        st.metric(label="Total Penjualan", value=f"Rp {total_sales:,.2f}")
    with col5:
        st.metric(label="Total Profit", value=f"Rp {total_profit:,.2f}")

    # Line chart trend penjualan
    filtered_df['order_month'] = pd.to_datetime(filtered_df['order_date']).dt.to_period('M')

    sales_by_month = filtered_df.groupby('order_month')['sales'].sum().reset_index()
    
    # Memastikan urutan bulannya benar
    sales_by_month = sales_by_month.sort_values('order_month')
    sales_by_month['order_month'] = sales_by_month['order_month'].astype(str)
    
    fig_monthly_sales = px.line(
        sales_by_month,
        x='order_month',
        y='sales',
        title='Total Penjualan per Bulan'
    )
    st.plotly_chart(fig_monthly_sales, use_container_width=True)

    # Line chart trend penjualan
    profit_by_month = filtered_df.groupby('order_month')['profit'].sum().reset_index()
    
    # Memastikan urutan bulannya benar
    profit_by_month = profit_by_month.sort_values('order_month')
    profit_by_month['order_month'] = profit_by_month['order_month'].astype(str)
    
    fig_monthly_profit = px.line(
        profit_by_month,
        x='order_month',
        y='profit',
        title='Total Profit per Bulan'
    )
    st.plotly_chart(fig_monthly_profit, use_container_width=True)

     # visualisasi dengan tab, lebih detail
    st.subheader("Detailed Sales Performance")

    # Membuat tab 1, tab 2, tab 3
    tab1, tab2, tab3 = st.tabs(["Segment", "Region", "Category"])

    with tab1:
        st.write("#### Penjualan Berdasarkan Segment")

        sales_by_segment = filtered_df.groupby(
            'segment'
            )['sales'].sum().reset_index()
        
        fig_segment = px.bar(
            sales_by_segment,
            x='segment',
            y='sales',
            color='segment'
        )
        # Menampilkan bar chart
        st.plotly_chart(fig_segment, use_container_width=True)

    with tab2:
        st.write("#### Penjualan Berdasarkan Region")

        sales_by_region = filtered_df.groupby(
            'region'
        )['sales'].sum().reset_index()

        fig_region = px.bar(
            sales_by_region,
            x='region',
            y='sales',
            color='region'
        )
        st.plotly_chart(fig_region, use_container_width=True)
    
    with tab3:
        st.write("#### Penjualan Berdasarkan category")

        sales_by_category = filtered_df.groupby(
            'category'
        )['sales'].sum().reset_index()

        fig_category = px.bar(
            sales_by_category,
            x='category',
            y='sales',
            color='category'
        )
        st.plotly_chart(fig_category, use_container_width=True)

        # Membuat tab 1, tab 2, tab 3
    tab1, tab2, tab3 = st.tabs(["Segment", "Region", "Category"])

    with tab1:
        st.write("#### Jumlah Produk yang Terjual Berdasarkan Segment")

        quantity_by_segment = filtered_df.groupby(
            'segment'
            )['quantity'].sum().reset_index()
        
        fig_segment = px.bar(
            quantity_by_segment,
            x='segment',
            y='quantity',
            color='segment'
        )
        # Menampilkan bar chart
        st.plotly_chart(fig_segment, use_container_width=True)

    with tab2:
        st.write("#### Jumlah Produk yang Terjual Berdasarkan Region")

        quantity_by_region = filtered_df.groupby(
            'region'
        )['quantity'].sum().reset_index()

        fig_region = px.bar(
            quantity_by_region,
            x='region',
            y='quantity',
            color='region'
        )
        st.plotly_chart(fig_region, use_container_width=True)
    
    with tab3:
        st.write("#### Jumlah Produk yang Terjual Berdasarkan category")

        quantity_by_category = filtered_df.groupby(
            'category'
        )['quantity'].sum().reset_index()

        fig_category = px.bar(
            quantity_by_category,
            x='category',
            y='quantity',
            color='category'
        )
        st.plotly_chart(fig_category, use_container_width=True)

    # Membuat tab 1, tab 2, tab 3
    tab1, tab2, tab3 = st.tabs(["Segment", "Region", "Category"])

    with tab1:
        st.write("#### Profit Berdasarkan Segment")

        profit_by_segment = filtered_df.groupby(
            'segment'
            )['profit'].sum().reset_index()
        
        fig_segment = px.bar(
            profit_by_segment,
            x='segment',
            y='profit',
            color='segment'
        )
        # Menampilkan bar chart
        st.plotly_chart(fig_segment, use_container_width=True)

    with tab2:
        st.write("#### Profit Berdasarkan Region")

        profit_by_region = filtered_df.groupby(
            'region'
        )['profit'].sum().reset_index()

        fig_region = px.bar(
            profit_by_region,
            x='region',
            y='profit',
            color='region'
        )
        st.plotly_chart(fig_region, use_container_width=True)
    
    with tab3:
        st.write("#### Profit Berdasarkan category")

        profit_by_category = filtered_df.groupby(
            'category'
        )['profit'].sum().reset_index()

        fig_category = px.bar(
            profit_by_category,
            x='category',
            y='profit',
            color='category'
        )
        st.plotly_chart(fig_category, use_container_width=True)

    

    



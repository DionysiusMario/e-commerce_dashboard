import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

# Load Dataset
all_df = pd.read_csv("all_data.csv")

datetime_columns = ["order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date"]
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
  all_df[column] = pd.to_datetime(all_df[column])

# Menyiapkan DataFrame dengan membuat helper function
def create_byproduct_df(df):
    byproduct_df = df.groupby(by="product_category_name").order_id.nunique().reset_index()
    byproduct_df.rename(columns={
        "order_id": "order_count"
    }, inplace=True)

    return byproduct_df

def create_bycity_df(df):
    bycity_df = df.groupby(by="seller_city").order_id.nunique().reset_index()
    bycity_df.rename(columns={
        "order_id": "order_count"
    }, inplace=True)

    return bycity_df

def create_annual_orders_df(df):
    annual_orders_df = df.resample(rule='Y', on='order_approved_at').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    annual_orders_df.index = annual_orders_df.index.strftime('%Y') #mengubah format order date menjadi tahun
 
    annual_orders_df = annual_orders_df.reset_index()
    annual_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "gross_profit"
    }, inplace=True)

    return annual_orders_df

# Membuat Komponen Filter
min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()
 
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("logo.svg")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# start_date dan end_date di atas akan digunakan untuk memfilter all_df
main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) & 
                (all_df["order_approved_at"] <= str(end_date))]

# Memanggil helper function
byproduct_df = create_byproduct_df(main_df)
bycity_df = create_bycity_df(main_df)
annual_orders_df = create_annual_orders_df(main_df)

# melengkapi dashboard dengan berbagai visualisasi data
st.header('E-Commerce Public Dataset Dashboard :sparkles:')

## Subheader untuk annual orders
st.subheader('Annual Orders')
 
col1, col2 = st.columns(2)
 
with col1:
    total_orders = annual_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)
 
with col2:
    total_gross_profit = format_currency(annual_orders_df.gross_profit.sum(), "IDR ", locale='es_CO') 
    st.metric("Total Gross Profit", value=total_gross_profit)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    annual_orders_df["order_approved_at"],
    annual_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

## Subheader untuk Best & Worst Performing Products
st.subheader("Best & Worst Performing Product")
 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
 
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
 
sns.barplot(x="order_count", y="product_category_name", data=byproduct_df.sort_values(by="order_count", ascending=False).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Orders", fontsize=30)
ax[0].set_title("Best Performing Product", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)
 
sns.barplot(x="order_count", y="product_category_name", data=byproduct_df.sort_values(by="order_count", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Orders", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
 
st.pyplot(fig)

## Subheader untuk Best Cities
st.subheader("Best Performing CIties")
fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    y="order_count", 
    x="seller_city",
    data=bycity_df.sort_values(by="order_count", ascending=False).head(5),
    palette=colors,
    ax=ax
)
ax.set_title("Number of Order by Cities", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=25)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

st.caption('Copyright (c) Dionysius Mario 2023')
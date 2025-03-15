import streamlit as st
import pandas as pd
import plotly.express as px
from pymongo import MongoClient

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["your_database_name"]  # Change this to your actual database name

# Load Data
@st.cache_data
def load_data():
    booking_df = pd.DataFrame(list(db["booking_data"].find()))
    dining_df = pd.DataFrame(list(db["dining_info"].find()))
    reviews_df = pd.DataFrame(list(db["reviews_data"].find()))
    return booking_df, dining_df, reviews_df

booking_df, dining_df, reviews_df = load_data()

# Data Cleaning
for df in [booking_df, dining_df, reviews_df]:
    df.drop(columns=["_id"], errors="ignore", inplace=True)

booking_df["check_in_date"] = pd.to_datetime(booking_df["check_in_date"], errors="coerce")
dining_df["order_time"] = pd.to_datetime(dining_df["order_time"], errors="coerce")
dining_df["date"] = dining_df["order_time"].dt.date
reviews_df["review_date"] = pd.to_datetime(reviews_df["review_date"], errors="coerce")

# Streamlit App
st.title("Hotel Data Dashboard")

tab1, tab2, tab3 = st.tabs(["Bookings", "Dining", "Reviews"])

with tab1:
    st.header("Hotel Bookings Analysis")
    date_range = st.date_input("Select Date Range", [booking_df["check_in_date"].min(), booking_df["check_in_date"].max()])
    filtered_booking = booking_df[(booking_df["check_in_date"] >= pd.to_datetime(date_range[0])) &
                                  (booking_df["check_in_date"] <= pd.to_datetime(date_range[1]))]
    
    fig1 = px.line(filtered_booking.groupby(filtered_booking["check_in_date"].dt.date).size().reset_index(name="bookings"), 
                   x="check_in_date", y="bookings", title="Bookings Per Day")
    st.plotly_chart(fig1)

with tab2:
    st.header("Dining Insights")
    date_range_dining = st.date_input("Select Date Range for Dining", [dining_df["order_time"].min(), dining_df["order_time"].max()])
    filtered_dining = dining_df[(dining_df["order_time"] >= pd.to_datetime(date_range_dining[0])) &
                                 (dining_df["order_time"] <= pd.to_datetime(date_range_dining[1]))]
    
    cuisine_filter = st.multiselect("Select Preferred Cuisines", filtered_dining["Preferred Cusine"].dropna().unique())
    if cuisine_filter:
        dining_filtered = filtered_dining[filtered_dining["Preferred Cusine"].isin(cuisine_filter)]
    else:
        dining_filtered = filtered_dining
    
    fig2 = px.pie(dining_filtered, names="Preferred Cusine", values="price_for_1", title="Average Dining Cost by Cuisine")
    st.plotly_chart(fig2)

with tab3:
    st.header("Reviews Analysis")
    date_range_reviews = st.date_input("Select Date Range for Reviews", [reviews_df["review_date"].min(), reviews_df["review_date"].max()])
    filtered_reviews = reviews_df[(reviews_df["review_date"] >= pd.to_datetime(date_range_reviews[0])) &
                                   (reviews_df["review_date"] <= pd.to_datetime(date_range_reviews[1]))]
    
    fig3 = px.histogram(filtered_reviews, x='Rating', nbins=5, title="Distribution of Ratings")
    st.plotly_chart(fig3)

st.write("### Data Preview")
st.write("Bookings:")
st.dataframe(booking_df.head())
st.write("Dining:")
st.dataframe(dining_df.head())
st.write("Reviews:")
st.dataframe(reviews_df.head())

import streamlit as st
import pandas as pd
import random
import datetime
import os
from langchain_together import TogetherEmbeddings
from together import Together
from pinecone import Pinecone

df = pd.read_excel('reviews_data.xlsx')
os.environ["TOGETHER_API_KEY"] = "b8b5809a8bd9c19931da8c7d5bb21822d7425dfc70b4bb8df9d08eb081686286"

pc = Pinecone(api_key='pcsk_VUg1S_5myRgHqfcu4jjbDiNRUSGX8DPYVR91HjSRNsgMaJ9Gh8mYS5Xmxb8VfkP7UjmAk')
embeddings = TogetherEmbeddings(model="togethercomputer/m2-bert-80M-8k-retrieval")
index = pc.Index(host="hotel-reviews-szhu2vz.svc.aped-4627-b74a.pinecone.io")
client = Together()

def generate_review_id():
    return max(df["review_id"].tolist()) + random.randint(15000, 1000000)

def convert_date_to_numeric(date_str):
    return int(date_str.replace("-",""))

st.title("Customer Review Submission")

customer_id = st.text_input("Enter your Customer ID:")
review_text = st.text_area("Enter your review:")
rating = st.slider("Rating",min_value=1.0,max_value=10.0,step=0.1)
staying_now = st.radio("Are you currently staying at the hotel?", ("Yes","No"))
submit = st.button("Submit Review")

if submit and review_text and customer_id:
    new_review_id = generate_review_id()
    review_date = datetime.date.today().strftime("%Y-%m--%d")
    review_date_numeric = convert_date_to_numeric(review_date)

    new_entry = {
        "review_id": new_review_id,
        "customer_id": int(customer_id),
        "review_date": review_date,
        "Review": review_text,
        "Rating": rating,
        "review_date_numeric" : review_date_numeric,
        "staying_now": staying_now,
    }
    df = pd.concat([df,pd.DataFrame([new_entry])],ignore_index=True)
    df.to_excel("reviews_data.xlsx",index=False)

    query_embedding = embeddings.embed_query(review_text)

    metadata = {
        "customer_id": int(customer_id),
        "review_date": review_date_numeric,
        "Rating": rating,
        "review_id": new_review_id,
    }

    index.upsert(vectors=[(str(new_review_id), query_embedding,metadata)])

    st.success("Review subitted successfully!")
    st.write("Updated DataFrame:", df)
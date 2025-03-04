import streamlit as st
import pandas as pd
import os
from langchain_together import TogetherEmbeddings
from pinecone import Pinecone
from together import Together




df = pd.read_excel('reviews_data.xlsx')
os.environ["TOGETHER_API_KEY"] = "b8b5809a8bd9c19931da8c7d5bb21822d7425dfc70b4bb8df9d08eb081686286"

pc = Pinecone(api_key='pcsk_VUg1S_5myRgHqfcu4jjbDiNRUSGX8DPYVR91HjSRNsgMaJ9Gh8mYS5Xmxb8VfkP7UjmAk')
embeddings = TogetherEmbeddings(model="togethercomputer/m2-bert-80M-8k-retrieval")
index = pc.Index(host="hotel-reviews-szhu2vz.svc.aped-4627-b74a.pinecone.io")
client = Together()

st.title("🏨 Hotel Customer Sentiment Analysis 📝")
print("TOGETHER_API_KEY:",os.getenv("TOGETHER_API_KEY"))
# User inputs
query = st.text_input("Enter a query about customer reviews:", "How is the food quality?")
start_date = st.date_input("📅 Start Date")
end_date = st.date_input("📅 End Date")
rating_filter = st.slider("⭐ Select Rating Filter", 1, 10, (1, 10))

if st.button("📊 Analyze Sentiment"):
    query_embedding = embeddings.embed_query(query)

    # Convert date range to numeric format YYYYMMDD
    start_date_str = int(start_date.strftime('%Y%m%d'))
    end_date_str = int(end_date.strftime('%Y%m%d'))

    # Query Pinecone index
    results = index.query(
        vector=query_embedding,
        top_k=5,
        namespace="",
        include_metadata=True,
        filter={
            "Rating": {"$gte": rating_filter[0], "$lte": rating_filter[1]},
            "review_date": {"$gte": start_date_str, "$lte": end_date_str}
        }
    )
    matches=results["matches"]
    if not matches:
        st.warning("No reviews found matching the criteria")
    else:
        matched_ids = [int(match["metadata"]["review_id"]) for match in matches]
        req_df=df[df["review_id"].isin(matched_ids)]
        concatenated_reviews=" ".join(req_df["Review"].tolist())
        response = client.chat.completions.create(
            model="meta-llama/Llama-Vision-Free",
            messages = [{"role": "user", "content": f"""Briefly Summarize the overall sentiment of customers about food and restaurant based on these reviews - {
            concatenated_reviews}. Dont mention the name of the hotel"""}]
        )
        st.subheader("Sentiment Summary")
        st.write(response.choices[0].message.content)
        st.subheader("Matched Reviews")
        st.dataframe(df[["Review"]])



    




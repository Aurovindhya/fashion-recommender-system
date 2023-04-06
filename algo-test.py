import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import urllib.request
import webcolors
import pandas as pd
from sklearn.svm import LinearSVC
from sklearn.metrics.pairwise import cosine_similarity
import time

# download the dataset
urllib.request.urlretrieve(
    "https://github.com/Aurovindhya/fashion-recommender-system/blob/csv/myntra-data.parquet?raw=true", "myntra-data.parquet")

data = pd.read_parquet("myntra-data.parquet", engine="fastparquet")

# drop color rows which are empty
data.dropna(subset=["colors"], inplace=True)
data = data.reset_index(drop=True)

#
desc_vectorizer = TfidfVectorizer()
desc_vectorizer.fit(data["Description"])
desc_vectors = desc_vectorizer.transform(data["Description"])

category_vectorizer = TfidfVectorizer()
category_vectorizer.fit(data["Individual_category"])
cat_vectors = category_vectorizer.transform(data["Individual_category"])

svm = LinearSVC()
# create the predictor
svm.fit(desc_vectors, data["Individual_category"])


def predict_category_get_recommendations(query, price, gender):
    qvector = desc_vectorizer.transform([query])
    qcategory = svm.predict(qvector)[0]
    qcategory_vector = desc_vectorizer.transform([qcategory])
    cosine_similarities = cosine_similarity(
        desc_vectors, qcategory_vector).flatten()
    top_indices = []
    for i in cosine_similarities.argsort()[::-1]:
        if data.loc[i, "OriginalPrice (in Rs)"] <= price and data.loc[i, "category_by_Gender"].lower() == gender.lower():
            top_indices.append(i)

    top_indices = top_indices[:5]
    top_products = data.iloc[top_indices]
    return top_products


start, result = time.time(), predict_category_get_recommendations(
    "socks", 500, "men")
time_taken = time.time() - start
print(f"Total Recommendations: {result.shape[0]}")
print(f"Recomendations took: {time_taken}s")

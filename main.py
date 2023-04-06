import functions_framework
from flask import *
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import urllib.request
import time
import faiss


urllib.request.urlretrieve(
    "https://github.com/Aurovindhya/fashion-recommender-system/blob/csv/myntra-data.parquet?raw=true", "myntra-data.parquet")

data = pd.read_parquet("myntra-data.parquet", engine="fastparquet")


# Define a function to preprocess text by stemming
vectorizer = TfidfVectorizer()
gender_tfidf = TfidfVectorizer()
color_tfidf = TfidfVectorizer()

data.dropna(subset=["colors"], inplace=True)
data = data.reset_index(drop=True)
# data['stemmed_description'] = data['Description'].apply(preprocess)

vectorizer.fit(data['Individual_category'])
gender_tfidf.fit(data['category_by_Gender'])
color_tfidf.fit(data['colors'])

product_vectors = vectorizer.transform(
    data['Individual_category']).toarray().astype("float32")
gender_vec = gender_tfidf.transform(
    data['category_by_Gender']).toarray().astype("float32")
colors_vec = color_tfidf.transform(
    data['colors']).toarray().astype("float32")


combined_vec = np.concatenate(
    (product_vectors, gender_vec, colors_vec), axis=1)

d = combined_vec.shape[1]
index = faiss.IndexFlatL2(d)
index.add(combined_vec)

# print(combined_vec.shape)

# product_vectors_2 = vectorizer.transform(
#    data['Individual_category'])
# similarity_matrix = awesome_cossim_topn(
#    product_vectors_2, product_vectors_2.transpose(), ntop=1000)

# print(similarity_matrix.shape)
print("Function Ready...")


def process_recommendations(query: str, color: str, price: int, gender: str, num_recommendations=5):
    query = query.lower()
    color = color.lower()
    gender = gender.lower()

    print(product_vectors.size)
    print(
        f"Searching for '{query}' with color '{color}' and price < '{price}'")
    query_vector = vectorizer.transform(
        [query]).toarray().astype("float32")
    gender_vector = gender_tfidf.transform(
        [gender]).toarray().astype("float32")

    if (color != ""):
        colors_vector = color_tfidf.transform(
            [color]).toarray().astype("float32")
    else:
        colors_vector = np.zeros_like(
            colors_vec, shape=(1, colors_vec.shape[1]))
        # colors_vector = np.resize(zero_vec, (1, zero_vec.shape[1]))

    query_vector_new = np.concatenate(
        (query_vector, gender_vector, colors_vector), axis=1)

    print(query_vector_new.shape)
    begin = time.time()

    D, I = index.search(query_vector_new, k=250)
    results = []
    for i in I[0]:
        if price is None or data.loc[i, 'OriginalPrice (in Rs)'] <= price:
            results.append({'name': data.loc[i, 'BrandName'], 'description': data.loc[i, 'Description'],
                           'price': data.loc[i, 'OriginalPrice (in Rs)'], 'url': data.loc[i, 'URL'], 'rating': data.loc[i, 'Ratings']})
    results = sorted(results, key=lambda x: x['rating'], reverse=True)
    # print(results[:5])
    diff = time.time() - begin
    print(f"Prediction took: {diff}")
    return results[:5]


@functions_framework.http
def get_recommendations(request: Request):
    """
        HTTP Cloud Function.
        Args:
            request (flask.Request): The request object.
            <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
        Returns:
            The response text, or any set of values that can be turned into a
            Response object using `make_response`
            <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
        Note:
            For more information on how Flask integrates with Cloud
            Functions, see the `Writing HTTP functions` page.
            <https://cloud.google.com/functions/docs/writing/http#http_frameworks>
    """
    request_object = request.get_json()
    print(request_object)
    print(request_object["queryResult"]["parameters"])
    params = request_object["queryResult"]["parameters"]
    query = params["color"] + " " + params["Type"]
    price = params["price"]["amount"]
    gender = params["gender"]
    print("Generated query: " + query)
    # store starting time
    begin = time.time()

    """ def sendFollowUpIntent():
        response = {
            "followupEventInput": {
                "name": "ProductRecommendation-followup"
            }
        }
        return jsonify(response) """

    # scheduler = sched.scheduler(time.time, time.sleep)
    # scheduler.enter(4, 1, sendFollowUpIntent)

    recommendations = process_recommendations(
        params["Type"].lower(), params["color"].lower(), price, gender.lower())
    diff = time.time() - begin
    print(f"Total runtime of the program is {diff}")
    print(recommendations)
    response = "Here are some recommendations you can try:\n" if len(
        recommendations) > 0 else "I'm sorry, there are no recommendations for that criteria as of now."
    telegram_response = []
    for product in recommendations:
        response = response + "\n" + \
            product["name"] + ": " + product["description"] + \
            " - " + product["url"] + "\n\n"
        telegram_response.append({
            'text': product["name"] + ": " + product["description"],
            'url': product["url"]
        })

    response = {
        'fulfillmentText': response,
        'payload': {
            'telegram': {
                'text': f"{response}",
                'parse_mode': 'Markdown',
                'reply_markup': {
                    'inline_keyboard': [telegram_response]
                }
            }
        }
    }
    return jsonify(response)

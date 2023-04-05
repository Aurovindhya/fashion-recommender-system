import functions_framework
from flask import *

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, HashingVectorizer
from sklearn.metrics.pairwise import linear_kernel
import urllib.request
import time
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, learning_curve
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier


urllib.request.urlretrieve(
    "https://github.com/Aurovindhya/fashion-recommender-system/blob/csv/myntra-data.parquet?raw=true", "myntra-data.parquet")

data = pd.read_parquet("myntra-data.parquet", engine="fastparquet")


"""
 def ngrams(string, n=3):
    string = string.encode("ascii", errors="ignore").decode()
    string = string.lower()
    chars_to_remove = [")", "(", ".", ",", "[", "]", "{", "}", "'"]
    rx = '[' + re.escape("".join(chars_to_remove)) + "]"
    string = re.sub(rx, "", string)
    string = string.replace("&", "and")
    string = string.replace(",", " ")
    string = string.replace("-", " ")
    string = re.sub(" +", " ", string).strip()
    string = " " + string + " "
    string = re.sub(r'[,-./]|\sBD', r'', string)
    results = zip(*[string[i:] for i in range(n)])
    return ["".join(ngram) for ngram in results]
"""


"""min_df=1, analyzer=ngrams"""
vectorizer = TfidfVectorizer()


x = data['Description'].values
y = data["URL"].values

product_vectors = vectorizer.fit_transform(x)
array_tfid = product_vectors.toarray()
tfid_feature_names = vectorizer.get_feature_names_out()
X_Tfid = pd.DataFrame(product_vectors.toarray(), columns=tfid_feature_names)
x_train, x_test, y_train, y_test = train_test_split(X_Tfid, y, test_size=0.2)

knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(x_train, y_train)

y_pred = knn.predict(x_test)
print(y_pred)


# clf = SVC(kernel="linear", random_state=0)
# clf.fit(x_train, y_train)
# y_pred = clf.predict(x_test)
# print(y_pred)

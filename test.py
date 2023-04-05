
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import urllib.request
import webcolors
import pandas as pd

df = pd.read_csv('new_file.csv', low_memory=False)
df.to_parquet('myntra-data.parquet', engine="fastparquet")


def extract_colors(text):
    matches = []
    if (text == "" or text == None or type(text) != str):
        return ""
    for word in text.split():
        try:
            rgb = webcolors.name_to_rgb(word)
            matches.append(webcolors.rgb_to_name(rgb))
        except ValueError:
            pass
    if matches:
        return ' '.join(matches)
    else:
        return ''


# df['colors'] = df['Description'].apply(extract_colors)
# df.to_csv('new_file.csv', index=False)

""" df = pd.read_csv('myntra-data.csv')
n = 2500
df = df.groupby(['Individual_category', "category_by_Gender"]).head(n)
df.to_csv('new_file.csv', index=False)
 """

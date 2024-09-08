# -*- coding: utf-8 -*-
"""DL-2(Section 1).ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/16K-1vnHZWkGfZSHfUD1FAdb2iKTebZUm
"""

!pip install nltk
import nltk
nltk.download('punkt')
nltk.download('stopwords')

import numpy as np
import pandas as pd
import nltk
import re
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
from gensim.models import Word2Vec
from scipy import spatial
import networkx as nx
import csv

df = pd.read_csv('/content/medium_articles.csv')
df.head()

df = df[['title','text']]
df.shape

df = df.drop_duplicates()
df.shape

df['text'] = df['text'].str.replace('\n','<|n|>')

sample_blog = df['text'][10]
print(sample_blog)

sentences = sent_tokenize(sample_blog)
sentences_clean = [re.sub(r'[^\w\s]','',sentence.lower()) for sentence in sentences]
stop_words = stopwords.words('english')

sentence_tokens = [[words for words in sentence.split(' ') if words not in stop_words] for sentence in sentences_clean]
w2v = Word2Vec(sentence_tokens,vector_size=1, min_count=1, epochs=1000)

sentence_embeddings = [[w2v.wv.get_vector(word)[0] for word in words] for words in sentence_tokens]
max_len = max([len(tokens) for tokens in sentence_tokens])
sentence_embeddings = [np.pad(embedding,(0,max_len-len(embedding)),'constant') for embedding in sentence_embeddings]

similarity_matrix = np.zeros([len(sentence_tokens), len(sentence_tokens)])
for i, row_embedding in enumerate(sentence_embeddings):
    for j, column_embedding in enumerate(sentence_embeddings):
        similarity_matrix[i][j] = 1 - spatial.distance.cosine(row_embedding, column_embedding)

nx_graph = nx.from_numpy_array(similarity_matrix)
scores = nx.pagerank(nx_graph, max_iter=500)

top_sentence = {sentence: scores[index] for index, sentence in enumerate(sentences)}
sentNeeded = round(0.25 * len(sentences)) - 1
top = dict(sorted(top_sentence.items(), key=lambda x: x[1], reverse=True)[:sentNeeded])

summary = ""
for sent in sentences:
    if sent in top.keys():
        summary += sent
print(summary)

count = 0
def generateSummary(blog):
    global count
    count += 1
    print("Summarising blog ", count)
    try:
        sentences = sent_tokenize(blog)
        sentences_clean = [re.sub(r'[^\\w\\s]', '', sentence.lower()) for sentence in sentences]
        stop_words = stopwords.words('english')
        sentence_tokens = [[words for words in sentence.split(' ') if words not in stop_words] for sentence in sentences_clean]
        w2v = Word2Vec(sentence_tokens, vector_size=1, min_count=1, epochs=1000)
        sentence_embeddings = [[w2v.wv.get_vector(word) for word in words] for words in sentence_tokens]
        max_len = max([len(tokens) for tokens in sentence_tokens])
        sentence_embeddings = [np.pad(embedding, (0, max_len-len(embedding)), 'constant') for embedding in sentence_embeddings]
        similarity_matrix = np.zeros([len(sentence_tokens), len(sentence_tokens)])
        for i, row_embedding in enumerate(sentence_embeddings):
            for j, column_embedding in enumerate(sentence_embeddings):
                similarity_matrix[i][j] = 1 - spatial.distance.cosine(row_embedding, column_embedding)
        nx_graph = nx.from_numpy_array(similarity_matrix)
        scores = nx.pagerank(nx_graph, max_iter=600)
        top_sentence = {sentence: scores[index] for index, sentence in enumerate(sentences)}
        sentNeeded = round(0.25 * len(sentences)) - 1
        top = dict(sorted(top_sentence.items(), key=lambda x: x[1], reverse=True)[:sentNeeded])

        summary = ""
        for sent in sentences:
            if sent in top.keys():
                summary += sent
        return summary
    except:
        return float("NaN")

import csv

filename = "articlesSet.csv"
fields = ['title', 'summary', 'content']

# Writing to CSV file
with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
    # Creating a csv writer object
    csvwriter = csv.writer(csvfile)

    # Write the header if the file is empty
    if csvfile.tell() == 0:
        csvwriter.writerow(fields)

    # Define the callback function to process each row
    def callback(row):
        summary = generateSummary(row['text'])

        # Only proceed if the summary is a valid string
        if isinstance(summary, str):
            rows = [row['title'], summary, row['text']]
            csvwriter.writerow(rows)

    # Apply the callback function to each row in the DataFrame
    df.apply(callback, axis=1)
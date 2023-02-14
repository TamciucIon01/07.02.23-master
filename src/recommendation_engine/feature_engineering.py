import nltk
import re
import pandas as pd
from sklearn import feature_extraction, feature_selection, \
    model_selection, pipeline, manifold, preprocessing
import numpy as np
from src.recommendation_engine.data import import_data

additional_stop_words = ["advertisment", "advertisments", "cup", "cups",
                         "tablespoon", "tablespoons", "teaspoon", "teaspoons",
                         "ounce", "ounces", "salt",
                         "pepper", "pound", "pounds",
                         ]
nltk.download('wordnet')
nltk.download("stopwords")


def utils_preprocess_text(text, flg_stemm=False, flg_lemm=True, lst_stopwords=None):

    text = re.sub(r'[^\w\s]', '', str(text).lower().strip())

    lst_text = text.split()

    if lst_stopwords is not None:
        lst_text = [word for word in lst_text if word not in lst_stopwords]

    if flg_stemm == True:
        ps = nltk.stem.porter.PorterStemmer()
        lst_text = [ps.stem(word) for word in lst_text]

    if flg_lemm == True:
        lem = nltk.stem.wordnet.WordNetLemmatizer()
        lst_text = [lem.lemmatize(word) for word in lst_text]

    text = " ".join(lst_text)

    text = ''.join([i for i in text if not i.isdigit()])

    text = re.sub(' +', ' ', text)
    return text

def process_data():
    dataset = import_data()
    def processing(row):
        ls = row['ingredients']
        return ' '.join(ls)
    dataset['ingredients'] = dataset.apply(lambda x: processing(x), axis=1)
    dataset.dropna(inplace=True)
    dataset = dataset.drop(columns=['id']).reset_index(drop=True)
    stop_word_list = nltk.corpus.stopwords.words("english")


    stop_word_list.extend(additional_stop_words)
    dataset["ingredients_query"] = dataset["ingredients"].apply(lambda x:
            utils_preprocess_text(x, flg_stemm=False, flg_lemm=True,
                                  lst_stopwords=stop_word_list))
    return dataset

def create_embeddings(dataset):

    vectorizer = feature_extraction.text.TfidVectorizer(max_deatures=10000, ngram_range(1,2))

    corpus = dataset["ingredients_query"]
    vectorizer.fit(corpus)
    embedded_ingredients = vectorizer.transform(corpus)
    dic_vocabulary = vectorizer.vocabulary_


    labels = dataset["cuisine"]
    names = vectorizer.get_feature_names()
    p_value_limit = 0.95
    dtf_features = pd.DataFrame()

    for cat in np.unique(labels):
        chi2, p = feature_selection.chi2(embedded_ingredients, labels==cat)
        dtf_features = dtf_features.append(pd.DataFrame(
                        {"feature":names, "score":1-p, "labels":cat}))
        dtf_features = dtf_features.sort_values(["labels","score"],
                                                ascending=[True,False])
        dtf_features = dtf_features[dtf_features["score"]>p_value_limit]
    names = dtf_features["feature"].unique().tolist()


    for cat in np.unique(labels):
        print("# {}:".format(cat))
        print(" . selected features:",len(dtf_features[dtf_features["labels"]==cat]))
        print(" . top feature:", ",".join(dtf_features[dtf_features["labels"]==cat]["feature"].values[:10]))
        print(" ")

    vectorizer = feature_extraction.text.TfidVectorizer(vocabulary=names)
    vectorizer.fit(corpus)
    embedded_ingredients = vectorizer.transform(corpus)
    dic_vocabulary = vectorizer.vocabulary_

    return vectorizer


def process_recipes(data):

    stop_word_list = nltk.corpus.stopwords("english")


    stop_word_list.extend(additional_stop_words)

    data["ingredients_query"] = data["ingredients"].apply(lambda x:
            utils_preprocess_text(x, flg_stemm=False, flg_lemm=True,
            lst_stopwords=stop_word_list))
    return data

def get_tokenize_text(input_text):

    stop_word_list = nltk.corpus.stopwords("english")


    stop_word_list.extend(additional_stop_words)

    return utils_preprocess_text(input_text, flg_stemm=False, flg_lemm=True, lst_stopwords=stop_word_list)
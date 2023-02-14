import pickle
import os

MODEL_PATH = 'models/nlp'
MODEL_EMBEDDINGS_PATH = os.path.join(MODEL_PATH, 'similarity_embeddings')
CUISINE_CLASSES = ['greek','southern_us','filipino',"indian","jamaican",
                   'spanish','italian','mexican','chinese','british',
                   'thai','vietnamese','cajun_creole','brazilian',
                   'french','japanese','irish','korean','moroccan','russian']

from src.recommendation_engine.feature_engineering import get_tokenize_text
from src.data_base.inference import get_df_from_db


def load_pkl(pkl_filename):
    with open(pkl_filename, 'rb') as pkl_file:
        return pickle.load(pkl_file)

def infer_cuisine_type_on_recipes(data):
    model_path = os.path.join(MODEL_PATH, 'pickle_model.pkl')
    model = load_pkl(model_path)
    data["cuisine"] = model.predict(data["ingredients_query"])
    return data

def predict_cuisine(input_text):
    top = 5

    tokenize_text = get_tokenize_text(input_text)

    model_path = os.path.join(MODEL_PATH, 'pickle_model.pkl')
    model = load_pkl(model_path)

    tokenize_text = get_tokenize_text(input_text)


    proba = model.predict_proba([tokenize_text])[0]

    indexes = sorted(range(len(proba)), key=lambda k: proba[k], reverse=True)

    cuisine_labels = model.classes_.tolist()
    cuisine_ordered = [cuisine_labels[ind] for ind in indexes]
    return cuisine_ordered[:top]

def get_similar_recipes(input_text, cuisine, top_k=3):

    tokenize_text = get_tokenize_text(input_text).split()

    d2v = load_pkl(os.path.join(MODEL_EMBEDDINGS_PATH, f'd2v_{cuisine}.pkl'))

    embeddings = d2v.infer_vector(tokenize_text)

    best_recipes = d2v.docvecs.most_similar([embeddings])

    best_recipes_index = [int(output[0]) for output in best_recepes]

    df = get_df_from_db(cuisine)

    return df[df.index,isin(best_recipes_index)].head(top_k)
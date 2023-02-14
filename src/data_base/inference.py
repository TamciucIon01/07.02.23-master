import sqlite3 as sq
import pandas as pd
def get_df_from_db(cusine):
    db = sq.connect('recepies.db')
    sql_query = "SELECT title, instructions, ingridients, ingridients_query "\
                "FROM main_recepies WHERE cusine = ?"

    return pd.read_sql(sql_query, db, params=(cusine))
import pandas as pd
import numpy as np
import psycopg2
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from dataherald import Dataherald
from dataherald.types.sql_generation_create_params import Prompt

class DHEvaluator():
  def __init__(self, dh_client):
    self.dh_client = dh_client
    self.db_connection_id = self.dh_client.database_connections.list()[0].id
  
  def read_query_result_to_df(self, prompt, query):
    prompt = Prompt(
      text=prompt,
      db_connection_id=self.db_connection_id
      )
    sql_generation = self.dh_client.sql_generations.create(
      prompt=prompt,
      evaluate=False,
      sql=query
      )
    df = pd.DataFrame(self.dh_client.sql_generations.execute(sql_generation.id))
    return df

  def execute_query(self, prompt, query, stringify:bool=True):
    df = self.read_query_result_to_df(prompt, query).astype(str)
    if stringify:
      df['dhai_row_string'] = df.apply(lambda x : ' '.join(x.values), axis=1)
    
    return df

  def get_content_similarity(self, golden_df, result_df):
    # create the TF-IDF vectorizer
    tfidf = TfidfVectorizer(stop_words='english')

    # concatenate result_df and golden_df
    concat_results = pd.concat([golden_df['dhai_row_string'], result_df['dhai_row_string']])

    # generate cosine similarity matrix, set diagonals to 0, and keep only scores related to golden_df
    cos_sim = cosine_similarity(tfidf.fit_transform(concat_results))
    np.fill_diagonal(cos_sim, 0)
    cos_sim = cos_sim[:golden_df.shape[0], golden_df.shape[0]:]

    # get the similarity by averaging the highest scores for each row
    content_similarity = np.average(np.max(cos_sim, axis=1))
    return content_similarity

  def get_row_similarity(self, golden_df, result_df, smoothing_factor:int=0):
    # get number of rows for both DFs
    golden_rows = golden_df.shape[0] + smoothing_factor
    result_rows = result_df.shape[0] + smoothing_factor

    # custom row similarity calculation with optional LaPlace smoothing
    # row_similarity = 1 - (abs(golden_rows - result_rows) + smoothing_factor) / (max(golden_rows, result_rows) + (smoothing_factor*2))
    row_similarity = min([golden_rows, result_rows]) / max([golden_rows, result_rows])
    return row_similarity

  def get_col_similarity(self, golden_df, result_df, smoothing_factor:int=0):
    # get number of columns for both DFs
    golden_cols = golden_df.shape[1] + smoothing_factor - 1
    result_cols = result_df.shape[1] + smoothing_factor - 1

    # custom column similarity calculation with optional LaPlace smoothing
    # col_similarity = 1 - (abs(golden_cols - result_cols) + smoothing_factor) / (max(golden_cols, result_cols) + (smoothing_factor*2))
    col_similarity = min([golden_cols, result_cols]) / max([golden_cols, result_cols])
    return col_similarity

  def get_confidence_score(self, prompt, result_query, golden_queries, weights:list=[0.8, 0.1, 0.1], smoothing_factor:int=0, test:str=None):
    # create list to track similarities
    confidence_scores = []

    # generate the DataFrame for the results
    result_df = self.execute_query(prompt, result_query, True)
    if len(result_df) == 0:
      return 0
    # print("===================================")
    # print("RESULT DF")
    # print(result_df.head(1))
    # print("===================================")

    # iterate though all golden queries and generate confidence score
    for golden_query in golden_queries:
      golden_df = self.execute_query(prompt, golden_query, True)
      # print("===================================")
      # print("GOLDEN DF")
      # print(golden_df.head(1))
      # print("===================================")
      content_similarity = self.get_content_similarity(golden_df, result_df)
      row_similarity = self.get_row_similarity(golden_df, result_df, smoothing_factor)
      col_similarity = self.get_col_similarity(golden_df, result_df, smoothing_factor)
      # scores = [content_similarity, row_similarity, col_similarity]
      # final_score = np.sum(np.multiply(scores, weights))
      final_score = content_similarity * ((row_similarity + col_similarity) / 2)
      confidence_scores.append(final_score)

      # if(test == 'Are there more single family sold in seattle or condos'):
      #   print('Golden Query:')
      #   print(golden_query)
      #   print(f"Content similarity: {content_similarity}")
      #   print(f"Row similarity: {row_similarity}")
      #   print(f"Col similarity: {col_similarity}")
      #   print(f"Final score: {final_score}")
      #   print("Result DataFrame:")
      #   result_df.display()
      #   print("Reference DataFrame:")
      #   golden_df.display()

    # return the highest confidence score
    return max(confidence_scores)
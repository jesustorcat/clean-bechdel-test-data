import pandas as pd
import re
import json
import requests

# GET DATA FROM GITHUB
raw_bechdel = pd.read_csv('https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2021/2021-03-09/raw_bechdel.csv')
movies = pd.read_csv('https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2021/2021-03-09/movies.csv')

# SAVE DATA TO CSV
raw_bechdel.to_csv('raw_bechdel.csv', index=False)
movies.to_csv('movies.csv', index=False)

# READ DATA FROM CSV
raw_bechdel = pd.read_csv('raw_bechdel.csv')

# CLEAN 'title' COLUMN
def clean_title(title):
  if ', The' in title:
    title = title.replace(', The', '')
    title = 'The ' + title
  else:
    title = title.replace('&#39;', "'")
  return title.strip()

# APPLY CLEAN_TITLE FUNCTION
raw_bechdel['title'] = raw_bechdel['title'].apply(clean_title)

raw_bechdel.to_csv('raw_bechdel_clean.csv', index=False)

# READING 'movies.csv' AND CREATING 'imdb_id'
movies = pd.read_csv('movies.csv')
movies['imdb_id'] = movies['imdb'].str.replace('tt', '')
movies.to_csv('movies_clean.csv', index=False)

# DOWNLOAD JSON DATA FROM IMDb
imdb_url = 'https://raw.githubusercontent.com/brianckeegan/Bechdel/master/imdb_data.json'
imdb_response = requests.get(imdb_url)
imdb_json = imdb_response.json()

# CONVERT JSON TO DATAFRAME
imdb_df = pd.json_normalize(imdb_json)

# LOWERCASE COLUMN NAMES
imdb_df.columns = imdb_df.columns.str.lower()

# CLEAN AND TRANSFORM imdb DATA
imdb_df['metascore'] = pd.to_numeric(imdb_df['metascore'], errors='coerce')
imdb_df['imdb_rating'] = pd.to_numeric(imdb_df['imdbrating'], errors='coerce')
imdb_df['year'] = pd.to_numeric(imdb_df['year'], errors='coerce')
imdb_df['imdb_id'] = imdb_df['imdbid'].str.replace('tt', '')


movies_clean = pd.read_csv('movies_clean.csv')
movies_clean['imdb_id'] = movies_clean['imdb_id'].astype(str)
imdb_df['imdb_id'] = imdb_df['imdb_id'].astype(str)

# DROP COLUMNS FROM 'movies_clean'
columns_to_drop = ['title', 'year', 'rated', 'released', 'runtime', 'genre',
                   'director', 'writer', 'actors', 'plot', 'language', 'country',
                   'awards', 'poster', 'metascore', 'imdb_rating', 'imdb_votes',
                   'type', 'dvd', 'boxoffice', 'production', 'website', 'response']

movies_clean = movies_clean.drop(columns=columns_to_drop, errors='ignore')

# COMBINE DATAFRAMES
combo_movies = movies_clean.merge(imdb_df, on='imdb_id', how='left', suffixes=('_movies', '_imdb'))

# SAVE COMBINED DATA TO CSV
combo_movies.to_csv('movies_combined_clean.csv', index=False)

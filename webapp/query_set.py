import random
import psycopg2
import json

#questo l'ho copiato dal main
connection = psycopg2.connect(
    host="127.0.0.1",
    database="postgres",
    user="postgres",
    password=""
)

cursor = connection.cursor()
cursor.execute("SELECT tconst, title_ratings.\"numVotes\" FROM title_ratings")
movies = cursor.fetchall()

total_votes = sum([movie[1] for movie in movies])
probabilities = [movie[1] / total_votes for movie in movies]

query_set = random.choices(
    population=[movie[0] for movie in movies],
    weights=probabilities,
    k=10000
)

with open('query_set.json', 'w') as f:
    json.dump(query_set, f)

cursor.close()
connection.close()

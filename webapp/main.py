import psycopg2
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from utils import to_html_table

app = FastAPI()

# connect to local postgres db
conn = psycopg2.connect(
    host="127.0.0.1",
    database="postgres",
    user="postgres",
    password=""
)


@app.get("/", response_class=HTMLResponse)
async def root():
    # build html page with an input field and a submit button to search for a movie
    return """
        <html>
            <head>
                <title>Movie Search</title>
            </head>
            <body style="padding: 30px">
                <h1>Search for a movie</h1>
                <form action="/movies" method="get">
                    <input type="text" name="movie_name" placeholder="Movie name">
                    <input type="submit" value="Search">
                </form>
            </body>
        </html>
    """


@app.get("/movies", response_class=HTMLResponse)
async def get_movie(movie_name: str):
    try:
        cur = conn.cursor()

        # title basics table
        cur.execute(f"SELECT title_basics.tconst, title_basics.\"originalTitle\", title_basics.\"primaryTitle\", title_basics.\"startYear\", title_basics.\"endYear\", title_basics.\"genres\", title_basics.\"runtimeMinutes\", title_basics.\"isAdult\", title_basics.\"titleType\", "
                    f"title_ratings.\"averageRating\", title_ratings.\"numVotes\", "
                    f"title_akas.\"title\", title_akas.\"region\", title_akas.\"language\", title_akas.\"types\", title_akas.\"attributes\", title_akas.\"isOriginalTitle\", "
                    f"te_1.\"seasonNumber\", te_1.\"episodeNumber\", "
                    f"tb_1.\"originalTitle\" as series_title, tb_1.\"startYear\" as series_start_year, tb_1.\"endYear\" as series_end_year "
                    f"FROM title_basics "
                    f"LEFT JOIN title_ratings ON title_basics.tconst = title_ratings.tconst "
                    f"LEFT JOIN title_akas ON title_basics.tconst = title_akas.\"titleId\" "
                    f"LEFT JOIN title_episode te_1 ON title_basics.tconst = te_1.tconst "
                    f"LEFT JOIN title_basics tb_1 ON te_1.\"parentTconst\" = tb_1.tconst "
                    f"WHERE title_basics.\"tconst\" = '{movie_name}'")
        movies = cur.fetchall()

        # Extract the column names
        col_names = []
        for elt in cur.description:
            col_names.append(elt[0])

        # get casts
        casts = []
        tconsts = set()
        for movie in movies:
            if movie[0] in tconsts:
                continue

            tconsts.add(movie[0])

            cur.execute(f"SELECT title_principals.\"tconst\", name_basics.\"primaryName\", title_principals.\"category\", title_principals.\"job\", title_principals.\"characters\" "
                    f"FROM title_principals "
                    f"LEFT JOIN name_basics ON title_principals.\"nconst\" = name_basics.\"nconst\" "
                    f"WHERE title_principals.\"tconst\" = '{movie[0]}'")
            casts.append(cur.fetchall())

        cur.close()
    except Exception as e:
        return f"An error occurred: {str(e)}"

    return f"""
        <html>
            <head>
                <title>{movie_name}</title>
                <style>
                table, th, td {{
                    border: 1px solid black;
                    border-collapse: collapse;
                    text-align: center;
                }}
                </style>
            </head>
            <body style="padding: 30px">
                <h1>{movie_name}</h1>
                {to_html_table(col_names, movies)}
                <h2>Casts</h2>
                {'<br>'.join([to_html_table(['tconst', 'Name', 'Category', 'Job', 'Characters'], cast) for cast in casts]) if casts else 'No cast found.'}
            </body>            
        </html>
    """

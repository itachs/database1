from flask import Flask, render_template, request, redirect, url_for
import sqlite3

main = Flask(__name__, template_folder='src')
dataB = 'animes.db'

def init_db():
    with sqlite3.connect(dataB) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS genres (
            genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
            genre_name TEXT NOT NULL
            )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS animes (
            anime_id INTEGER PRIMARY KEY AUTOINCREMENT,
            genre_id INTEGER,
            title TEXT NOT NULL,
            episodes_watched INTEGER ,
            review TEXT ,
            rating INTEGER CHECK (rating BETWEEN 1 AND 5) ,
            watched_date DATE ,
            FOREIGN KEY (genre_id) REFERENCES genres(genre_id)
            )''')
        conn.commit()

@main.route('/add', methods=['POST'])
def add_anime():
    title = request.form['title']
    genre_name = request.form['gen']
    episodes_watched = request.form['episodes_watched']
    review = request.form['review']
    rating = request.form['rating']
    watched_date = request.form['watched_date']

    with sqlite3.connect(dataB) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT genre_id FROM genres WHERE genre_name = ?', (genre_name,))
        genre = cursor.fetchone()
        
        if genre:
            genre_id = genre[0]
        else:
            cursor.execute('''INSERT INTO genres (genre_name) 
                           VALUES (?)''', (genre_name,))
            genre_id = cursor.lastrowid

        cursor.execute('''INSERT INTO animes (genre_id, title, episodes_watched, review, rating, watched_date)
                       VALUES (?, ?, ?, ?, ?, ?)''', (genre_id, title, episodes_watched, review, rating, watched_date))
        conn.commit()
    return redirect(url_for('index'))

@main.route('/delete/<int:id>')
def delete_anime(id):
    with sqlite3.connect(dataB) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM animes WHERE anime_id = ?', (id,))
        conn.commit()
    return redirect(url_for('index'))

@main.route('/edit/<int:id>', methods=['GET'])
def edit_anime(id):
    with sqlite3.connect(dataB) as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT animes.anime_id, animes.title, animes.episodes_watched, animes.review, animes.rating, animes.watched_date, genres.genre_name
                       FROM animes
                       JOIN genres ON animes.genre_id = genres.genre_id
                       WHERE animes.anime_id = ?''', (id,))
        anime = cursor.fetchone()

    if anime:
        return render_template('edit.html', anime=anime)
    return redirect(url_for('index'))

@main.route('/update/<int:id>', methods=['POST'])
def update_anime(id):
    title = request.form['title']
    genre_name = request.form['genre']
    episodes_watched = request.form['episodes_watched']
    review = request.form['review']
    rating = request.form['rating']
    watched_date = request.form['watched_date']

    with sqlite3.connect(dataB) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT genre_id FROM genres WHERE genre_name = ?', (genre_name,))
        genre = cursor.fetchone()
        
        if genre:
            genre_id = genre[0]
        else:
            cursor.execute('INSERT INTO genres (genre_name) VALUES (?)', (genre_name,))
            genre_id = cursor.lastrowid

        cursor.execute('''UPDATE animes 
                       SET title = ?, genre_id = ?, episodes_watched = ?, review = ?, rating = ?, watched_date = ?
                       WHERE anime_id = ?''', (title, genre_id, episodes_watched, review, rating, watched_date, id))
        conn.commit()
    return redirect(url_for('index'))

@main.route('/')
def index():
    with sqlite3.connect(dataB) as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT animes.anime_id, animes.title, animes.episodes_watched, animes.review, animes.rating, animes.watched_date, genres.genre_name
                       FROM animes
                       JOIN genres ON animes.genre_id = genres.genre_id
                       ORDER BY genres.genre_name, animes.title''')
        animes = cursor.fetchall()
        genresArry = {}
        
        for anime in animes:
            genre = anime[6]
            if genre not in genresArry:
                genresArry[genre] = []
            genresArry[genre].append(anime)
            
    return render_template('index.html', genres=genresArry)

@main.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_title = request.form['search_title']
        
        with sqlite3.connect(dataB) as conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT animes.anime_id, animes.title, animes.episodes_watched, animes.review, animes.rating, animes.watched_date, genres.genre_name
                           FROM animes
                           JOIN genres ON animes.genre_id = genres.genre_id
                           WHERE animes.title LIKE ?
                           ORDER BY animes.title''', ('%' + search_title + '%',))
            animes = cursor.fetchall()
        return render_template('search.html', animes=animes)
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()  
    main.run(debug=True)

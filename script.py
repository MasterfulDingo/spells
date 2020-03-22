import sqlite3
from flask import Flask, render_template, url_for
app = Flask(__name__)

posts = [ #context for making context
    {
        'author' : 'lachlan row',
        'title' : 'first post',
        'content' : 'first post content',
        'date_posted' : 'february 10 2020'
    },
    {
        'author' : 'john doe',
        'title' : 'second post',
        'concent' : 'second post concent',
        'date posted' : 'april 1 2020'
    }
]

@app.route("/")
@app.route("/home")
def hello():
    return render_template('home.html', posts=posts)

@app.route('/all_spells')
def all_spells():

    conn = sqlite3.connect('spells.db')
    cur = conn.cursor()
    cur.execute('SELECT name FROM spell')
    results = cur.fetchall()

    return render_template('all_spells.html', spells=results)

@app.route('/spell/<path:id>')
def spell(id):
    conn = sqlite3.connect('spells.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM spell WHERE id == "{}"'.format(id))
    results = cur.fetchall()

    return render_template('spell.html', spell=results)


if __name__ == "__main__":
    app.run(debug=True)
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
    resultsfinal = 'spell name: {} <br> level: {} concentration: {} ritual: {} components: <br> {} range: {} casting time: {} duration: {} damage: {} <br><br> description: {}'
    conn = sqlite3.connect('spells.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM spell WHERE id == "{}"'.format(id))
    #resultsfinal = cur.fetchall()
    resultscrude = cur.fetchall()
    resultscrudetuple = resultscrude[0]
    rcl = list(resultscrudetuple)

    resultsfinal = resultsfinal.format(rcl[1],rcl[3],rcl[4],rcl[5],rcl[6],rcl[8],rcl[10],rcl[9],rcl[7],rcl[2])
    return render_template('spell.html', spell=resultsfinal)


if __name__ == "__main__":
    app.run(debug=True)
import sqlite3
from flask import Flask, render_template, url_for
app = Flask(__name__)

entfields = ['id','name','description','level','components','concentration','ritual','damage','range','duration','casting time','school']

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
    cur.execute('SELECT id, name FROM spell')
    results = cur.fetchall()

    return render_template('all_spells.html', spells=results)

@app.route('/spell/<path:id>')
def spell(id):
    conn = sqlite3.connect('spells.db')
    cur = conn.cursor()
    cur.execute('SELECT spell.id, spell.name, spell.description, spell.level, spell.components, spell.concentration, spell.ritual, spell.damage, range.name, duration.name, castingtime.name, school.name FROM spell INNER JOIN range ON range.id = spell.range INNER JOIN duration ON duration.id = spell.duration INNER JOIN castingtime ON castingtime.id = spell.castingtime INNER JOIN school ON school.id = spell.school WHERE spell.id == "{}"'.format(id))
    result = cur.fetchall()
    
    spell = list(result[0])
    spell[2] = spell[2].split('\n')

    return render_template('spell.html', spell=spell)


if __name__ == "__main__":
    app.run(debug=True)
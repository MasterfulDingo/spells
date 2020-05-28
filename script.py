import sqlite3
from flask import Flask, render_template, url_for
app = Flask(__name__)

entfields = ['id','name','description','level','components','concentration','ritual','damage','range','duration','casting time','school']


@app.route("/")
@app.route("/home")
def hello():
    return render_template('home.html')

@app.route('/all_spells')
def all_spells():

    conn = sqlite3.connect('spells.db')
    cur = conn.cursor()
    cur.execute('SELECT spell.id, spell.name, spell.level, castingtime.name, duration.name, range.name, spell.damage FROM spell INNER JOIN range ON range.id = spell.range INNER JOIN castingtime ON castingtime.id = spell.castingtime INNER JOIN duration ON duration.id = spell.duration')
    results = cur.fetchall()
    conn.close()

    return render_template('all_spells.html', spells=results)

@app.route('/spell/<path:id>')
def spell(id):
    conn = sqlite3.connect('spells.db')
    cur = conn.cursor()
    cur.execute('SELECT spell.id, spell.name, spell.description, spell.level, spell.components, spell.concentration, spell.ritual, spell.damage, range.name, duration.name, castingtime.name, school.name FROM spell INNER JOIN range ON range.id = spell.range INNER JOIN duration ON duration.id = spell.duration INNER JOIN castingtime ON castingtime.id = spell.castingtime INNER JOIN school ON school.id = spell.school WHERE spell.id == "{}"'.format(id))
    result = cur.fetchall()
    
    spell = list(result[0])
    spell[2] = spell[2].split('\n')
    conn.close()
    
    return render_template('spell.html', spell=spell)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == "__main__":
    app.run(debug=True)
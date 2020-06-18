import sqlite3
from flask import Flask, render_template, url_for, redirect, request
from forms import SpellSearchForm

#importing the basics

app = Flask(__name__) #defining the app to run through flask

allentfields = ['id','name','description','level','components','concentration','ritual','damage','range','duration','casting time','school'] #entry fields in db in order, to be seen whether this is required.
entfields = [['level','0','1','2','3','4','5','6','7','8','9'],['school','abjuration','conjuration','divination','enchantment','evocation','illusion','necromancy','transmutation'],['concentration','no','yes'],['ritual','no','yes']]

@app.route("/")
@app.route("/home") #either of these will return user to the correct site
def hello():
    return render_template('home.html') #runs 

@app.route('/all_spells')
def all_spells():
    sql = "SELECT spell.id, spell.name, spell.level, castingtime.name, duration.name, range.name, spell.damage FROM spell INNER JOIN range ON range.id = spell.range INNER JOIN castingtime ON castingtime.id = spell.castingtime INNER JOIN duration ON duration.id = spell.duration"
    single = False
    results = db_func(sql,single)

    return render_template('all_spells.html', spells=results, entfields=entfields)

@app.route('/spell/<path:id>') #while there is a slight risk of people being able to do nasty things by sticking sql on the end of the link, i'm not sure how to counter it, so i'll leave it for now.
def spell(id):
    sql = "SELECT spell.id, spell.name, spell.description, spell.level, spell.components, spell.concentration, spell.ritual, spell.damage, range.name, duration.name, castingtime.name, school.name FROM spell INNER JOIN range ON range.id = spell.range INNER JOIN duration ON duration.id = spell.duration INNER JOIN castingtime ON castingtime.id = spell.castingtime INNER JOIN school ON school.id = spell.school WHERE spell.id == {}".format(id) #the sql query, complete with joins. the format inserts the id of the spell in the database, and therefore returns all relevant information about it for the page.
    single = True #only want one result
    spell = list(db_func(sql,single)) #runs the sql command, and turns the resultant tuple into a list to allow later formatting
    spell[2] = spell[2].split('\n') #splits up the description by python spaces, so it can be properly formatted with flask, as the python was not being picked up by the html side.
    return render_template('spell.html', spell=spell) #passes data through to flask template and magic happens

@app.route('/about', methods=('GET','POST')) #defines methods available to this route 
def about(): #the function itself
    if request.method == 'POST': #if the method being attempted is 'POST'
        var = request.form['var'] #then var will be the result of the form named 'var'

        return render_template('about.html', var=var) #returns the template, with var defined as whatever the user imput previously.

    return render_template('about.html') #returns the template normally


        
def db_func(sql,single):
    conn=sqlite3.connect("spells.db") #connects to database
    cur=conn.cursor() #creates cursor
    cur.execute(sql) #executes the sql command required with the cursor
    result=cur.fetchone() if single else cur.fetchall() #returns a single tuple if that is all that is required, or a list of tuples if more are needed.
    conn.commit #commits any changes made to the database with the sql.
    conn.close
    return result


if __name__ == "__main__":
    app.run(debug=True)
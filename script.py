import sqlite3
from flask import Flask, render_template, url_for, redirect, request, make_response
from flask_sqlalchemy import SQLAlchemy
from forms import SpellSearchForm
import json

#importing the basics

app = Flask(__name__) #defining the app to run through flask

allentfields = ['id','name','description','level','components','concentration','ritual','damage','range','duration','casting time','school'] #entry fields in db in order, to be seen whether this is required.
entfields = [['level','0','1','2','3','4','5','6','7','8','9'],['school','abjuration','conjuration','divination','enchantment','evocation','illusion','necromancy','transmutation'],['concentration','no','yes'],['ritual','no','yes']]

@app.route("/")
@app.route("/home") #either of these will return user to the correct site
def hello():
    return render_template('home.html') #returns the home html file

@app.route('/all_spells')
def all_spells():
    sql = "SELECT spell.id, spell.name, spell.level, castingtime.name, duration.name, range.name, spell.damage FROM spell INNER JOIN range ON range.id = spell.range INNER JOIN castingtime ON castingtime.id = spell.castingtime INNER JOIN duration ON duration.id = spell.duration" #sql used to gather information for this page
    single = False #we want a list of results, not just the top one
    spells = db_func(sql,single) #sending the sql to my sql function

    return render_template('all_spells.html', spells=spells, entfields=entfields) #returns template with data to be presented

@app.route('/spell/<id>') #while there is a slight risk of people being able to do nasty things by sticking sql on the end of the link, i'm not sure how to counter it, so i'll leave it for now.
def spell(id):
    sql = "SELECT spell.id, spell.name, spell.description, spell.level, spell.components, spell.concentration, spell.ritual, spell.damage, range.name, duration.name, castingtime.name, school.name FROM spell INNER JOIN range ON range.id = spell.range INNER JOIN duration ON duration.id = spell.duration INNER JOIN castingtime ON castingtime.id = spell.castingtime INNER JOIN school ON school.id = spell.school WHERE spell.id == {}".format(id) #the sql query, complete with joins. the format inserts the id of the spell in the database, and therefore returns all relevant information about it for the page.
    single = True #only want one result
    spell = db_func(sql,single) #runs the sql command
    if spell == False:
        return render_template('404.html'), 404 #if the data is not in the database, the page cannot be created, so return 404 error
    spell[2] = spell[2].split('\n') #splits up the description by python spaces, so it can be properly formatted with flask, as the python was not being picked up by the html side.
    return render_template('spell.html', spell=spell) #passes data through to flask template and magic happens

@app.route('/about', methods=('GET','POST')) #defines methods available to this route 
def about(): #the function itself
    sql = "SELECT spell.id, spell.name FROM spell" 
    spellnames = db_func(sql,single=False) #getting the names of every spell
    if request.method == 'POST': #if the method being attempted is 'POST'
        var = request.form['var'] #then var will be the result of the form named 'var'
        
        return render_template('about.html', entfields=entfields, var=var, spellnames=spellnames) #returns the template, with var defined as whatever the user imput previously.

    return render_template('about.html', entfields=entfields, spellnames=spellnames) #returns the template normally

@app.route('/search', methods=('GET','POST'))
def search():
    sql = "SELECT spell.id, spell.name, spell.level, castingtime.name, duration.name, range.name, spell.damage FROM spell INNER JOIN range ON range.id = spell.range INNER JOIN castingtime ON castingtime.id = spell.castingtime INNER JOIN duration ON duration.id = spell.duration" #!!!!!! MOVE THIS BEHIND THE IF STATEMENT !!!!!
    spells = db_func(sql,single=False)
    if request.method == 'POST':
        var = request.form.getlist('param')
        sqlparams = filtermfunc(var)
        sql = "{} {}".format(sql,sqlparams)
        spells = db_func(sql, single=False)
        return render_template('search.html', entfields=entfields, spells=spells, var=var)

    return render_template('search.html', entfields=entfields, spells=spells)

@app.errorhandler(404) #note that I have explicitly stated that this route is related to the 404 error, and i am using the errorhandler function, not the route function
def page_not_found(e):
    return render_template('404.html'), 404 #returns the error page

def db_func(sql,single):
    conn=sqlite3.connect("spells.db") #connects to database
    cur=conn.cursor() #creates cursor
    try: #if the data called for is not in the database, an error will occur ("Nonetype" is not iterable). this try/except statement catches the error when it is throw up, and returns a "false" so the original function can return a 404 errorpage.
        cur.execute(sql) #executes the sql command required with the cursor
        if single == True: #returns a single tuple if that is all that is required, and turns it into a list
            result = cur.fetchone()
            result = list(result) #converts tuple to list
        else: #returns a list of tuples, which are then turned into lists
            result = cur.fetchall()
            for i in range(len(result)):
                result[i-1] = list(result[i-1])
        #result=cur.fetchone() if single else cur.fetchall() one line function, does not convert tuples to lists
    except:
        return False
    
    conn.commit #commits any changes made to the database with the sql.
    conn.close
    return result


def filtermfunc(filterraw):
    sql = []
    for term in filterraw:
        term = term.split("_")
        if term[0] == "school":
            for school in entfields[1]:
                if term[1] == school:
                    term[1] = entfields[1].index(term[1])
        elif term[0] == "concentration" or term[0] == "ritual":
            if term[1] == "no":
                term[1] = "0"
            elif term[1] == "yes":
                term[1] = "1"
        paramsingle = "spell.{} = {}".format(term[0],term[1])
        sql.append(paramsingle)
    sqlstring = str(" AND ".join(sql))
    sqlstring = " WHERE {}".format(sqlstring)
    return sqlstring

if __name__ == "__main__":
    app.run(debug=True)
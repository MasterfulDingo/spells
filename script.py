#importing a number of extensions which are used in the code
import sqlite3
from flask import Flask, render_template, url_for, redirect, request, make_response
import json

#importing the basics

app = Flask(__name__) #defining the app to run through flask

allentfields = ['id','name','description','level','components','concentration','ritual','damage','range','duration','casting time','school'] #entry fields in db in order, to be seen whether this is required.
entfields = [['level','0','1','2','3','4','5','6','7','8','9'],['school','abjuration','conjuration','divination','enchantment','evocation','illusion','necromancy','transmutation'],['concentration','no','yes'],['ritual','no','yes'],['casters','bard','cleric','druid','paladin','ranger','sorcerer','warlock','wizard']]
casters = ["bard","cleric","druid","paladin","ranger","sorcerer","warlock","wizard"]

@app.route("/home") #either of these will return user to the correct site
@app.route("/")
def hello():
    return render_template('home.html') #returns the home html file

@app.route('/all_spells')
def all_spells():
    sql = "SELECT spell.id, spell.name, spell.level, castingtime.name, duration.name, range.name, spell.damage FROM spell INNER JOIN range ON range.id = spell.range INNER JOIN castingtime ON castingtime.id = spell.castingtime INNER JOIN duration ON duration.id = spell.duration" #sql used to gather information for this page
    single = False #we want a list of results, not just the top one
    spells = db_func(sql,single) #sending the sql to my sql function

    return render_template('all_spells.html', spells=spells, entfields=entfields) #returns template with data to be presented

@app.route('/spell/<id>') 
@app.route('/class/spell/<id>')
def spell(id):
    try:
        int(id)
    except:
        return render_template('404.html'), 404 #making sure no nasty code can be tacked onto the end of the URL to cause data breaches
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
        var = request.form.getlist('param') #getting a list of all of the selected parameters on the page
        sqlparams = filtermfunc(var)
        sql = "{} {}".format(sql,sqlparams) #joining the original all-selecting sql statement with the SQL-ordered parameters that the sqlparams function returns
        spells = db_func(sql, single=False) #doing the SQL thing! woooooo!
        return render_template('search.html', entfields=entfields, spells=spells)

    return render_template('search.html', entfields=entfields, spells=spells)

@app.route('/class')
def classes():
    sql = "SELECT caster.id, caster.name, caster.description FROM caster"
    casters = db_func(sql, single=False)
    return render_template('all_classes.html', casters = casters)

@app.route('/class/<classname>')
def classsing(classname):
    castersql = "SELECT caster.name, caster.description FROM caster WHERE caster.id = {}"
    spellsql = "SELECT spell.id, spell.name, spell.level, castingtime.name, duration.name, range.name, spell.damage FROM spell INNER JOIN range ON range.id = spell.range INNER JOIN castingtime ON castingtime.id = spell.castingtime INNER JOIN duration ON duration.id = spell.duration WHERE spell.id IN (SELECT sid FROM spellcaster WHERE cid = {})"
    if classname in casters:
        casterid = entfields[4].index(classname)
        castersql = castersql.format(casterid)
        caster = db_func(castersql, single = True)
        spellsql = spellsql.format(casterid)
        spells = db_func(spellsql, single = False)
        return render_template('class.html', caster = caster, spells = spells)
    else:
        return render_template("404.html"), 404
    

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
    sql = [] #setting up some empty lists and variables for use in formatting the returned data.
    schools = []
    schoolstr = "spell.school IN ({})"

    levels = []
    levelstr = "spell.level IN ({})"

    concentration = []
    concentrationstr = "spell.concentration IN ({})"

    ritual = []
    ritualstr = "spell.ritual IN ({})"

    caster = []
    casterstr = "spell.id IN (SELECT sid FROM spellcaster WHERE cid == {})" #nested SQL query, gathering all of the spell ids from the joining table "spellcaster" where the caster id matches that of the id given, which is gathered later in the function.

    for term in filterraw: #iterates through the returned terms from the form in the "search" page
        term = term.split("_") #splits each term by the underscore, as they were connected when being sent from the webpage. this gives us the first term, the column name in the database in the table "spells", and the value that we want to search by, which will need formatting in the following functions.
        if term[0] == "school": 
            term[1] = entfields[1].index(term[1]) #finds the entry in the second list of the list "entfields" established at the start of this file that matches the current term being analysed, then takes the index of said matching entry and replaces the two. This works because though python is a 0 index language, I have the field name (not a value) in the 0 index position.
            schools.append(str(term[1])) #turns the index into a string and puts it in the list
        elif term[0] == "level": 
            levels.append(str(term[1])) 
        elif term[0] == "casters":
            term[1] = entfields[4].index(term[1]) #this acts much the same as the function used at the start of this if statement for schools, gathering the index of the matching term in the fifth list in the main list 'entfields' and later comparing it to the caster id in the joining table
            caster.append(casterstr.format(str(term[1]))) #for each spellcaster, a different list of spells must be returned, so the sql string used before is combined together with OR parameters. The database will only return the information for each spell once, so if multiple classes can cast the same spell there is no problem
        elif term[0] == "concentration":
            term[1] = (entfields[2].index(term[1]))-1 #with concentration and ritual, in the database they are represented as 0 and 1, so i must subtract one from their indexes in the list "entfields"
            concentration.append(str(term[1]))
        elif term[0] == "ritual":
            term[1] = (entfields[3].index(term[1]))-1
            ritual.append(str(term[1]))

    #these four statements take an input of whether there is anything in the list, and if there are then joins the altered terms into a string and adds the string to the list of completed strings
    if schools: 
        schoolstr = schoolstr.format(", ".join(schools))
        sql.append(schoolstr)
    if levels:
        levelstr = levelstr.format(", ".join(levels))
        sql.append(levelstr)
    if caster:
        casterstr = " OR ".join(caster) #joining the nested SQL queries with OR statements so it returns the spells that are available to any of the selected classes
        sql.append(casterstr)
    if concentration:
        concentrationstr = concentrationstr.format(", ".join(concentration))
        sql.append(concentrationstr)
    if ritual:
        ritualstr = ritualstr.format(", ".join(ritual))
        sql.append(ritualstr)
    sqlstring = str(" AND ".join(sql)) #joins the completed strings together via SQL conventions
    sqlstring = " WHERE {}".format(sqlstring) #throws a "WHERE" on the front to make the statement a parameter! this SQL parameter is now complete!
    return sqlstring

if __name__ == "__main__":
    app.run(debug=True)
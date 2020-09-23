#importing a number of extensions which are used in the code
from flask import Flask, render_template, url_for, redirect, request, make_response


#importing functions from other python files to fulfil vital tasks.
from dbconnect import db_func
from sqlformat import filtermfunc



app = Flask(__name__) #defining the app to run through flask

#this list contains a number of lists which have the database column name in the first position and the possible values of the entry following.
entfields = [['level','0','1','2','3','4','5','6','7','8','9'],['school','abjuration','conjuration','divination','enchantment','evocation','illusion','necromancy','transmutation'],['concentration','no','yes'],['ritual','no','yes'],['casters','bard','cleric','druid','paladin','ranger','sorcerer','warlock','wizard']]


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
    try: #try and except statement checks to see if the id in the url can be a route
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


@app.route('/class') #this route returns a webpage for a number of classes, with information on each and a link to their own page.
def classes():
    sql = "SELECT caster.id, caster.name, caster.description FROM caster"
    casters = db_func(sql, single=False)
    return render_template('all_classes.html', casters = casters)


@app.route('/class/<classname>')
def classsing(classname):
    castersql = "SELECT caster.name, caster.description FROM caster WHERE caster.id = {}"
    spellsql = "SELECT spell.id, spell.name, spell.level, castingtime.name, duration.name, range.name, spell.damage FROM spell INNER JOIN range ON range.id = spell.range INNER JOIN castingtime ON castingtime.id = spell.castingtime INNER JOIN duration ON duration.id = spell.duration WHERE spell.id IN (SELECT sid FROM spellcaster WHERE cid = {})" #many-many SQL query, with nested parameters
    if classname in entfields[4][1:]: #checking if it's in the list in "entfields" from the 1 index on (0 index is the name of the field)
        casterid = entfields[4].index(classname) #takes id of matching entry and replaces name with it
        castersql = castersql.format(casterid) 
        caster = db_func(castersql, single = True) 
        spellsql = spellsql.format(casterid) #puts the id of the caster into the many-many SQL query
        spells = db_func(spellsql, single = False)
        return render_template('class.html', caster = caster, spells = spells)
    else:
        return render_template("404.html"), 404
    

@app.errorhandler(404) #note that I have explicitly stated that this route is related to the 404 error, and i am using the errorhandler function, not the route function
def page_not_found(e):
    return render_template('404.html'), 404 #returns the error page


if __name__ == "__main__":
    app.run(debug=True)
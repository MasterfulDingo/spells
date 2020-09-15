#this list contains a number of lists which have the database column name in the first position and the possible values of the entry following.
entfields = [['level','0','1','2','3','4','5','6','7','8','9'],['school','abjuration','conjuration','divination','enchantment','evocation','illusion','necromancy','transmutation'],['concentration','no','yes'],['ritual','no','yes'],['casters','bard','cleric','druid','paladin','ranger','sorcerer','warlock','wizard']]


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
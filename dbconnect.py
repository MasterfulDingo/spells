#importing sqlite three so i can connect with my database through it in this particular file
import sqlite3 


def db_func(sql,single):
    conn=sqlite3.connect("spells.db") #connects to database
    cur=conn.cursor() #creates cursor
    try: #if the data called for is not in the database, an error will occur ("Nonetype" is not iterable). this try/except statement catches the error when it is throw up, and returns a "false" so the original function can return a 404 errorpage.
        cur.execute(sql) #executes the sql command required with the cursor
        if single == True: #returns a single tuple if that is all that is required, and turns it into a list
            result = cur.fetchone()
            result = list(result)
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
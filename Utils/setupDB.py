import mysql.connector


# Function to run .sql file
def executeScriptsFromFile(filename):
    fd = open(filename, 'r')
    sqlFile = fd.read()
    fd.close()

   
    sqlCommands = sqlFile.split(';')
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",  # change as per your requirement
        passwd="root",  # change as per your requirement
    )
    c = mydb.cursor()

    # Execute command from the input file
    for command in sqlCommands:
        try:
            c.execute(command)
        except (mysql.connector.Error) as e:
            print(e)
    mydb.commit()
    mydb.close()


# Setting up the database
executeScriptsFromFile('LibraryDB.sql')


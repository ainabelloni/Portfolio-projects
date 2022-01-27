import mysql.connector

dbconn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="ainabelloni",
    database="restaurant"
)

dbcur = dbconn.cursor()

def table_available(g):
    # checks if there are available tables and which is the one available
    dbcur.execute("select number_table,seats "
                  "from dining_table "
                  "where seats>=%s and available='Y'"
                  "order by seats asc" % g)
    res = dbcur.fetchall()
    if len(res) == 0:
        return 0
    else :
        return res[0][0]

def check_reservation(phone,name):
    # checks if there are reservations in general
    sql = "select number_table,guests,seats,phone,name_guest " \
          "from dining_table natural join reservation"
    dbcur.execute(sql)
    res = dbcur.fetchall()

    if len(res)==0:
        return 0

    elif phone=="all" and name=="all" and len(res)!=0:
        return 1

    # checks if there is a reservation with the name or number given
    else:
        dbcur.execute("select number_table "
                  "from reservation "
                  "where name_guest='%s' or phone='%s'" % (name,phone))

        res = dbcur.fetchall()

        if len(res)==0:
            return 0

        else:
            return res[0][0]

def update_r(g,phone,name):
    # sets the variable available='N' for the table of the new reservation made
    num_table=table_available(g)
    dbcur.execute("update dining_table "
                  "set available='N' "
                  "where number_table=%s" % num_table)
    dbconn.commit()

    # updates the database with a new reservation line
    query = "INSERT INTO reservation (guests, phone, name_guest, number_table) " \
            "VALUES (%s, %s, %s, %s)"
    val = (g, phone, name, num_table)
    dbcur.execute(query, val)
    dbconn.commit()

def show_reservation(name_phone):
    # shows all the reservations if the parameter is "all"
    sql = "select number_table,guests,seats,phone,name_guest " \
          "from dining_table natural join reservation"
    dbcur.execute(sql)
    res = dbcur.fetchall()

    if len(res)==0 and name_phone=="all": # if the query gives no results
        print("No result(s)")

    elif name_phone == "all":
        for i in range(0, dbcur.rowcount):
            print(res[i][0], res[i][1], res[i][2], res[i][3], res[i][4])

    # shows the reservation information for the name/phone given
    else :
        for i in range(0, len(res)):
            if name_phone == res[i][3] or name_phone == res[i][4]:
                print(res[i][0],res[i][1],res[i][2],res[i][3],res[i][4])

def delete(name_phone):
    # sets for the reservation i want to drop, the table as available='Y'
    dbcur.execute("update dining_table "
                  "set available='Y' "
                  "where number_table=%s" % check_reservation(name_phone,name_phone))
    dbconn.commit()
    # drop the reservation from the database, given the name or the phone number
    dbcur.execute("delete from reservation "
                  "where name_guest='%s' or phone='%s'" % (name_phone,name_phone))
    dbconn.commit()

def unreserved_tables():
    # shows all the unreserved tables, with available='Y'
    sql = "select number_table,seats " \
          "from dining_table " \
          "where available='Y'"
    dbcur.execute(sql)
    res = dbcur.fetchall()

    for i in range(0, dbcur.rowcount):
        print(res[i][0], res[i][1])

    # print "No results" if there is no table unreserved
    if dbcur.rowcount == 0:
        print("No result(s)")

def reserved_tables(g):
    # shows the number of all the reserved tables
    if g=="all":
        sql = "select count(*) " \
              "from dining_table " \
              "where available='N'"
        dbcur.execute(sql)
        return dbcur.fetchall()[0][0]

    # shows the number of reserved tables with the number of guests given as parameter
    else:

        sql = "select count(*) " \
              "from dining_table natural join reservation " \
              "where available='N' and guests=%s"
        dbcur.execute(sql % g)
        return dbcur.fetchall()[0][0]

def guests():
    # total number of  guests contained in the reservation db
    dbcur.execute("select sum(guests) from reservation")
    res = dbcur.fetchall()[0][0]

    if res == None: # if the query gives no results
        return 0
    else:
        return res

def seats():
    # total number of seats of the restaurant
    dbcur.execute("select sum(seats) from dining_table")
    res = dbcur.fetchall()[0][0]
    return res

def max_unreserved():
    # max number of unreserved seats for a table
    query = "select max(seats-(case when guests is null then 0 else guests end)) " \
            "from dining_table natural left join reservation"

    dbcur.execute(query)
    return dbcur.fetchall()[0][0]

def gu():
    # shows number_table, guests, seats for those tables with the maximum unreserved seats
    sql = "select number_table, " \
          "(case when guests is null then 0 else guests end) as g," \
          "seats " \
          "from dining_table natural left join reservation " \
          "having seats-g=%s"
    dbcur.execute(sql % max_unreserved())
    res = dbcur.fetchall()
    for i in range(0, dbcur.rowcount):
        print(res[i][0], res[i][1], res[i][2])

def gr():
    # shows number_table, guests, seats for those reserved tables with the maximum unreserved seats
    sql = "select number_table, guests, seats " \
          "from dining_table natural join reservation " \
          "where seats-guests=(select max(seats-guests) " \
          "                    from dining_table natural join reservation);"
    dbcur.execute(sql)
    res = dbcur.fetchall()

    for i in range(0, dbcur.rowcount):
        print(res[i][0], res[i][1], res[i][2])

def main():

    command = "None" # set priorly the variable command
    while command!="X":

        act = str(input(">")).split(sep=" ") # command input for the user
        command=act[0] # correspond to the first letter(s) wrote by the userv, which indicates the function

        if command=="R" and len(act)==4: # R = reservation

            if table_available(int(act[1]))==0 or check_reservation(act[2],act[3]) != 0:
                print("Error") # if there reservation with the same nameor phone -> error
                               # if there aren't available tables for the number of guests requested -> error
            else:
                update_r(int(act[1]),act[2],act[3])
                dbconn.commit()

        elif command=="S" and len(act)==2: # S = show reservation

            if show_reservation==0 or check_reservation(act[1],act[1])==0:
                print("Error") # if there is no reservation with this name/phone
            else:
                show_reservation(act[1])

        elif command=="C" and len(act)==2: # C = cancel reservation

            if check_reservation(act[1],act[1])==0:
                print("Error") # if there is no reservation with this name/phone

            else:
                delete(act[1])

        elif command=="L" and len(act)==1: # L = list all reservations

            show_reservation("all")

        elif command=="U" and len(act)==1: # U = information of unreserved_tables

            unreserved_tables()

        elif command=="NT":

            if len(act)==1:   # NT = number of reserved tables
                print(reserved_tables("all"))

            elif len(act)==2:  # NT g = number of reserved tables with g guests
                print(reserved_tables(act[1]))

            else:
                print("Error")

        elif command=="NG" and len(act)==1: # NG = total number of guests

            print(guests())

        elif command=="NU" and len(act)==1: # NU = total number of unreserved seats

            print(seats()-guests())

        elif command=="GU" and len(act)==1: # GU = tables with max number of unreserved seats

            gu()

        elif command=="GR" and len(act)==1: # GR = reserved tables with max number of unreserved seats

            if check_reservation("all","all")==0: # no results if there is no reservation
                print("No result(s)")

            else:
                gr()

        elif command=="X": # X = EXIT from the program
            dbconn.close()
            exit()

        else: # if the command is another letter/word it's an error
            print("Error")

    dbconn.commit()
    dbconn.close()

main()
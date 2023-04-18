import sqlite3

def insertroomfree():
    con=sqlite3.connect("kldatabase.db")
    cur=con.cursor()
    cur.execute("drop table roomfree;")
    cur.execute("create table roomfree(room,day,hour);")
    res=cur.execute("select DISTINCT room from timetable where room!='';")
    x=res.fetchall()
    print(len(x))
    for i in x:
            res1=cur.execute("select day,hour from timetable where room='"+i[0]+"' AND modeofstudy!='SELF LEARNING';")
            x2=res1.fetchall()
            for z in x2:
                if len(z)>0:
                    cur.execute("insert into roomfree values('"+i[0]+"','"+z[0]+"','"+z[1]+"');")

            con.commit()

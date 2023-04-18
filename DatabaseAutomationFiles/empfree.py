import sqlite3

def insertemployeefree():
    con=sqlite3.connect("kldatabase.db")
    cur=con.cursor()
    cur.execute("drop table employeefree;")
    cur.execute("create table employeefree(faculty,day,hour);")
    res=cur.execute("select DISTINCT faculty from timetable where faculty!='-';")
    x=res.fetchall()
    print(len(x))
    for i in x:
        res1=cur.execute("select day,hour from timetable where faculty='"+i[0]+"' AND modeofstudy!='SELF LEARNING';")
        x2=res1.fetchall()
        for z in x2 :
            if len(z)>0:
                cur.execute("insert into employeefree values('"+i[0]+"','"+z[0]+"','"+z[1]+"');")
    con.commit()

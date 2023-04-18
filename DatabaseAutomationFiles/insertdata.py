import sqlite3
import pandas as pd
import empfree
import roomfree
import aicte
import exams

data_xls=pd.read_csv('studentslist_allyears_Jan2.csv',na_filter=True,header=None)
data_xls=data_xls.drop(0)
data_xls=data_xls.values.tolist()
print(data_xls[0])

con=sqlite3.connect("kldatabase.db")
cur=con.cursor()
con.execute("drop table studentcourses")
con.execute("drop table timetable")
cur.execute("create table studentcourses(id,coursecode,ltps,coursename,section)")


for li in data_xls:
    cur.execute("insert into studentcourses values("+"'"+str(li[1])+"'"+","+"'"+str(li[3])+"'"+","+"'"+str(li[4])+"'"+","+"'"+str(li[5])+"'"+","+"'"+str(li[7])+"'"+")")
con.commit()
con.close()

data_xls=pd.read_excel('2022-23 EVEN SEM CSE HONORS ALL YEARS TT ON 02-01-2023.xlsx','COMPLETE TIMETABLE')
data_xls=data_xls.values.tolist()
print(data_xls[1])
con=sqlite3.connect("kldatabase.db")
cur=con.cursor()
cur.execute("create table timetable(coursecode,shortname,ltps,section,faculty,facultysection,day,hour,time,room,shiftedto,modeofstudy)")


for li in data_xls:
    cur.execute("insert into timetable values("+"'"+str(li[1])+"'"+","+"'"+str(li[3])+"'"+","+"'"+str(li[5])+"'"+","+"'"+str(li[7])+"'"+","+"'"+str(li[9])+"'"+","+"'"+str(li[10])+"'"+","+"'"+str(li[11])+"'"+","+"'"+str(li[12])+"'"+","+"'"+str(li[13])+"'"+","+"'"+str(li[14])+"'"+","+"'"+str(li[15])+"'"+","+"'"+str(li[16])+"'"+")")
con.commit()

empfree.insertemployeefree();
roomfree.insertroomfree();
aicte.insertaicte();
exams.insertexams();

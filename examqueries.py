import sqlite3
from datetime import datetime as date
import pandas as pd
import matplotlib.pylab as plt
from pandas.plotting import table
from pytz import timezone
import matplotlib.image as image
from datetime import timedelta
from PIL import Image
from io import BytesIO
import os

def getempexams(str1,day):
    con=sqlite3.connect("/home/nvsai/mysite/kldatabase.db")
    cur=con.cursor()
    dayx=date.now(timezone("Asia/Kolkata"))
    print(day)
    res=cur.execute("select * from facultyduties where empid='"+str1+"' and date='"+str(day)+"';")
    x=res.fetchall()
    timet=[]
    if len(x)>0:
        for i in x:
            timet.append(i)
    timet=pd.DataFrame(timet,columns=['Venue','strength','Emp Id','Emp Name','Date','Time','Nature of Duty'])
    timet=timet.drop(['strength'],axis=1)
    timet=timet[['Emp Id','Emp Name','Date','Venue','Time','Nature of Duty']]
    rp=timet['Venue'].to_list()
    tims=timet['Time'].to_list()
    print(tims)
    roomseats=[]
    for i in range(0,len(rp)):
        x=rp[i].strip(" ")
        print(x)
        if os.path.exists("/home/nvsai/mysite/roomseatings/"+x+".jpg") and tims[i].count("9") and day=="2023-04-10":
            byt=BytesIO()
            im=Image.open("/home/nvsai/mysite/roomseatings/"+x+".jpg")
            im.save(byt,format='PNG')
            byt.seek(0)
            print(x)
            roomseats.append(byt)
    timet.index+=1
    po=0
    fig, ax = plt.subplots(figsize=(15,5+po))
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)

    ax.set_frame_on(False)
    ax.set_title(str1+"    "+"    "+str(dayx),weight='bold')
    ax.text(0.2,0.1,'Instructions:\n1. All invigilators are instructed to report at C606A (CSEH Examination Cell) half an hour prior to the examination time.\n2. No student should allow to leave the examination hall 30 mins before to the closure of the exam.\n3. Invigilators must ensure every student get signature & booklet number in the signature sheet provided by examination section.\n4. Any issues should bring to the notice of examination section.',fontsize=9,fontweight='bold')
    ax.text(0.2,0,'Bot Built by: Student Lead - Mr.Naga Venkata Sai( 2000030558 )       Faculty Mentor - Dr.K.Ashesh',fontsize= 7,color='blue',fontweight='bold')
    im = image.imread('/home/nvsai/mysite/klcsehon-original.jpeg')

    im2 = image.imread('/home/nvsai/mysite/rpalogo.png')
    newax = fig.add_axes([0.1,0.8,0.2,0.2], anchor='NE', zorder=1)
    newax2 = fig.add_axes([0.7,0.8,0.2,0.2], anchor='NE', zorder=1)
    newax.imshow(im)
    newax.axis('off')
    newax2.imshow(im2)
    newax2.axis('off')
    try:
        tab = table(ax, timet,cellLoc='center', loc='center')
    except Exception as e:
        plt.close(fig)
        print("Empty table")
        return False
    tab.scale(1,2)
    tab.auto_set_font_size(False)
    tab.auto_set_column_width(col=list(range(len(timet.columns))))
    tab.set_fontsize(10)
    buf = BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    img = buf
    img.seek(0)
    plt.close(fig)
    return img,roomseats

def getstuexams(str1):
    con=sqlite3.connect("/home/nvsai/mysite/kldatabase.db")
    cur=con.cursor()
    res=cur.execute("select * from studentcourses where ltps='L' and id='"+str1+"';")
    myli=res.fetchall()
    dayx=date.now(timezone("Asia/Kolkata"))
    day=dayx.strftime("%Y-%m-%d")
    print(day)
    timet=[]
    for li in myli:
        res=cur.execute("select * from studentdetails where coursecode='"+li[1]+"' and fromid<='"+str1+"' and toid>='"+str1+"' and date='"+str(day)+"';")
        x=res.fetchall()
        if len(x)>0:
            for i in x:
                timet.append(i)

    timet=pd.DataFrame(timet,columns=['Venue','CourseCode','CourseName','FromId','ToId','Total','Date','Time'])
    timet=timet.drop(['Total'],axis=1)
    timet=timet.drop(['FromId'],axis=1)
    timet=timet.drop(['ToId'],axis=1)
    timet=timet[['CourseCode','CourseName','Date','Venue','Time']]
    print(timet)
    rp=timet['Venue'].to_list()
    tims=timet['Time'].to_list()
    print(tims)
    roomseats=[]
    for i in range(0,len(rp)):
        x=rp[i].strip(" ")
        if os.path.exists("/home/nvsai/mysite/roomseatings/"+x+".jpg") and tims[i].count('9') and day=="2023-04-10":
            byt=BytesIO()
            im=Image.open("/home/nvsai/mysite/roomseatings/"+x+".jpg")
            im.save(byt,format='PNG')
            byt.seek(0)
            print(x)
            roomseats.append(byt)
    timet.index+=1
    po=0
    fig, ax = plt.subplots(figsize=(15,5+po))

    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)

    ax.set_frame_on(False)
    ax.set_title(str1+"    "+"    "+str(dayx),weight='bold')
    ax.text(0.9,0.5,'Bot Built by: \n Student Lead - Mr.Naga Venkata Sai \n                          ( 2000030558 ) \n Faculty Mentor - Dr.K.Ashesh',fontsize= 7,fontweight='bold')
    ax.text(0.2,0.1,'Instructions:\n1. Students are expected to in time for the examination. No student will be allowed after 30 min to the commencement of exam.\n2. Students are not permitted to leave the examination hall before 30 mins to the closure of the exam.\n3. Any case of copying, malpractice, discussion in the examination hall will be punished as per department and university norms.',fontsize=9,fontweight='bold')

    im = image.imread('/home/nvsai/mysite/klcsehon-original.jpeg')

    im2 = image.imread('/home/nvsai/mysite/rpalogo.png')
    newax = fig.add_axes([0.1,0.8,0.2,0.2], anchor='NE', zorder=1)
    newax2 = fig.add_axes([0.7,0.8,0.2,0.2], anchor='NE', zorder=1)
    newax.imshow(im)
    newax.axis('off')
    newax2.imshow(im2)
    newax2.axis('off')
    try:
        tab = table(ax, timet,cellLoc='center', loc='center')
    except Exception as e:
        plt.close(fig)
        print("Empty table")
        return False
    tab.scale(1,2)
    tab.auto_set_font_size(False)
    tab.auto_set_column_width(col=list(range(len(timet.columns))))
    tab.set_fontsize(10)
    buf = BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    img = buf
    img.seek(0)
    plt.close(fig)
    return img,roomseats

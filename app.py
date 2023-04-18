from flask import Flask
from flask import request
from flask import Response, make_response
import requests
import sqlite3
from datetime import datetime as date
from datetime import timedelta
import pandas as pd
import matplotlib.pylab as plt
from pandas.plotting import table
from PIL import Image
from io import BytesIO
from pytz import timezone
import matplotlib.image as image
import csv
from io import StringIO
import examqueries

TOKEN = ""
"""tok1: 

tok2: """
app = Flask(__name__)

def parse_message(message):
    print("message-->",message)
    chat_id = message['message']['chat']['id']
    txt = message['message']['text']
    print("chat_id-->", chat_id)
    print("txt-->", txt)
    txt=txt.lower()
    return chat_id,txt

def parse_query_message(message):
    print("message-->",message)
    chat_id = message['callback_query']['from']['id']
    query_id = message['callback_query']['id']
    txt = message['callback_query']['message']['reply_markup']['inline_keyboard'][0][0]['callback_data']
    return chat_id,txt,query_id

def tel_send_document(chat_id, text):
    url = f'https://api.telegram.org/bot{TOKEN}/sendDocument?chat_id={chat_id}'
    files={'document':text}
    r = requests.post(url,files=files)
    return r

def tel_send_message(chat_id, text):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {
                'chat_id': chat_id,
                'text': text
                }

    r = requests.post(url,json=payload)
    return r

def tel_send_button(chat_id,text,btxt):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {
                'chat_id': chat_id,
                'text': btxt,
                "reply_markup": {
        'inline_keyboard':  [[{'text':'Previous',
                    'callback_data':'prev+'+text}]]
    }
                }
    payload2 = {
                'chat_id': chat_id,
                'text': "Click on Next button for Tommorrows's timetable",
                "reply_markup": {
        'inline_keyboard':  [[{'text':'Next',
                    'callback_data':'next+'+text}]]
    }
                }

    r = requests.post(url,json=payload)
    r = requests.post(url,json=payload2)
    return r

def send_table(chat_id, txt):
    con=sqlite3.connect("/home/nvsai/mysite/kldatabase.db")
    cur=con.cursor()
    str1=txt
    day=date.now(timezone("Asia/Kolkata")).strftime("%A")
    dayx=date.now(timezone("Asia/Kolkata"))
    if 'next+' in txt:
        command,txt=txt.split("+")
        dayx=dayx + timedelta(1)
        day=dayx.strftime("%A")
        print(txt)
    elif 'next' in txt:
        if len(txt.split(" "))==3:
            command1,command2,txt=txt.split(" ")
            txt=command2+" "+txt
        elif len(txt.split(" "))==2:
            command1,txt=txt.split(" ")
        dayx=dayx + timedelta(1)
        day=dayx.strftime("%A")
        print(txt)
    if 'prev+' in txt:
        command,txt=txt.split("+")
        dayx=dayx - timedelta(1)
        day=dayx.strftime("%A")
        print(txt)
    elif 'prev' in txt:
        if len(txt.split(" "))==3:
            command1,command2,txt=txt.split(" ")
            txt=command2+" "+txt
        elif len(txt.split(" "))==2:
            command1,txt=txt.split(" ")
        dayx=dayx - timedelta(1)
        day=dayx.strftime("%A")
        print(txt)
    if day=="Monday":
        day="MON"
    if day=="Tuesday":
        day="TUE"
    if day=="Wednesday":
        day="WED"
    if day=="Thursday":
        day="THUR"
    if day=="Friday":
        day="FRI"
    if day=="Saturday":
        day="SAT"
    timet=[]
    print(day)
    if day=="Sunday" and "aicte" not in txt:
        tel_send_message(chat_id,"It's sunday!")
        return 1
    if 'emp' in txt:
        command,idx=txt.split(" ")
        str1=idx
        res1=cur.execute("select * from timetable where faculty='"+str1+"' AND day='"+day+"';")
        x=res1.fetchall()
        print(x)
        if len(x)>0:
            for i in x:
                timet.append(i)
    elif 'room' in txt:
        command,idx=txt.split(" ")
        str1=idx.upper()
        res1=cur.execute("select * from timetable where day='"+day+"' AND room='"+str1+"';")
        x=res1.fetchall()
        print(x)
        if len(x)>0:
            for i in x:
                timet.append(i)
    elif 'aicte' in txt:
        command,idx=txt.split(" ")
        res=cur.execute("select * from aictecohort where id='"+str(idx)+"';")
        x=res.fetchall()
        if len(x)!=0:
            tel_send_message(chat_id,"Congratlations you have registered for cohort-4 AICTE Virtual Internship.")
        timet=[]
        timet.append(x[0])
    else:
        str1=txt
        res=cur.execute("select * from studentcourses where id='"+str1+"';")
        myli=res.fetchall()
        for li in myli:
            if li[2]=="L":
                ltps="LECTURE"
            if li[2]=="P":
                ltps="PRACTICAL"
            if li[2]=="T":
                ltps="TUTORIAL"
            if li[2]=="S":
                ltps="SKILL"
            sec=''.join(i for i in li[4] if i.isdigit())
            sec='S'+str(sec)
            res1=cur.execute("select * from timetable where coursecode='"+li[1]+"'AND ltps='"+ltps+"'AND section='"+sec+"' AND day='"+day+"';")
            x=res1.fetchall()
            print(x)
            if len(x)>0:
                for i in x:
                    timet.append(i)

    pd.set_option('display.max_columns', 10)
    pd.options.display.max_columns = 10
    li=[' ','a']
    if 'aicte' not in txt:
        timet=pd.DataFrame(timet,columns=['coursecode','Shortname','LTPS','Section','EmpID','Faculty section','day','hour','timings','room','shiftedto','modeofstudy'])
        timet['hour']=timet['hour'].apply(pd.to_numeric)
        timet=timet.sort_values('hour')
        timet=timet.drop_duplicates(subset='hour', keep="first")
        timet=timet.set_index('hour')
        timet=timet.drop(['Faculty section'],axis=1)
        timet=timet.rename_axis('hour')
        timet=timet[['timings','room','shiftedto','coursecode','Shortname','LTPS','Section','EmpID','modeofstudy']]
        timet=timet.replace('nan',' ')
        li=timet['shiftedto'].values.tolist()
        print(len(li))
    else:
        timet=pd.DataFrame(timet,columns=['Sno','Student Id','Domain name'])
        timet=timet.drop(['Sno'],axis=1)
    if li.count(' ')==len(li):
        timet=timet.drop(['shiftedto'],axis=1)
    if len(timet)>=10:
        po=len(timet)-9
    else:
        po=0
    fig, ax = plt.subplots(figsize=(13, 5+po))

    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)

    ax.set_frame_on(False)
    ax.set_title(str1+"    "+"    "+str(dayx),weight='bold')


    im = image.imread('/home/nvsai/mysite/klcsehon-original.jpeg')
    if 'aicte' not in txt:
        im2 = image.imread('/home/nvsai/mysite/rpalogo.png')
        ax.text(0.9,0.8,'Bot Built by: \n Student Lead - Mr.Naga Venkata Sai \n                          ( 2000030558 ) \n Faculty Mentor - Dr.K.Ashesh',fontsize= 7,fontweight='bold')
    else:
        im2 = image.imread('/home/nvsai/mysite/asm-aicte-approved.jpg')
        ax.text(0.8,0.5,'COHORT-4 AICTE Virtual Internship',fontsize= 9,fontweight='bold')
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
    url = f'https://api.telegram.org/bot{TOKEN}/sendPhoto?chat_id={chat_id}'
    files = {"photo": img}
    requests.post(url, files=files)
    return True

@app.route('/aicte',methods=['GET','POST'])
def aicte():
    global TOKEN
    TOKEN=""
    if request.method == 'POST':
        if request.method == 'POST':
            msg = request.get_json()
            if 'callback_query' in msg:
                print("Got call back")
                chat_id,txt,query_id=parse_query_message(msg)
            else:
                try:
                    chat_id,txt = parse_message(msg)
                    print(txt)
                except Exception as e:
                    try:
                        chat_id = msg['message']['chat']['id']
                        tel_send_message(chat_id,"Sorry message type not supported! \n If this result is wrong, feel free to contact \n rpa.techclub@kluniversity.in ")
                        return Response('ok', status=200)
                    except Exception as e:
                        return Response('ok', status=200)
            if txt == "/start" or txt== "hi" or txt=="hello":
                tel_send_message(chat_id," Welcome to KLUAICTE, \n Feel free to contact \n naresh.vurukonda@kluniversity.in  \n if anything is wrong. \n If you are a student enter your Id to get cohort details. ")
            elif 'aicte' in txt:
                try:
                    send_table(chat_id,txt)
                except Exception as e:
                    tel_send_message(chat_id,"oops you are not registered for cohort-4 AICTE virtual internship! \n If this result is wrong, feel free to contact \n naresh.vurukonda@kluniversity.in ")
                    print(e)
            else:
                try:
                    txt="aicte "+txt
                    my=send_table(chat_id,txt)
                    if not my:
                        tel_send_message(chat_id,"No Schedule Found! \n If this result is wrong, feel free to contact \n rpa.techclub@kluniversity.in ")
                except Exception as e:
                    tel_send_message(chat_id,"oops you are not registered for cohort-4 AICTE virtual internship! \n If this result is wrong, feel free to contact \n naresh.vurukonda@kluniversity.in ")
                    print(e)
            return Response('ok', status=200)
    else:
        return "<h1>Welcome!</h1>"

@app.route('/', methods=['GET', 'POST'])
def index():
    global TOKEN
    TOKEN=""
    if request.method == 'POST':
        msg = request.get_json()
        if 'callback_query' in msg:
            print("Got call back")
            chat_id,txt,query_id=parse_query_message(msg)
        else:
                try:
                    chat_id,txt = parse_message(msg)
                    print(txt)
                except Exception as e:
                    try:
                        chat_id = msg['message']['chat']['id']
                        tel_send_message(chat_id,"Sorry message type not supported! \n If this result is wrong, feel free to contact \n rpa.techclub@kluniversity.in ")
                        return Response('ok', status=200)
                    except Exception as e:
                        return Response('ok', status=200)
        if txt == "/start" or txt== "hi" or txt=="hello":
            tel_send_message(chat_id," Welcome to timetablebot, \n This is our initial implementation of bot.We recommend you to compare bot output with course codes in timetable of ERP. \n Feel free to contact rpa.techclub@kluniversity.in if anything is wrong. \n If you are a student enter your Id to get today 's timetable. \n If your a faculty use emp as prefix followed by faculty id \n Eg: emp 0000")
        elif txt == "/students" or txt=="students" or txt == "/menu" or txt=="menu":
            tel_send_message(chat_id,"Commands for Students.:\n\n1. Just Enter student Id for timetable of present day.\n\nExample: 2000030558\n\n2. Click /exams for exam retaled commands for student.")
        elif txt == "/faculty" or txt == "faculty":
            tel_send_message(chat_id,"Commands for Faculty.:\n\n1. Use emp prefix followed by Employee id for present day timetable.And use next button for tommorrows timetable.\n\nExample: emp 4868\n\n2. Use emp prefix then free followed by day for free faculty on that particularday.\n \t\t[or]\n monday,tuesday,wednesday,thursday,friday,saturday\n\nExample: emp free mon\n\nDays Available shortcuts: mon,tue,wed,thur,fri,sat\n\n3. Click /exams for exam retaled commands for Faculty.")
        elif txt == "/exams" or txt == "exams":
            tel_send_message(chat_id,"Commands for Students.:\n\n1. Use exam prefix followed by student Id for exam timetable of present day(on the day of exam).\n\nExample: exam 2000030558\n\nCommands for Faculty:\n\n1. Use exam prefix with emp followed by your EmployeeId for exam timetable of present day.\n\nExample: exam emp 4868\n\n2. Use exam prefix with emp followed by your EmployeeId then day for particular day timetable.\n\nDays: mon,tue,wed,thur,fri,sat\n \t\t[or]\n monday,tuesday,wednesday,thursday,friday,saturday\n\nExample: exam emp 4868 tue")
        elif 'emp' in txt:
            try:
                if 'exam' in txt:
                    if len(txt.split(" "))==3:
                        command,subcommand,idx=txt.split(" ")
                        dayx=date.now(timezone("Asia/Kolkata"))
                        day=dayx.strftime("%Y-%m-%d")
                    if len(txt.split(" "))==4:
                        command,subcommand,idx,day=txt.split(" ")
                        dayx=date.now(timezone("Asia/Kolkata"))
                        day=day.upper()
                        if day=="MONDAY":
                            day="MON"
                        if day=="TUESDAY":
                            day="TUE"
                        if day=="WEDNESDAY":
                            day="WED"
                        if day=="THURSDAY":
                            day="THUR"
                        if day=="FRIDAY":
                            day="FRI"
                        if day=="SATURDAY":
                            day="SAT"

                        if day=="MON":
                            day="Monday"
                        if day=="TUE":
                            day="Tuesday"
                        if day=="WED":
                            day="Wednesday"
                        if day=="THUR" or day=="THU" or day=="THURS":
                            day="Thursday"
                        if day=="FRI":
                            day="Friday"
                        if day=="SAT":
                            day="Saturday"
                        while dayx.strftime("%A")!=day:
                            dayx=dayx+timedelta(1)
                        day=dayx.strftime("%Y-%m-%d")
                    img,roomseats=examqueries.getempexams(idx,day)
                    if not img:
                        tel_send_message(chat_id,"No Schedule Found! \n If this result is wrong, feel free to contact \n rpa.techclub@kluniversity.in ")
                        print("No schedule")
                        return Response('ok', status=200)
                    url = f'https://api.telegram.org/bot{TOKEN}/sendPhoto?chat_id={chat_id}'
                    files = {"photo": img}
                    requests.post(url, files=files)
                    for images in roomseats:
                        files = {"photo": images}
                        requests.post(url, files=files)
                    return Response('ok', status=200)
                if 'free' in txt:
                    con=sqlite3.connect("/home/nvsai/mysite/kldatabase.db")
                    cur=con.cursor()
                    if len(txt.split(" "))==3:
                        command,subcommand,day=txt.split(" ")
                        day=day.upper()
                        res=cur.execute("select DISTINCT faculty from employeefree where day='"+day+"';")
                    elif len(txt.split(" "))==4:
                        command,subcommand,day,hour=txt.split(" ")
                        day=day.upper()
                        if ',' not in hour:
                            res=cur.execute("select DISTINCT faculty from employeefree where day='"+day+"' AND hour='"+hour+"';")
                        elif ',' in hour:
                            hour=hour.split(",")
                            print(hour)
                            strx="select DISTINCT faculty from employeefree where (hour='"+hour[0]
                            for h in range(1,len(hour)):
                                print(hour[h])
                                strx=strx+"' OR hour='"+hour[h]
                            strx=strx+"') AND day='"+day+"';"
                            res=cur.execute(strx)
                    x=res.fetchall();
                    x=set(x)
                    res2=cur.execute("select DISTINCT faculty from employeefree;")
                    x1=res2.fetchall();
                    x1=set(x1)
                    freeemp=list(x1-x)
                    si = StringIO()
                    cw = csv.writer(si,quoting=csv.QUOTE_ALL)
                    # cw.writerow({'S.No.','Emp ID'})
                    freeemplist=[]
                    freeempserialid=[]
                    for i in range(0,len(freeemp)):
                        if freeemp[i][0]!='nan':
                            freeemplist.append(int(freeemp[i][0]))
                            freeempserialid.append(i)
                    freeemplist.sort()
                    freeemp=dict(zip(freeempserialid,freeemplist))
                    print(freeemplist)
                    for key, value in freeemp.items():
                        cw.writerow([key,value])
                    si.seek(0)
                    buf = BytesIO()
                    buf.write(si.getvalue().encode())
                    buf.seek(0)
                    buf.name = f'free_employees_'+day+'.csv'
                    tel_send_document(chat_id,buf)
                elif 'load' in txt:
                    con=sqlite3.connect("/home/nvsai/mysite/kldatabase.db")
                    cur=con.cursor()
                    if len(txt.split(" "))==3:
                        command,subcommand,faculty=txt.split(" ")
                        res=cur.execute("select faculty from employeefree where faculty='"+faculty+"';")
                    elif len(txt.split(" "))==4:
                        command,subcommand,faculty,day=txt.split(" ")
                        day=day.upper()
                        res=cur.execute("select faculty from employeefree where day='"+day+"' AND faculty='"+faculty+"';")
                    tel_send_message(chat_id,"Total Hours: "+str(len(res.fetchall())))
                else:
                    my=send_table(chat_id,txt)
                    if not my:
                        tel_send_message(chat_id,"No Schedule Found! \n If this result is wrong, feel free to contact \n rpa.techclub@kluniversity.in ")
                    if 'next' not in txt and 'prev' not in txt:
                        btxt="Click on Previous button for Yesterday's  timetable"
                        tel_send_button(chat_id,txt,btxt)
            except Exception as e:
                tel_send_message(chat_id,"No Schedule Found! \n If this result is wrong, feel free to contact \n rpa.techclub@kluniversity.in ")
                print(e)
        elif 'exam' in txt:
            try:
                command,idx=txt.split(" ")
                str1=idx
                img,roomseats=examqueries.getstuexams(str1)
                if not img:
                    tel_send_message(chat_id,"No Schedule Found!\nPlease note that you can only view the exam schedule on the day of exam only. \n If this result is wrong, feel free to contact \n rpa.techclub@kluniversity.in ")
                    print("No schedule")
                    return Response('ok', status=200)
                url = f'https://api.telegram.org/bot{TOKEN}/sendPhoto?chat_id={chat_id}'
                files = {"photo": img}
                requests.post(url, files=files)
                for images in roomseats:
                        files = {"photo": images}
                        requests.post(url, files=files)
                return Response('ok', status=200)
            except Exception as e:
                tel_send_message(chat_id,"No Schedule Found! \n If this result is wrong, feel free to contact \n rpa.techclub@kluniversity.in ")
                print(e)
        elif 'aicte' in txt:
            try:
                send_table(chat_id,txt)
            except Exception as e:
                tel_send_message(chat_id,"No Cohort Found! \n If this result is wrong, feel free to contact \n rpa.techclub@kluniversity.in ")
                print(e)
        elif 'room' in txt:
            try:
                if 'free' in txt:
                    con=sqlite3.connect("/home/nvsai/mysite/kldatabase.db")
                    cur=con.cursor()
                    if len(txt.split(" "))==3:
                        command,subcommand,day=txt.split(" ")
                        day=day.upper()
                        res=cur.execute("select DISTINCT room from roomfree where day='"+day+"';")
                    elif len(txt.split(" "))==4:
                        command,subcommand,day,hour=txt.split(" ")
                        day=day.upper()
                        if ',' not in hour:
                            res=cur.execute("select DISTINCT room from roomfree where day='"+day+"' AND hour='"+hour+"';")
                        elif ',' in hour:
                            hour=hour.split(",")
                            print(hour)
                            strx="select DISTINCT room from roomfree where (hour='"+hour[0]
                            for h in range(1,len(hour)):
                                print(h)
                                strx=strx+"' OR hour='"+hour[h]
                            strx=strx+"') AND day='"+day+"';"
                            res=cur.execute(strx)
                    x=res.fetchall();
                    x=set(x)
                    res2=cur.execute("select DISTINCT room from roomfree;")
                    x1=res2.fetchall();
                    x1=set(x1)
                    freeemp=list(x1-x)
                    si = StringIO()
                    cw = csv.writer(si,quoting=csv.QUOTE_ALL)
                    # cw.writerow({'S.No.','Room No.'})
                    freeemplist=[]
                    freeempserialid=[]
                    for i in range(0,len(freeemp)):
                        freeemplist.append(freeemp[i][0])
                        freeempserialid.append(i)
                    freeemplist.sort()
                    freeemp=dict(zip(freeempserialid,freeemplist))
                    print(freeemplist)
                    for key, value in freeemp.items():
                        cw.writerow([key,value])
                    si.seek(0)
                    buf = BytesIO()
                    buf.write(si.getvalue().encode())
                    buf.seek(0)
                    buf.name = f'free_rooms_'+day+'.csv'
                    tel_send_document(chat_id,buf)
                elif 'load' in txt:
                    con=sqlite3.connect("/home/nvsai/mysite/kldatabase.db")
                    cur=con.cursor()
                    if len(txt.split(" "))==3:
                        command,subcommand,faculty=txt.split(" ")
                        res=cur.execute("select room from roomfree where room='"+faculty+"';")
                    elif len(txt.split(" "))==4:
                        command,subcommand,faculty,day=txt.split(" ")
                        day=day.upper()
                        res=cur.execute("select room from roomfree where day='"+day+"' AND room='"+faculty+"';")
                    tel_send_message(chat_id,"Total Hours: "+str(len(res.fetchall())))
                else:
                    my=send_table(chat_id,txt)
                    if not my:
                        tel_send_message(chat_id,"No Schedule Found! \n If this result is wrong, feel free to contact \n rpa.techclub@kluniversity.in ")
            except Exception as e:
                tel_send_message(chat_id,"No Schedule Found! \n If this result is wrong, feel free to contact \n rpa.techclub@kluniversity.in ")
                print(e)
        else:
            try:
                my=send_table(chat_id,txt)
                if not my:
                        tel_send_message(chat_id,"No Schedule Found! \n If this result is wrong, feel free to contact \n rpa.techclub@kluniversity.in ")
                if 'next' not in txt and 'prev' not in txt:
                    btxt="Click on Previous button for Yesterday's  timetable"
                    tel_send_button(chat_id,txt,btxt)
            except Exception as e:
                tel_send_message(chat_id,"No Classwork Found! \n If this result is wrong, feel free to contact \n rpa.techclub@kluniversity.in \n If your a faculty use emp as prefix followed by faculty id \n Eg: emp 0000")

        return Response('ok', status=200)
    else:
        return "<h1>Welcome!</h1>"

if __name__ == '__main__':
    app.run(threaded=True)

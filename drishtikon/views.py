from django.shortcuts import render,HttpResponse,redirect
from .mails import contact_us_email,otp_email
from django.contrib import messages
from django.contrib import sessions
import math,random
from django.db import connection
from datetime import timedelta, datetime
from deepface import DeepFace
import pandas as pd
import csv
import cv2
import numpy as np
import json
import base64
from django.views.decorators.csrf import csrf_exempt
from coolname import generate_slug
from werkzeug.utils import secure_filename

# OTP Generator
def generateOTP() : 
    digits = "0123456789"
    OTP = "" 
    for i in range(5) : 
        OTP += digits[math.floor(random.random() * 10)] 
    return OTP 

# Landing Page
def home(request):
    return render(request,"index.html")

# Login Page
def login_page(request):
    return render(request,'login.html')


# Login
@csrf_exempt
def login(request):
    email = request.POST.get('email')
    password_candidate = request.POST.get('password')
    user_type = request.POST.get('user_type')
    imgdata1 = request.POST.get('image_hidden')
    with connection.cursor() as cur:
        results1 = cur.execute('SELECT uid, name, email, password, user_type, user_image from drishtikon_users where email = %s and user_type = %s and user_login = 0' , (email,user_type))
        if results1 > 0:
            cresults = cur.fetchone()
            imgdata2 = cresults[5]
            password = cresults[3]
            name = cresults[1]
            uid = cresults[0]
            nparr1 = np.frombuffer(base64.b64decode(imgdata1), np.uint8)
            nparr2 = np.frombuffer(base64.b64decode(imgdata2), np.uint8)
            image1 = cv2.imdecode(nparr1, cv2.COLOR_BGR2GRAY)
            image2 = cv2.imdecode(nparr2, cv2.COLOR_BGR2GRAY)
            img_result  = DeepFace.verify(image1, image2, enforce_detection = False)
            if img_result["verified"] == True and password == password_candidate:
                results2 = cur.execute('UPDATE drishtikon_users set user_login = 1 where email = %s' , [email])
                if results2 > 0:
                    request.session['logged_in'] = True
                    request.session['email'] = email
                    request.session['name'] = name
                    request.session['user_role'] = user_type
                    request.session['uid'] = uid
                    if user_type == "student":
                        return redirect("/studentindex/")
                    else:
                        return redirect("/professorindex/")
                else:
                    messages.error(request,"Error Occured !!!")
                    return redirect("/loginpage/")	
            else:
                messages.error(request,'Either Image not Verified or you have entered Invalid password or Already login')
                return redirect("/loginpage/")
        else:
            messages.error(request,'Already Login or Email was not found!')
            return redirect("/loginpage/")
            
# Logout
def logout(request):
    with connection.cursor() as cur:
        lbr = cur.execute('UPDATE drishtikon_users set user_login = 0 where email = %s and uid = %s',(request.session['email'],request.session['uid']))
        if lbr > 0:
            request.session.clear()
            return redirect("/")
        else:
            return "error"

# Student Index Page
def student_index(request):
    return render(request,"student_index.html")

# Professor Index Page
def professor_index(request):
    return render(request,"professor_index.html")

# Register
@csrf_exempt
def register(request):
    name=request.POST.get("name")
    email=request.POST.get("email")
    password=request.POST.get("password")
    user_type=request.POST.get("user_type")
    imgdata=request.POST.get("image_hidden")
    request.session['tempName'] =name
    request.session['tempEmail'] =email
    request.session['tempPassword'] =password
    request.session['tempUT'] =user_type
    request.session['tempImage'] =imgdata
    sesOTP= generateOTP()
    request.session['tempOTP']= sesOTP
    print("Data before session:- ",request.session['tempName'],request.session['tempOTP'])
    otp_email('MyProctor.ai - OTP Verification',"New Account opening - Your OTP Verfication code is "+sesOTP+".",email)
    return redirect("/verifyemailpage/")

# Verify Email Page
def verify_email_page(request):
     return render(request,'verifyEmail.html')

# Verify Email
@csrf_exempt
def verify_email(request):
    theOTP = request.POST.get('eotp')
    mOTP= request.session["tempOTP"]
    dbName= request.session["tempName"]
    dbEmail= request.session["tempEmail"]
    dbPassword= request.session["tempPassword"]
    dbUser_type= request.session["tempUT"]
    dbImgdata= request.session["tempImage"]
    print("Data after session:- ",request.session['tempName'],request.session['tempOTP'],mOTP)
    with connection.cursor() as cursor:
        if(theOTP == mOTP):
                ar = cursor.execute('INSERT INTO drishtikon_users(name, email, password,register_time, user_type, user_image, user_login,examcredits) values(%s,%s,%s,%s,%s,%s,%s,%s)', (dbName, dbEmail, dbPassword,datetime.now(), dbUser_type, dbImgdata,0,7))
                if ar > 0:
                    messages.success(request,"Thanks for registering! You are sucessfully verified!.")
                    return redirect("/loginpage/")
                else:
                    messages.error(request,"Error Occurred!")
                    return redirect("/loginpage/") 
                request.session.clear()
        else:
            messages.error(request,"OTP is incorrect")
            return redirect("/registerpage/")


def register_page(request): # Register Page
	return render(request,'register.html')

# Contact Us Page
def contact_us_page(request):
	return render(request,'contact.html')
    
# Send Query
@csrf_exempt
def send_query(request):
	cname = request.POST.get("cname")
	cemail = request.POST.get("cemail")
	cquery = request.POST.get("cquery")
	message1= f'Your query will be processed within 24 Hours.'
	message2= f"Name: {cname} Email: {cemail} Query: {cquery}"
	contact_us_email(message1,cemail)
	contact_us_email(message2,"hamzasanwala31@gmail.com")
	messages.success(request,"Your query has been sent successfuly!!!")
	return redirect('/contactpage/')

# Create Test Page
def create_test_page(request):
    return render(request,'create_test.html')

# Create Test
def create_test(request):
    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")
    start_time = request.POST.get("start_time")
    end_time = request.POST.get("end_time")
    start_date_time = str(start_date) + " " + str(start_time)
    end_date_time = str(end_date) + " " + str(end_time)
    duration = int(request.POST.get("duration"))
    password = request.POST.get("password")
    subject = request.POST.get("subject")
    topic = request.POST.get("topic")
    proctor_type = request.POST.get("proctor_type")
    doc = request.FILES["doc"]
    test_id = generate_slug(2)
    # filename = secure_filename(doc)
    # print(filename)
    # filestream = doc
    # print(start_date,end_date,start_time,end_time,start_date_time,end_date_time,duration,password,subject,topic,proctor_type,test_id,doc,filename)
    # filestream.seek(0)
    ef = pd.read_csv(doc)
    fields = ['qid','q','a','b','c','d','ans','marks']
    df = pd.DataFrame(ef, columns = fields)
    print(df)
    # return HttpResponse("Test Created Successfully")
    
    with connection.cursor() as cur:
        for row in df.index:
            cur.execute('INSERT INTO drishtikon_questions(test_id,qid,q,a,b,c,d,ans,marks,uid) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', (test_id, df['qid'][row], df['q'][row], df['a'][row], df['b'][row], df['c'][row], df['d'][row], df['ans'][row], df['marks'][row], request.session['uid']))
        
        cur.execute('INSERT INTO drishtikon_teachers (email, test_id, test_type, start, end, duration, show_ans, password, subject, topic, proctoring_type, uid) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            (request.session['email'], test_id, "objective", start_date_time, end_date_time, duration, 1, password, subject, topic, proctor_type, request.session['uid']))
        cur.execute('UPDATE drishtikon_users SET examcredits = examcredits-1 where email = %s and uid = %s', (request.session['email'],request.session['uid']))
        messages.success(request,f'Exam ID: {test_id}')
        return redirect ('/professorindex/')
    # return HttpResponse("Test Created Successfully")

# Give Test Page
def give_test_page(request):
    return render(request,'give_test.html')

# Give Test
def give_test(request):
    # return HttpResponse("Test started successfully")
    global duration, marked_ans, subject, topic, proctortype
    test_id = request.POST.get('test_id')
    password_candidate = request.POST.get('password')
    imgdata1 = request.POST.get('image_hidden')
    with connection.cursor() as cur:
        results1 = cur.execute('SELECT user_image from drishtikon_users where email = %s and user_type = %s ', (request.session['email'],'student'))
        if results1 > 0:
            cresults = cur.fetchone()
            imgdata2 = cresults[0]
            nparr1 = np.frombuffer(base64.b64decode(imgdata1), np.uint8)
            nparr2 = np.frombuffer(base64.b64decode(imgdata2), np.uint8)
            image1 = cv2.imdecode(nparr1, cv2.COLOR_BGR2GRAY)
            image2 = cv2.imdecode(nparr2, cv2.COLOR_BGR2GRAY)
            img_result  = DeepFace.verify(image1, image2, enforce_detection = False)
            if img_result["verified"] == True:
                results = cur.execute('SELECT * from drishtikon_teachers where test_id = %s', [test_id])
                if results > 0:
                    data = cur.fetchone()
                    password = data[8]
                    duration = data[6]
                    subject = data[9]
                    topic = data[10]
                    start = data[4]
                    start = str(start)
                    end = data[5]
                    end = str(end)
                    proctortype = data[11]
                    if password == password_candidate:
                        now = datetime.now()
                        now = now.strftime("%Y-%m-%d %H:%M:%S")
                        now = datetime.strptime(now,"%Y-%m-%d %H:%M:%S")
                        if datetime.strptime(start,"%Y-%m-%d %H:%M:%S") < now and datetime.strptime(end,"%Y-%m-%d %H:%M:%S") > now:
                            results = cur.execute('SELECT time_left,completed from drishtikon_studenttestinfo where email = %s and test_id = %s', (request.session['email'], test_id))
                            if results > 0:
                                results = cur.fetchone()
                                is_completed = results[1]
                                if is_completed == 0:
                                    time_left = results[0]
                                    if time_left <= duration:
                                        duration = time_left
                                        results = cur.execute('SELECT qid , ans from drishtikon_students where email = %s and test_id = %s and uid = %s', (request.session['email'], test_id, request.session['uid']))
                                        marked_ans = {}
                                        if results > 0:
                                            results = cur.fetchall()
                                            for row in results:
                                                print(row[0])
                                                qiddb = ""+row[0]
                                                print(qiddb)
                                                marked_ans[qiddb] = row[1]
                                                marked_ans = json.dumps(marked_ans)
                                else:
                                    messages.error(request,'Exam already given')
                                    return redirect ('/givetestpage/')
                            else:
                                cur.execute('INSERT into drishtikon_studenttestinfo (email, test_id,time_left,completed,uid) values(%s,%s,SEC_TO_TIME(%s),0,%s)', (request.session['email'], test_id, duration, request.session['uid']))
                                results = cur.execute('SELECT time_left,completed from drishtikon_studenttestinfo where email = %s and test_id = %s and uid = %s', (request.session['email'], test_id, request.session['uid']))
                                if results > 0:
                                    results = cur.fetchone()
                                    is_completed = results[1]
                                    if is_completed == 0:
                                        time_left = results[0]
                                        if time_left <= duration:
                                            duration = time_left
                                            results = cur.execute('SELECT * from drishtikon_students where email = %s and test_id = %s and uid = %s', (request.session['email'], test_id, request.session['uid']))
                                            marked_ans = {}
                                            if results > 0:
                                                results = cur.fetchall()
                                                for row in results:
                                                    marked_ans[row[3]] = row[4]
                                                marked_ans = json.dumps(marked_ans)
                        else:
                            if datetime.strptime(start,"%Y-%m-%d %H:%M:%S") > now:
                                messages.warning(request,f'Exam start time is {start}')
                            else:
                                messages.warning(request,f'Exam has ended')
                            return redirect ('/givetestpage/')
                        return redirect (f'/test/{test_id}/')
                    else:
                        messages.error(request,'Invalid password')
                        return redirect ('/givetestpage/')
                messages.error(request,'Invalid testid')
                return redirect ('/givetestpage/')

            else:
                messages.error(request,'Image not Verified')
                return redirect ('/givetestpage/')

# Test
def test(request,testid):  
    with connection.cursor() as cur:
        cur.execute('SELECT test_type from drishtikon_teachers where test_id = %s ', [testid])
        callresults = cur.fetchone()
        if callresults[0] == "objective":
            global duration, marked_ans, subject, topic, proctortype
            if request.method == 'GET':
                # data = {'duration': duration, 'marks': '', 'q': '', 'a': '', 'b':'','c':'','d':'','answers':marked_ans,'subject':subject,'topic':topic,'tid':testid,'proctortype':proctortype }
                data = { 'marks': '', 'q': '', 'a': '', 'b':'','c':'','d':'','tid':testid }
                return render (request,'testquiz.html' ,data)
                try:
                    data = {'duration': duration, 'marks': '', 'q': '', 'a': '', 'b':'','c':'','d':'','answers':marked_ans,'subject':subject,'topic':topic,'tid':testid,'proctortype':proctortype }
                    return render (request,'testquiz.html' ,data)
                except:
                    # return HttpResponse("Test interrupted Successfully")
                    return redirect ('/givetestpage/')
            else:
                flag = request.form['flag']
                if flag == 'get':
                    num = request.form['no']
                    results = cur.execute('SELECT test_id,qid,q,a,b,c,d,ans,marks from drishtikon_questions where test_id = %s and qid =%s',(testid, num))
                    if results > 0:
                        data = cur.fetchone()
                        del data['ans']
                        return json.dumps(data)
                elif flag=='mark':
                    qid = request.form['qid']
                    ans = request.form['ans']
                    results = cur.execute('SELECT * from drishtikon_students where test_id =%s and qid = %s and email = %s', (testid, qid, request.session['email']))
                    if results > 0:
                        cur.execute('UPDATE drishtikon_students set ans = %s where test_id = %s and qid = %s and email = %s', (testid, qid, request.session['email']))
                    else:
                        cur.execute('INSERT INTO drishtikon_students(email,test_id,qid,ans,uid) values(%s,%s,%s,%s,%s)', (request.session['email'], testid, qid, ans, request.session['uid']))
                elif flag=='time':
                    time_left = request.form['time']
                    try:
                        cur.execute('UPDATE drishtikon_studenttestinfo set time_left=SEC_TO_TIME(%s) where test_id = %s and email = %s and uid = %s and completed=0', (time_left, testid, request.session['email'], request.session['uid']))
                        return json.dumps({'time':'fired'})
                    except:
                        pass
                else:
                    cur.execute('UPDATE drishtikon_studenttestinfo set completed=1,time_left=sec_to_time(0) where test_id = %s and email = %s and uid = %s', (testid, request.session['email'],request.session['uid']))
                    messages.info(request,"Exam submitted successfully")
                    return json.dumps({'sql':'fired'})

        elif callresults['test_type'] == "subjective":
            if request.method == 'GET':
                cur = mysql.connection.cursor()
                cur.execute('SELECT test_id, qid, q, marks from longqa where test_id = %s ORDER BY RAND()',[testid])
                callresults1 = cur.fetchall()
                cur.execute('SELECT time_to_sec(time_left) as duration from studentTestInfo where completed = 0 and test_id = %s and email = %s and uid = %s', (testid, session['email'], session['uid']))
                studentTestInfo = cur.fetchone()
                if studentTestInfo != None:
                    duration = studentTestInfo['duration']
                    cur.execute('SELECT test_id, subject, topic, proctoring_type from teachers where test_id = %s',[testid])
                    testDetails = cur.fetchone()
                    subject = testDetails['subject']
                    test_id = testDetails['test_id']
                    topic = testDetails['topic']
                    proctortypes = testDetails['proctoring_type']
                    cur.close()
                    return render_template("testsubjective.html", callresults = callresults1, subject = subject, duration = duration, test_id = test_id, topic = topic, proctortypes = proctortypes )
                else:
                    cur = mysql.connection.cursor()
                    cur.execute('SELECT test_id, duration, subject, topic from teachers where test_id = %s',[testid])
                    testDetails = cur.fetchone()
                    subject = testDetails['subject']
                    duration = testDetails['duration']
                    test_id = testDetails['test_id']
                    topic = testDetails['topic']
                    cur.close()
                    return render_template("testsubjective.html", callresults = callresults1, subject = subject, duration = duration, test_id = test_id, topic = topic )
            elif request.method == 'POST':
                cur = mysql.connection.cursor()
                test_id = request.form["test_id"]
                cur = mysql.connection.cursor()
                results1 = cur.execute('SELECT COUNT(qid) from longqa where test_id = %s',[testid])
                results1 = cur.fetchone()
                cur.close()
                insertStudentData = None
                for sa in range(1,results1['COUNT(qid)']+1):
                    answerByStudent = request.form[str(sa)]
                    cur = mysql.connection.cursor()
                    insertStudentData = cur.execute('INSERT INTO longtest(email,test_id,qid,ans,uid) values(%s,%s,%s,%s,%s)', (session['email'], testid, sa, answerByStudent, session['uid']))
                    mysql.connection.commit()
                else:
                    if insertStudentData > 0:
                        insertStudentTestInfoData = cur.execute('UPDATE studentTestInfo set completed = 1 where test_id = %s and email = %s and uid = %s', (test_id, session['email'], session['uid']))
                        mysql.connection.commit()
                        cur.close()
                        if insertStudentTestInfoData > 0:
                            flash('Successfully Exam Submitted', 'success')
                            return redirect(url_for('student_index'))
                        else:
                            cur.close()
                            flash('Some Error was occured!', 'error')
                            return redirect(url_for('student_index'))	
                    else:
                        cur.close()
                        flash('Some Error was occured!', 'error')
                        return redirect(url_for('student_index'))

        elif callresults['test_type'] == "practical":
            if request.method == 'GET':
                cur = mysql.connection.cursor()
                cur.execute('SELECT test_id, qid, q, marks, compiler from practicalqa where test_id = %s ORDER BY RAND()',[testid])
                callresults1 = cur.fetchall()
                cur.execute('SELECT time_to_sec(time_left) as duration from studentTestInfo where completed = 0 and test_id = %s and email = %s and uid = %s', (testid, session['email'], session['uid']))
                studentTestInfo = cur.fetchone()
                if studentTestInfo != None:
                    duration = studentTestInfo['duration']
                    cur.execute('SELECT test_id, subject, topic, proctoring_type from teachers where test_id = %s',[testid])
                    testDetails = cur.fetchone()
                    subject = testDetails['subject']
                    test_id = testDetails['test_id']
                    topic = testDetails['topic']
                    proctortypep = testDetails['proctoring_type']
                    cur.close()
                    return render_template("testpractical.html", callresults = callresults1, subject = subject, duration = duration, test_id = test_id, topic = topic, proctortypep = proctortypep )
                else:
                    cur = mysql.connection.cursor()
                    cur.execute('SELECT test_id, duration, subject, topic from teachers where test_id = %s',[testid])
                    testDetails = cur.fetchone()
                    subject = testDetails['subject']
                    duration = testDetails['duration']
                    test_id = testDetails['test_id']
                    topic = testDetails['topic']
                    cur.close()
                    return render_template("testpractical.html", callresults = callresults1, subject = subject, duration = duration, test_id = test_id, topic = topic )
            elif request.method == 'POST':
                test_id = request.form["test_id"]
                codeByStudent = request.form["codeByStudent"]
                inputByStudent = request.form["inputByStudent"]
                executedByStudent = request.form["executedByStudent"]
                cur = mysql.connection.cursor()
                insertStudentData = cur.execute('INSERT INTO practicaltest(email,test_id,qid,code,input,executed,uid) values(%s,%s,%s,%s,%s,%s,%s)', (session['email'], testid, "1", codeByStudent, inputByStudent, executedByStudent, session['uid']))
                mysql.connection.commit()
                if insertStudentData > 0:
                    insertStudentTestInfoData = cur.execute('UPDATE studentTestInfo set completed = 1 where test_id = %s and email = %s and uid = %s', (test_id, session['email'], session['uid']))
                    mysql.connection.commit()
                    cur.close()
                    if insertStudentTestInfoData > 0:
                        flash('Successfully Exam Submitted', 'success')
                        return redirect(url_for('student_index'))
                    else:
                        cur.close()
                        flash('Some Error was occured!', 'error')
                        return redirect(url_for('student_index'))	
            else:
                cur.close()
                flash('Some Error was occured!', 'error')
                return redirect(url_for('student_index'))

# FAQ Page
def faq(request):
    return render(request,"faq.html")
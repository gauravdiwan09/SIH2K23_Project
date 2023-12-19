from django.shortcuts import render,HttpResponse,redirect
from django.http import JsonResponse
from .mails import contact_us_email,otp_email,share_details_email
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
# from .camera import get_frame

# OTP Generator
def generateOTP() : 
    digits = "0123456789"
    OTP = "" 
    for i in range(5) : 
        OTP += digits[math.floor(random.random() * 10)] 
    return OTP 

# Marks Calculate
def marks_calc(email,testid):
    with connection.cursor() as cur:
        results = cur.execute("select marks,q.qid as qid, \
                q.ans as correct, ifnull(s.ans,0) as marked from drishtikon_questions q inner join \
                drishtikon_students s on  s.test_id = q.test_id and s.test_id = %s \
                and s.email = %s and s.qid = q.qid group by q.marks, q.qid, q.ans, s.ans\
                order by q.qid asc", (testid, email))
        data=cur.fetchall()
        sum=0.0
        for i in range(results):
            if(str(data[i][3]).upper() != '0'):
                # if(str(data[i]['marked']).upper() != str(data[i]['correct']).upper()):
                #     sum=sum - (negm/100) * int(data[i]['marks'])
                if(str(data[i][3]).upper() == str(data[i][2]).upper()):
                    sum+=int(data[i][0])
        return sum

# Landing Page
def home(request):
    return render(request,"index.html")

# Login Page
def login_page(request):
    return render(request,'login.html')

# Lost Password Page
def lost_password_page(request):
    return render (request,'lostpassword.html')

# Lost Password
def lost_password(request):
    with connection.cursor() as cur:
        lpemail = request.POST.get('lpemail')
        results = cur.execute('SELECT * from drishtikon_users where email = %s' , [lpemail])
        if results > 0:
            sesOTPfp = generateOTP()
            request.session['tempOTPfp'] = sesOTPfp
            request.session['seslpemail'] = lpemail
            otp_email('MyProctor.ai - OTP Verification for Lost Password',"Your OTP Verfication code for reset password is "+sesOTPfp+".",lpemail)
            # msg1 = Message('MyProctor.ai - OTP Verification for Lost Password', sender = sender, recipients = [lpemail])
            # msg1.body = "Your OTP Verfication code for reset password is "+sesOTPfp+"."
            # mail.send(msg1)
            return redirect ('/verifyOTPpage/') 
        else:
            messages.error(request,"Account not found.")
            return render (request,'lostpassword.html')

# Lp New Pwd
def lp_new_pwd(request):
    with connection.cursor() as cur:
        npwd = request.POST.get('npwd')
        cpwd = request.POST.get('cpwd')
        slpemail = request.session['seslpemail']
        if(npwd == cpwd ):
            cur.execute('UPDATE drishtikon_users set password = %s where email = %s', (npwd, slpemail))
            request.session.clear()
            messages.success(request,"Your password was successfully changed.")
            return render (request,'login.html')
        else:
            messages.error(request,"Password doesn't matched.")
            return render (request,'lpnewpwd.html')

# Verify OTP
def verify_otp(request):
    fpOTP = request.POST.get('fpotp')
    fpsOTP = request.session['tempOTPfp']
    if(fpOTP == fpsOTP):
        return render (request,'lpnewpwd.html')
    messages.error(request,"Incorrect OTP")
    return render (request,'verifyOTPfp.html')

# Verify OTP Page
def verify_otp_page(request):
    return render (request,'verifyOTPfp.html')

# Change Password Professor
def change_password_professor(request):
    return render (request,'changepassword_professor.html')

# Change Password Student
def change_password_student(request):
    return render (request,'changepassword_student.html')

# Change Password
def change_password(request):
    with connection.cursor() as cur:
        oldPassword = request.POST.get('oldpassword')
        newPassword = request.POST.get('newpassword')
        results = cur.execute('SELECT * from drishtikon_users where email = %s and uid = %s', (request.session['email'], request.session['uid']))
        if results > 0:
            data = cur.fetchone()
            password = data[3]
            usertype = data[5]
            if(password == oldPassword):
                cur.execute("UPDATE drishtikon_users SET password = %s WHERE email = %s", (newPassword, request.session['email']))
                messages.success(request,'Changed successfully.')
                if usertype == "student":
                    return render (request,"student_index.html")
                else:
                    return render (request,"professor_index.html")
            else:
                messages.error(request,"Wrong password")
                if usertype == "student":
                    return render (request,"student_index.html")
                else:
                    return render (request,"professor_index.html")
        else:
            return redirect ('/')

# Report Professor
def report_professor(request):
    return render (request,'report_professor.html')

# Report Student
def report_student(request):
    return render (request,'report_student.html')

# Report Professor Email
def report_professor_email(request):
    careEmail = "hamzasanwala31@gmail.com"
    cname = request.session['name']
    cemail = request.session['email']
    ptype = request.POST.get('prob_type')
    cquery = request.POST.get('rquery')
    # msg1 = Message('PROBLEM REPORTED', sender = sender, recipients = [careEmail])
    # msg1.body = " ".join(["NAME:", cname, "PROBLEM TYPE:", ptype ,"EMAIL:", cemail, "", "QUERY:", cquery]) 
    # mail.send(msg1)
    otp_email('PROBLEM REPORTED'," ".join(["NAME:", cname, "PROBLEM TYPE:", ptype ,"EMAIL:", cemail, "", "QUERY:", cquery]),careEmail)
    messages.success(request,'Your Problem has been recorded.')
    return render (request,'report_professor.html')

# Report Student Email
def report_student_email(request):
    careEmail = "hamzasanwala31@gmail.com"
    cname = request.session['name']
    cemail = request.session['email']
    ptype = request.POST.get('prob_type')
    cquery = request.POST.get('rquery')
    # msg1 = Message('PROBLEM REPORTED', sender = sender, recipients = [careEmail])
    # msg1.body = " ".join(["NAME:", cname, "PROBLEM TYPE:", ptype ,"EMAIL:", cemail, "", "QUERY:", cquery]) 
    # mail.send(msg1)
    otp_email('PROBLEM REPORTED'," ".join(["NAME:", cname, "PROBLEM TYPE:", ptype ,"EMAIL:", cemail, "", "QUERY:", cquery]),careEmail)
    messages.success(request,'Your Problem has been recorded.')
    return render (request,'report_student.html')

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

# Student Test History
def student_test_history(request,email):
    with connection.cursor() as cur:
        if email == request.session['email']:
            results = cur.execute('SELECT a.test_id, b.subject, b.topic \
                from drishtikon_studenttestinfo a, drishtikon_teachers b where a.test_id = b.test_id and a.email=%s  \
                and a.completed=1', [email])
            results = cur.fetchall()
            data={'tests':results}
            return render (request,'student_test_history.html', data)
        else:
            messages.warning(request,'You are not authorized')
            return redirect ('/studentindex/')

# Tests Given Page
def tests_given_page(request,email):
    with connection.cursor() as cur:
        if email == request.session['email']:
            resultsTestids = cur.execute('select drishtikon_studenttestinfo.test_id as test_id from drishtikon_studenttestinfo, drishtikon_teachers where drishtikon_studenttestinfo.email = %s and drishtikon_studenttestinfo.uid = %s and drishtikon_studenttestinfo.completed=1 and drishtikon_teachers.test_id = drishtikon_studenttestinfo.test_id and drishtikon_teachers.show_ans = 1 ', (request.session['email'], request.session['uid']))
            resultsTestids = cur.fetchall()
            data={'cresults':resultsTestids}
            return render (request,'tests_given.html', data)
        else:
            messages.warning(request,'You are not authorized')
            return redirect ('/studentindex/')

# Tests Given
def tests_given(request,email):
    with connection.cursor() as cur:
        tidoption = request.POST.get('choosetid')
        cur.execute('SELECT test_type from drishtikon_teachers where test_id = %s',[tidoption])
        callresults = cur.fetchone()
        if callresults[0] == "objective":
            results = cur.execute('select distinct(drishtikon_students.test_id) as test_id, drishtikon_students.email as email, subject,topic from drishtikon_students, drishtikon_studenttestinfo, drishtikon_teachers where drishtikon_students.email = %s and drishtikon_teachers.test_type = %s and drishtikon_students.test_id = %s and drishtikon_students.test_id=drishtikon_teachers.test_id and drishtikon_students.test_id=drishtikon_studenttestinfo.test_id and drishtikon_studenttestinfo.completed=1', (email, "objective", tidoption))
            results = cur.fetchall()
            results1 = []
            studentResults = None
            for a in results:
                results1.append(marks_calc(a[1],a[0]))
                studentResults = zip(results,results1)
            data={'tests':studentResults}
            return render (request,'obj_result_student.html', data)
        elif callresults['test_type'] == "subjective":
            cur = mysql.connection.cursor()
            studentResults = cur.execute('select SUM(longtest.marks) as marks, longtest.test_id as test_id, teachers.subject as subject, teachers.topic as topic from longtest,teachers,studenttestinfo where longtest.email = %s and longtest.test_id = %s and longtest.test_id=teachers.test_id and studenttestinfo.test_id=teachers.test_id and longtest.email = studenttestinfo.email and studenttestinfo.completed = 1 and teachers.show_ans=1 group by longtest.test_id', (email, tidoption))
            studentResults = cur.fetchall()
            cur.close()
            return render_template('sub_result_student.html', tests=studentResults)
        elif callresults['test_type'] == "practical":
            cur = mysql.connection.cursor()
            studentResults = cur.execute('select SUM(practicaltest.marks) as marks, practicaltest.test_id as test_id, teachers.subject as subject, teachers.topic as topic from practicaltest,teachers,studenttestinfo where practicaltest.email = %s and practicaltest.test_id = %s and practicaltest.test_id=teachers.test_id and studenttestinfo.test_id=teachers.test_id and practicaltest.email = studenttestinfo.email and studenttestinfo.completed = 1 and teachers.show_ans=1 group by practicaltest.test_id', (email, tidoption))
            studentResults = cur.fetchall()
            cur.close()
            return render_template('prac_result_student.html', tests=studentResults)

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
    # print(df)
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
@csrf_exempt
def test(request,testid):  
    with connection.cursor() as cur:
        cur.execute('SELECT test_type from drishtikon_teachers where test_id = %s ', [testid])
        callresults = cur.fetchone()
        if callresults[0] == "objective":
            global duration, marked_ans, subject, topic, proctortype
            if request.method == 'GET':
                cur.execute("select * from drishtikon_questions where test_id='{}'".format(testid,))
                questions=cur.fetchall()
                cur.execute("select duration,subject,topic,proctoring_type from drishtikon_teachers where test_id='{}'".format(testid,))
                d=cur.fetchall()
                duration=d[0][0]
                subject=d[0][1]
                topic=d[0][2]
                proctortype=d[0][3]
                # data = {'duration': duration, 'marks': '', 'q': '', 'a': '', 'b':'','c':'','d':'','answers':marked_ans,'subject':subject,'topic':topic,'tid':testid,'proctortype':proctortype }
                data = {'questions':questions,'tid':testid,'duration':duration,'subject':subject,'topic':topic,'proctortype':proctortype}
                return render (request,'testquiz.html' ,data)
                return render (request,'capture.html' ,data)
                try:
                    data = {'duration': duration, 'marks': '', 'q': '', 'a': '', 'b':'','c':'','d':'','answers':marked_ans,'subject':subject,'topic':topic,'tid':testid,'proctortype':proctortype }
                    return render (request,'testquiz.html' ,data)
                except:
                    # return HttpResponse("Test interrupted Successfully")
                    return redirect ('/givetestpage/')
            else:
                # flag = request.form['flag']
                # if flag == 'get':
                #     num = request.form['no']
                #     results = cur.execute('SELECT test_id,qid,q,a,b,c,d,ans,marks from drishtikon_questions where test_id = %s and qid =%s',(testid, num))
                #     if results > 0:
                #         data = cur.fetchone()
                #         del data['ans']
                #         return json.dumps(data)
                # elif flag=='mark':
                #     qid = request.form['qid']
                #     ans = request.form['ans']
                #     results = cur.execute('SELECT * from drishtikon_students where test_id =%s and qid = %s and email = %s', (testid, qid, request.session['email']))
                #     if results > 0:
                #         cur.execute('UPDATE drishtikon_students set ans = %s where test_id = %s and qid = %s and email = %s', (testid, qid, request.session['email']))
                #     else:
                #         cur.execute('INSERT INTO drishtikon_students(email,test_id,qid,ans,uid) values(%s,%s,%s,%s,%s)', (request.session['email'], testid, qid, ans, request.session['uid']))
                # elif flag=='time':
                #     time_left = request.form['time']
                #     try:
                #         cur.execute('UPDATE drishtikon_studenttestinfo set time_left=SEC_TO_TIME(%s) where test_id = %s and email = %s and uid = %s and completed=0', (time_left, testid, request.session['email'], request.session['uid']))
                #         return json.dumps({'time':'fired'})
                #     except:
                #         pass
                # else:
                # cur.execute("select qid from drishtikon_questions where test_id='{}'".format(testid,))
                # d=cur.fetchall()
                # for i in d:
                #     ans=request.POST.get(i[0])
                #     cur.execute("insert into drishtikon_students(email,test_id,qid,ans,uid) values('{}','{}','{}','{}',{})".format(request.session['email'],testid,i[0],ans,request.session['uid']))
                # # return HttpResponse("Form submitted successfully")
                # cur.execute('UPDATE drishtikon_studenttestinfo set completed=1,time_left=sec_to_time(0) where test_id = %s and email = %s and uid = %s', (testid, request.session['email'],request.session['uid']))
                # messages.info(request,"Exam submitted successfully")
                return json.dumps({'sql':'fired'})
                # return redirect('/studentindex/')

        elif callresults[0] == "subjective":
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

        elif callresults[0] == "practical":
            if request.method == 'GET':
                cur.execute('SELECT test_id, qid, q, marks, compiler from drishtikon_practicalqa where test_id = %s ORDER BY RAND()',[testid])
                callresults1 = cur.fetchall()
                cur.execute('SELECT time_to_sec(time_left) as duration from drishtikon_studenttestinfo where completed = 0 and test_id = %s and email = %s and uid = %s', (testid, request.session['email'], request.session['uid']))
                studentTestInfo = cur.fetchone()
                if studentTestInfo != None:
                    duration = studentTestInfo[0]
                    cur.execute('SELECT test_id, subject, topic, proctoring_type from drishtikon_teachers where test_id = %s',[testid])
                    testDetails = cur.fetchone()
                    subject = testDetails[1]
                    test_id = testDetails[0]
                    topic = testDetails[2]
                    proctortypep = testDetails[3]
                    data={'callresults':callresults1,'subject':subject,'duration':duration,'test_id':test_id,'topic':topic,'proctortypep':proctortypep}
                    return render (request,"testpractical.html")
                else:
                    cur.execute('SELECT test_id, duration, subject, topic from drishtikon_teachers where test_id = %s',[testid])
                    testDetails = cur.fetchone()
                    subject = testDetails[2]
                    duration = testDetails[1]
                    test_id = testDetails[0]
                    topic = testDetails[3]
                    data={'callresults':callresults1,'subject':subject,'duration':duration,'test_id':test_id,'topic':topic}
                    return render (request,"testpractical.html")
            elif request.method == 'POST':
                test_id = request.POST.get("test_id")
                codeByStudent = request.POST.get("codeByStudent")
                inputByStudent = request.POST.get("inputByStudent")
                executedByStudent = request.POST.get("executedByStudent")
                insertStudentData = cur.execute('INSERT INTO drishtikon_practicaltest(email,test_id,qid,code,input,executed,uid) values(%s,%s,%s,%s,%s,%s,%s)', (request.session['email'], testid, "1", codeByStudent, inputByStudent, executedByStudent, request.session['uid']))
                if insertStudentData > 0:
                    insertStudentTestInfoData = cur.execute('UPDATE drishtikon_studenttestinfo set completed = 1 where test_id = %s and email = %s and uid = %s', (test_id, request.session['email'], request.session['uid']))
                    if insertStudentTestInfoData > 0:
                        messages.success(request,'Successfully Exam Submitted')
                        return redirect ('/studentindex/')
                    else:
                        messages.error(request,'Some Error was occured!')
                        return redirect ('/studentindex/')	
            else:
                messages.error(request,'Some Error was occured!')
                return redirect ('/studentindex/')

# Submit Test
def submit_test(request,testid):
    with connection.cursor() as cur:
        cur.execute("select qid from drishtikon_questions where test_id='{}'".format(testid,))
        d=cur.fetchall()
        for i in d:
            ans=request.POST.get(i[0])
            cur.execute("insert into drishtikon_students(email,test_id,qid,ans,uid) values('{}','{}','{}','{}',{})".format(request.session['email'],testid,i[0],ans,request.session['uid']))
        # return HttpResponse("Form submitted successfully")
        cur.execute('UPDATE drishtikon_studenttestinfo set completed=1,time_left=sec_to_time(0) where test_id = %s and email = %s and uid = %s', (testid, request.session['email'],request.session['uid']))
        messages.info(request,"Exam submitted successfully")
        # return json.dumps({'sql':'fired'})
        return redirect('/studentindex/')

# Backened Image
@csrf_exempt
def backened_image(request):
    # img=request.POST.get('image')
    img=json.loads(request.body)['image']
    # img= base64.b64encode(img)
    if img:
        # testid = request.form['data[testid]']
        # voice_db = request.form['data[voice_db]']
        # proctorData = get_frame(img)
        # jpg_as_text = proctorData['jpg_as_text']
        # mob_status =proctorData['mob_status']
        # print(mob_status)
        # person_status = proctorData['person_status']
        # print(person_status)
        # user_move1 = proctorData['user_move1']
        # print(user_move1)
        # user_move2 = proctorData['user_move2']
        # print(user_move2)
        # eye_movements = proctorData['eye_movements']
        # print(eye_movements)
        # cur = mysql.connection.cursor()
        # results = cur.execute('INSERT INTO proctoring_log (email, name, test_id, voice_db, img_log, user_movements_updown, user_movements_lr, user_movements_eyes, phone_detection, person_status, uid) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
        #     (Email_login, Name_login, testid, voice_db, jpg_as_text, user_move1, user_move2, eye_movements, mob_status, person_status,UID_login))
        # mysql.connection.commit()
        # cur.close()
        # if(results > 0):
        #     return "recorded image of video"
        # else:
        #     return "error in video"
        print("Hey")
        return JsonResponse({'status':'success'})
    else:
        print("Not found")
        return JsonResponse({'status':'error'})
# Generate Test Page
def generate_test_page(request):
    return render(request,'generatetest.html')

# View Questions Page
def view_questions_page(request):
        with connection.cursor() as cur:
            results = cur.execute('SELECT test_id from drishtikon_teachers where email = %s and uid = %s', (request.session['email'],request.session['uid']))
            if results > 0:
                cresults = cur.fetchall()
                data={'cresults':cresults}
                return render (request,"viewquestions.html", data)
            else:
                data={'cresults':None}
                return render (request,"viewquestions.html",data)

    # Exam Type Check
    # def examtypecheck(tidoption):
    #     with connection.cursor() as cur:
    #         print(callresults)
    #         return callresults

# Display Questions Page
def display_questions_page(request):
    with connection.cursor() as cur:
        tidoption = request.POST.get('choosetid')
        cur.execute('SELECT test_type from drishtikon_teachers where test_id = %s and email = %s and uid = %s', (tidoption, request.session['email'], request.session['uid']))
        et = cur.fetchone()
        if et[0] == "objective":
            cur.execute('SELECT * from drishtikon_questions where test_id = %s and uid = %s', (tidoption, request.session['uid']))
            callresults = cur.fetchall()
            data={'callresults':callresults}
            return render (request,"displayquestions.html", data)
        elif et[0] == "subjective":
            cur.execute('SELECT * from drishtikon_longqa where test_id = %s and uid = %s', (tidoption,request.session['uid']))
            callresults = cur.fetchall()
            data={'callresults':callresults}
            return render (request,"displayquestions.html", data)
        elif et[0] == "practical":
            cur.execute('SELECT * from drishtikon_practicalqa where test_id = %s and uid = %s', (tidoption,request.session['uid']))
            callresults = cur.fetchall()
            data={'callresults':callresults}
            return render (request,"displayquestions.html", data)

# Update TID List
def update_tid_list(request):
    with connection.cursor() as cur:
        results = cur.execute('SELECT * from drishtikon_teachers where email = %s and uid = %s', (request.session['email'],request.session['uid']))
        if results > 0:
            cresults = cur.fetchall()
            now = datetime.now()
            now = now.strftime("%Y-%m-%d %H:%M:%S")
            now = datetime.strptime(now,"%Y-%m-%d %H:%M:%S")
            testids = []
            for a in cresults:
                if datetime.strptime(str(a[4]),"%Y-%m-%d %H:%M:%S") > now:
                    testids.append(a[2])
            data={'cresults':testids}
            return render (request,"updatetidlist.html", data)
        else:
            data={'cresults':None}
            return render (request,"updatetidlist.html", data)
    
# Update Disp Ques
def update_disp_ques(request):
    with connection.cursor() as cur:
        tidoption = request.POST.get('choosetid')
        cur.execute('SELECT test_type from drishtikon_teachers where test_id = %s and email = %s and uid = %s', (tidoption, request.session['email'], request.session['uid']))
        et = cur.fetchone()
        if et[0] == "objective":
            cur.execute('SELECT * from drishtikon_questions where test_id = %s and uid = %s', (tidoption,request.session['uid']))
            callresults = cur.fetchall()
            data={'callresults':callresults}
            return render (request,"updatedispques.html", data)
        elif et[0] == "subjective":
            cur.execute('SELECT * from drishtikon_longqa where test_id = %s and uid = %s', (tidoption,request.session['uid']))
            callresults = cur.fetchall()
            data={'callresults':callresults}
            return render (request,"updatedispquesLQA.html", data)
        elif et[0] == "practical":
            cur.execute('SELECT * from drishtikon_practicalqa where test_id = %s and uid = %s', (tidoption,request.session['uid']))
            callresults = cur.fetchall()
            data={'callresults':callresults}
            return render (request,"updatedispquesPQA.html", data)
        else:
            messages.error(request,'Error Occured!')
            return redirect ('/updatetidlist/')

# Update Test Page
def update_test_page(request,testid,qid):
    with connection.cursor() as cur:
        cur.execute('SELECT * FROM drishtikon_questions where test_id = %s and qid =%s and uid = %s', (testid,qid,request.session['uid']))
        uresults = cur.fetchall()
        data={'uresults':uresults}
        return render (request,"updateQuestions.html", data)

# Update Test 
def update_test(request,testid,qid):
    with connection.cursor() as cur:
        ques = request.POST.get('ques')
        ao = request.POST.get('ao')
        bo = request.POST.get('bo')
        co = request.POST.get('co')
        do = request.POST.get('do')
        anso = request.POST.get('anso')
        markso = request.POST.get('mko')
        cur.execute('UPDATE drishtikon_questions SET q = %s, a = %s, b = %s, c = %s, d = %s, ans = %s, marks = %s where test_id = %s and qid = %s and uid = %s', (ques,ao,bo,co,do,anso,markso,testid,qid,request.session['uid']))
        messages.success(request,'Updated successfully.')
        return redirect ('/updatetidlist/')

# Del TID List
def del_tid_list(request):
    with connection.cursor() as cur:
        results = cur.execute('SELECT * from drishtikon_teachers where email = %s and uid = %s', (request.session['email'], request.session['uid']))
        if results > 0:
            cresults = cur.fetchall()
            now = datetime.now()
            now = now.strftime("%Y-%m-%d %H:%M:%S")
            now = datetime.strptime(now,"%Y-%m-%d %H:%M:%S")
            testids = []
            for a in cresults:
                if datetime.strptime(str(a[4]),"%Y-%m-%d %H:%M:%S") > now:
                    testids.append(a[2])
            data={'cresults':testids}
            return render (request,"deltidlist.html", data)
        else:
            return render (request,"deltidlist.html")

# Del Disp Ques
def del_disp_ques(request):
    with connection.cursor() as cur:
        tidoption = request.POST.get('choosetid')
        cur.execute('SELECT test_type from drishtikon_teachers where test_id = %s and email = %s and uid = %s', (tidoption, request.session['email'], request.session['uid']))
        et = cur.fetchone()
        if et[0] == "objective":
            cur.execute('SELECT * from drishtikon_questions where test_id = %s and uid = %s', (tidoption,request.session['uid']))
            callresults = cur.fetchall()
            data={"callresults":callresults,'tid':tidoption}
            return render (request,"deldispques.html", data)
        elif et[0] == "subjective":
            cur.execute('SELECT * from drishtikon_longqa where test_id = %s and uid = %s', (tidoption,request.session['uid']))
            callresults = cur.fetchall()
            data={"callresults":callresults,'tid':tidoption}
            return render (request,"deldispquesLQA.html", data)
        elif et[0] == "practical":
            cur.execute('SELECT * from drishtikon_practicalqa where test_id = %s and uid = %s', (tidoption,request.session['uid']))
            callresults = cur.fetchall()
            data={"callresults":callresults,'tid':tidoption}
            return render (request,"deldispquesPQA.html", data)
        else:
            messages.error(request,"Some Error Occured!")
            return redirect ('/deltidlist/')

# Delete Questions
@csrf_exempt
def delete_questions(request,testid):
    with connection.cursor() as cur:
        cur.execute('SELECT test_type from drishtikon_teachers where test_id = %s and email = %s and uid = %s', (testid, request.session['email'], request.session['uid']))
        et = cur.fetchone()
        if et[0] == "objective":
            msg = '' 
            # testqdel = request.json['qids']
            testqdel = json.loads(request.body)['qids']
            # print(testqdel)
            if testqdel:
                if ',' in testqdel:
                    testqdel = testqdel.split(',')
                    for getid in testqdel:
                        cur.execute('DELETE FROM drishtikon_questions WHERE test_id = %s and qid =%s and uid = %s', (testid,getid,request.session['uid']))
                    resp = JsonResponse('<span style=\'color:green;\'>Questions deleted successfully</span>',safe=False)
                    resp.status_code = 200
                    return resp
                else:
                    cur.execute('DELETE FROM drishtikon_questions WHERE test_id = %s and qid =%s and uid = %s', (testid,testqdel,request.session['uid']))
                    resp = JsonResponse('<span style=\'color:green;\'>Questions deleted successfully</span>',safe=False)
                    resp.status_code = 200
                    return resp
        elif et[0] == "subjective":
            msg = '' 
            testqdel = request.json['qids']
            if testqdel:
                if ',' in testqdel:
                    testqdel = testqdel.split(',')
                    for getid in testqdel:
                        cur.execute('DELETE FROM drishtikon_longqa WHERE test_id = %s and qid =%s and uid = %s', (testid,getid,request.session['uid']))
                    resp = JsonResponse('<span style=\'color:green;\'>Questions deleted successfully</span>')
                    resp.status_code = 200
                    return resp
                else:
                    cur.execute('DELETE FROM drishtikon_longqa WHERE test_id = %s and qid =%s and uid = %s', (testid,testqdel,request.session['uid']))
                    resp = JsonResponse('<span style=\'color:green;\'>Questions deleted successfully</span>')
                    resp.status_code = 200
                    return resp
        elif et[0] == "practical":
            msg = '' 
            testqdel = request.json['qids']
            if testqdel:
                if ',' in testqdel:
                    testqdel = testqdel.split(',')
                    for getid in testqdel:
                        cur.execute('DELETE FROM drishtikon_practicalqa WHERE test_id = %s and qid =%s and uid = %s', (testid,getid,request.session['uid']))
                    resp = JsonResponse('<span style=\'color:green;\'>Questions deleted successfully</span>')
                    resp.status_code = 200
                    return resp
            else:
                cur.execute('DELETE FROM drishtikon_questions WHERE test_id = %s and qid =%s and uid = %s', (testid,testqdel,request.session['uid']))
                resp = JsonResponse('<span style=\'color:green;\'>Questions deleted successfully</span>')
                resp.status_code = 200
                return resp
        else:
            messages.error(request,"Some Error Occured!")
            return redirect ('/deltidlist/')

# Disp Tests
def disp_tests(request,email):
    with connection.cursor() as cur:
        if email == request.session['email']:
            results = cur.execute('select * from drishtikon_teachers where email = %s and uid = %s', (email,request.session['uid']))
            results = cur.fetchall()
            data={'tests':results}
            return render (request,'disptests.html', data)
        else:
            messages.warning(request,'You are not authorized',)
            return redirect ('/professorindex/')

# Share Details
def share_details(request,email,testid):
    with connection.cursor() as cur:
        cur.execute('SELECT * from drishtikon_teachers where test_id = %s and email = %s', (testid, email))
        callresults = cur.fetchall()
        data={'callresults':callresults}   
        return render (request,"share_details.html", data)

# Share Details Emails
def share_details_emails(request):
    tid = request.POST.get('tid')
    subject = request.POST.get('subject')
    topic = request.POST.get('topic')
    duration = request.POST.get('duration')
    start = request.POST.get('start')
    end = request.POST.get('end')
    password = request.POST.get('password')
    emailssharelist = request.POST.get('emailssharelist')
    emaillist=emailssharelist.split(',')
    # msg1 = Message('EXAM DETAILS - MyProctor.ai', sender = sender, recipients = [emailssharelist])
    # msg1.body = " ".join(["EXAM-ID:", tid, "SUBJECT:", subject, "TOPIC:", topic, "DURATION:", duration, "START", start, "END", end, "PASSWORD", password, "NEGATIVE MARKS in %:","CALCULATOR ALLOWED:" ]) 
    # mail.send(msg1)
    share_details_email('EXAM DETAILS - MyProctor.ai'," ".join(["EXAM-ID:", tid, "SUBJECT:", subject, "TOPIC:", topic, "DURATION:", duration, "START", start, "END", end, "PASSWORD", password ]),emaillist)
    messages.success(request,'Emails sended sucessfully!')
    return redirect ("/professorindex/")

# Live Monitoring TID
def live_monitoring_tid(request):
    with connection.cursor() as cur:
        results = cur.execute('SELECT * from drishtikon_teachers where email = %s and uid = %s and proctoring_type = 1', (request.session['email'], request.session['uid']))
        if results > 0:
            cresults = cur.fetchall()
            now = datetime.now()
            now = now.strftime("%Y-%m-%d %H:%M:%S")
            now = datetime.strptime(now,"%Y-%m-%d %H:%M:%S")
            testids = []
            for a in cresults:
                if datetime.strptime(str(a[4]),"%Y-%m-%d %H:%M:%S") <= now and datetime.strptime(str(a[5]),"%Y-%m-%d %H:%M:%S") >= now:
                    testids.append(a[2])
            data={'cresults':testids}
            return render (request,"livemonitoringtid.html", data)
        else:
            return render (request,"livemonitoringtid.html")

# Live Monitoring
def live_monitoring(request):
    testid = request.POST.get('choosetid')
    data={'testid':testid}
    return render (request,'live_monitoring.html',data)

# View Students Logs
def view_students_logs(request):
    with connection.cursor() as cur:
        results = cur.execute('SELECT test_id from drishtikon_teachers where email = %s and uid = %s and proctoring_type = 0', (request.session['email'], request.session['uid']))
        if results > 0:
            cresults = cur.fetchall()
            data={'cresults':cresults}
            return render (request,"viewstudentslogs.html", data)
        else:
            return render (request,"viewstudentslogs.html")

# Display Students Details
def display_students_details(request):
    with connection.cursor() as cur:
        tidoption = request.POST.get('choosetid')
        cur.execute('SELECT DISTINCT email,test_id from drishtikon_proctoring_log where test_id = %s', [tidoption])
        callresults = cur.fetchall()
        data={'callresults':callresults}
        return render (request,"displaystudentsdetails.html", data)

# Insert Marks TID
def insert_marks_tid(request):
    with connection.cursor() as cur:
        results = cur.execute('SELECT * from drishtikon_teachers where show_ans = 0 and email = %s and uid = %s and (test_type = %s or test_type = %s)', (request.session['email'], request.session['uid'],"subjective","practical"))
        if results > 0:
            cresults = cur.fetchall()
            now = datetime.now()
            now = now.strftime("%Y-%m-%d %H:%M:%S")
            now = datetime.strptime(now,"%Y-%m-%d %H:%M:%S")
            testids = []
            for a in cresults:
                if datetime.strptime(str(a[5]),"%Y-%m-%d %H:%M:%S") < now:
                    testids.append(a[2])
            data={'cresults':testids}
            return render (request,"insertmarkstid.html", data)
        else:
            return render (request,"insertmarkstid.html")

# Publish Results Testid
def publish_results_testid(request):
    with connection.cursor() as cur:
        results = cur.execute('SELECT * from drishtikon_teachers where test_type != %s AND show_ans = 0 AND email = %s AND uid = %s', ("objectve", request.session['email'], request.session['uid']))
        if results > 0:
            cresults = cur.fetchall()
            now = datetime.now()
            now = now.strftime("%Y-%m-%d %H:%M:%S")
            now = datetime.strptime(now,"%Y-%m-%d %H:%M:%S")
            testids = []
            for a in cresults:
                if datetime.strptime(str(a[5]),"%Y-%m-%d %H:%M:%S") < now:
                    testids.append(a[2])
            data={'cresults':testids}
            return render (request,"publish_results_testid.html", data)
        else:
            return render (request,"publish_results_testid.html")

# Tests Created
def tests_created(request,email):
    with connection.cursor() as cur:
        if email == request.session['email']:
            results = cur.execute('select * from drishtikon_teachers where email = %s and uid = %s and show_ans = 1', (email,request.session['uid']))
            results = cur.fetchall()
            data={'tests':results}
            return render (request,'tests_created.html', data)
        else:
            messages.warning(request,'You are not authorized')
            return redirect ('/professorindex/')

# Student Results
def student_results(request,email,testid):
    with connection.cursor() as cur:
        if email == request.session['email']:
            cur.execute('SELECT test_type from drishtikon_teachers where test_id = %s and email = %s and uid = %s', (testid, request.session['email'], request.session['uid']))
            et = cur.fetchone()
            if et[0] == "objective":
                results = cur.execute('select drishtikon_users.name as name,drishtikon_users.email as email, drishtikon_studenttestinfo.test_id as test_id from drishtikon_studenttestinfo, drishtikon_users where test_id = %s and completed = 1 and  drishtikon_users.user_type = %s and drishtikon_studenttestinfo.email=drishtikon_users.email ', (testid,'student'))
                results = cur.fetchall()
                final = []
                names = []
                scores = []
                count = 1
                for user in results:
                    score = marks_calc(user[1], user[2])
                    # user['srno'] = count
                    # user['marks'] = score
                    final.append([count, user[0], score])
                    names.append(user[0])
                    scores.append(score)
                    count+=1
                dic={'data':final,'labels':names,'values':scores}
                return render (request,'student_results.html', dic)
            elif et['test_type'] == "subjective":
                cur = mysql.connection.cursor()
                results = cur.execute('select users.name as name,users.email as email, longtest.test_id as test_id, SUM(longtest.marks) AS marks from longtest, users where longtest.test_id = %s  and  users.user_type = %s and longtest.email=users.email', (testid,'student'))
                results = cur.fetchall()
                cur.close()
                names = []
                scores = []
                for user in results:
                    names.append(user['name'])
                    scores.append(user['marks'])
                return render_template('student_results_lqa.html', data=results, labels=names, values=scores)
            elif et['test_type'] == "practical":
                cur = mysql.connection.cursor()
                results = cur.execute('select users.name as name,users.email as email, practicaltest.test_id as test_id, SUM(practicaltest.marks) AS marks from practicaltest, users where practicaltest.test_id = %s  and  users.user_type = %s and practicaltest.email=users.email', (testid,'student'))
                results = cur.fetchall()
                cur.close()
                names = []
                scores = []
                for user in results:
                    names.append(user['name'])
                    scores.append(user['marks'])
                return render_template('student_results_pqa.html', data=results, labels=names, values=scores)

# Create Test Pqa Page
def create_test_pqa_page(request):
    return render (request,'create_prac_qa.html')

# Create Test Pqa
def create_test_pqa(request):
    with connection.cursor() as cur:
        test_id = generate_slug(2)
        compiler = request.POST.get("compiler")
        questionprac = request.POST.get("questionprac")
        marksprac = int(request.POST.get("marksprac"))
        cur.execute('INSERT INTO drishtikon_practicalqa(test_id,qid,q,compiler,marks,uid) values(%s,%s,%s,%s,%s,%s)', (test_id, 1, questionprac, compiler, marksprac, request.session['uid']))
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
        cur.execute('INSERT INTO drishtikon_teachers (email, test_id, test_type, start, end, duration, show_ans, password, subject, topic, proctoring_type, uid) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            (request.session['email'], test_id, "practical", start_date_time, end_date_time, duration, 0, password, subject, topic, proctor_type, request.session['uid']))
        messages.success(request,f'Exam ID: {test_id}')
        return redirect ('/professorindex/')

# FAQ Page
def faq(request):
    return render(request,"faq.html")
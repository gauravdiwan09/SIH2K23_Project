from django.shortcuts import render,HttpResponse,redirect
from .mails import contact_us_email,otp_email
from django.contrib import messages
from django.contrib import sessions
import math,random
from django.db import connection
import datetime
from deepface import DeepFace
import pandas as pd
import csv
import cv2
import numpy as np
import json
import base64
from django.views.decorators.csrf import csrf_exempt

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
                ar = cursor.execute('INSERT INTO drishtikon_users(name, email, password,register_time, user_type, user_image, user_login,examcredits) values(%s,%s,%s,%s,%s,%s,%s,%s)', (dbName, dbEmail, dbPassword,datetime.datetime.now(), dbUser_type, dbImgdata,0,7))
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

# FAQ Page
def faq(request):
    return render(request,"faq.html")
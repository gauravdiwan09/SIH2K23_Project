from django.shortcuts import render,HttpResponse,redirect
from .mails import contact_us_email,otp_email
from django.contrib import messages
from django.contrib import sessions
import math,random
from django.db import connection
import datetime

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
def login(request):
    return HttpResponse("Succesflly logged in")

# Register
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
    otp_email('MyProctor.ai - OTP Verification',"New Account opening - Your OTP Verfication code is "+sesOTP+".",email)
    return redirect("/verifyemailpage/")

# Verify Email Page
def verify_email_page(request):
     return render(request,'verifyEmail.html')

# Verify Email
def verify_email(request):
    theOTP = request.POST.get('eotp')
    mOTP= request.session["tempOTP"]
    dbName= request.session["tempName"]
    dbEmail= request.session["tempEmail"]
    dbPassword= request.session["tempPassword"]
    dbUser_type= request.session["tempUT"]
    dbImgdata= request.session["tempImage"]
    print(dbImgdata)
    with connection.cursor() as cursor:
        if(theOTP == mOTP):
                ar = cursor.execute('INSERT INTO drishtikon_users(name, email, password,register_time, user_type, user_image, user_login,examcredits) values(%s,%s,%s,%s,%s,%s,%s,%s)', (dbName, dbEmail, dbPassword,datetime.datetime.now(), dbUser_type, dbImgdata,0,7))
                if ar > 0:
                    messages.success(request,"Thanks for registering! You are sucessfully verified!.")
                    return redirect("/login/")
                else:
                    messages.error(request,"Error Occurred!")
                    return redirect("/login/") 
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
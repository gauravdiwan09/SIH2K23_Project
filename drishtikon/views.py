from django.shortcuts import render,HttpResponse,redirect
from .mails import contact_us_email,otp_email
from django.contrib import messages
import math,random

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
    image_hidden=request.POST.get("image_hidden")
	request.session['tempName'] = name
	request.session['tempEmail'] = email
	request.session['tempPassword'] = password
	request.session['tempUT'] = user_type
	request.session['tempImage'] = imgdata
	sesOTP = generateOTP()
	request.session['tempOTP'] = sesOTP
	otp_email('MyProctor.ai - OTP Verification',"New Account opening - Your OTP Verfication code is "+sesOTP+".",email)
		# return redirect(url_for('verifyEmail'))
	return HttpResponse("Done")

# Register Page
def register_page(request):
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
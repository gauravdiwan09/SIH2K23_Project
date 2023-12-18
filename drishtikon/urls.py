from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="HomePage"),
    path("loginpage/", views.login_page, name="LoginPage"),
    path("login/", views.login, name="Login"),
    path("logout/", views.logout, name="Logout"),
    path("lostpassword/", views.lost_password, name="LostPassword"),
    path("lostpasswordpage/", views.lost_password_page, name="LostPasswordPage"),
    path("registerpage/", views.register_page, name="RegisterPage"),
    path("register/", views.register, name="Register"),
    path("contactpage/", views.contact_us_page, name="ContactUsPage"),
    path("sendquery/", views.send_query, name="SendQuery"),
    path("faq/", views.faq, name="FAQPage"),
    path("verifyOTPpage/", views.verify_otp_page, name="VerifyOTPPage"),
    path("verifyOTP/", views.verify_otp, name="VerifyOTP"),
    path("lpnewpwd/", views.lp_new_pwd, name="LpNewPwd"),
    path("changepasswordprofessor/", views.change_password_professor, name="ChangePasswordProfessor"),
    path("changepasswordstudent/", views.change_password_student, name="ChangePasswordStudent"),
    path("changepassword/", views.change_password, name="ChangePassword"),
    path("backenedimage/", views.backened_image, name="BackenedImage"),
    path("verifyemailpage/", views.verify_email_page, name="VerifyEmailPage"),
    path("verifyemail/", views.verify_email, name="VerifyEmail"),
    path("reportprofessor/", views.report_professor, name="ReportProfessor"),
    path("reportstudent/", views.report_student, name="ReportStudent"),
    path("reportprofessoremail/", views.report_professor_email, name="ReportProfessorEmail"),
    path("reportstudentemail/", views.report_student_email, name="ReportStudentEmail"),
    path("studentindex/", views.student_index, name="StudentIndexPage"),
    path("professorindex/", views.professor_index, name="ProfessorIndexPage"),
    path("createtestpage/", views.create_test_page, name="CreateTestPage"),
    path("createtest/", views.create_test, name="CreateTest"),
    path("givetestpage/", views.give_test_page, name="GiveTestPage"),
    path("givetest/", views.give_test, name="GiveTest"),
    path("generatetestpage/", views.generate_test_page, name="GenerateTestPage"),
    path("viewquestionspage/", views.view_questions_page, name="ViewQuestionsPage"),
    path("displayquestionspage/", views.display_questions_page, name="DisplayQuestionsPage"),
    path("updatetidlist/", views.update_tid_list, name="UpdateTIDList"),
    path("deltidlist/", views.del_tid_list, name="DelTIDList"),
    path("updatedispques/", views.update_disp_ques, name="UpdateDispQues"),
    path("deldispques/", views.del_disp_ques, name="DelDispQues"),
    path("sharedetailsemails/", views.share_details_emails, name="ShareDetailsEmails"),
    path("livemonitoringtid/", views.live_monitoring_tid, name="LiveMonitoringTID"),
    path("livemonitoring/", views.live_monitoring, name="LiveMonitoring"),
    path("viewstudentslogs/", views.view_students_logs, name="ViewStudentsLogs"),
    path("displaystudentsdetails/", views.display_students_details, name="DisplayStudentsDetails"),
    path("createtestpqapage/", views.create_test_pqa_page, name="CreateTestPqaPage"),
    path("createtestpqa/", views.create_test_pqa, name="CreateTestPqa"),
    path("insertmarkstid/", views.insert_marks_tid, name="InsertMarksTID"),
    path("publishresultstestid/", views.publish_results_testid, name="PublishResultsTestid"),
    path("test/<str:testid>/", views.test, name="Test"),
    path("submittest/<str:testid>/", views.submit_test, name="SubmitTest"),
    path("deletequestions/<str:testid>/", views.delete_questions, name="DeleteQuestions"),
    path("updatetestpage/<str:testid>/<str:qid>/", views.update_test_page, name="UpdateTestPage"),
    path("updatetest/<str:testid>/<str:qid>/", views.update_test, name="UpdateTest"),
    path("<str:email>/disptests/", views.disp_tests, name="DisplayTests"),
    path("<str:email>/testscreated/", views.tests_created, name="TestsCreated"),
    path("<str:email>/studenttesthistory/", views.student_test_history, name="StudentTestHistory"),
    path("<str:email>/testsgivenpage/", views.tests_given_page, name="TestsGivenPage"),
    path("<str:email>/testsgiven/", views.tests_given, name="TestsGiven"),
    path("<str:email>/studentresults/<str:testid>/", views.student_results, name="StudentResults"),
    path("<str:email>/<str:testid>/sharedetails/", views.share_details, name="ShareDetails"),
    # path("examtypecheck/<str:tidoption>/", views.examtypecheck, name="ExamTypeCheck"),
    ]
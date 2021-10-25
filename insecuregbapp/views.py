import datetime
from django.contrib.auth import authenticate, login as li, logout as lg
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .models import Message, Visitor
from django.db import connection
from .poor_crypto import poor_substitution_cipher as psc
from .confused_user_management import insecure_user_transfer as iut

def index(request):
    all_messages = Message.objects.all()
    #context = {"messages": all_messages}
    insecure_username = ""
    if request.user.id == None:
        insecure_username = "anonymous"
    else:
        insecure_username = request.user.username
    context = {"messages": all_messages, "insec_user": insecure_username}
    return render(request, "insecuregbapp/index.html", context=context)

@csrf_exempt
def login(request):
    if request.method == "POST":
        lg(request)
        username = request.POST.get("oldusername")
        password = request.POST.get("oldpassword")
        old_user = authenticate(request, username=username, password=password)
        if old_user is not None:
            li(request, old_user)
            return redirect("/insecuregbapp/")
        else:
            return redirect("login")
    return render(request, "insecuregbapp/login.html")

@csrf_exempt
def register(request):
    if request.method == "POST":
        new_visitor = Visitor(visitor_name=request.POST.get("newusername"))
        #new_visitor.visitor_pass = request.POST.get("newpassword")
        new_visitor.visitor_pass = psc(psc(request.POST.get("newpassword"),'R'),'L')
        new_visitor.save()
        #new_user = User.objects.create_user(username=new_visitor.visitor_name, password=new_visitor.visitor_pass)
        #new_user.is_superuser = new_visitor.admin_true
        #new_user.is_staff = new_visitor.admin_true
        #new_user.save()
        new_user = iut(new_visitor)
        lg(request)
        li(request, new_user)
        return redirect("/insecuregbapp/")
    return render(request, "insecuregbapp/register.html")

def logout(request):
    lg(request)
    return redirect("/insecuregbapp/")

def addmessage(request):
    newcontent = request.GET.get("newmessage")
    if request.user.id == None:
        current_user = Visitor(visitor_name="anonymous")
        current_user.save()
    #else:
    #current_user = Visitor.objects.get(visitor_name=request.user.username)
    #print(request.user.username)
    #print(request.GET.get("insecure_username"))
    current_user = Visitor.objects.get(visitor_name=request.GET.get("insecure_username"))
    #newmessage = Message(content=newcontent, timestamp=datetime.datetime.now(), author=current_user)
    newmessage = Message(content="", timestamp=datetime.datetime.now(), author=current_user)
    newmessage.save()
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM insecuregbapp_message ORDER BY timestamp DESC LIMIT 1")
        use_id = cursor.fetchone()[0]
        cursor.execute("UPDATE insecuregbapp_message SET content='" + newcontent + "' WHERE id=%s", [use_id])
    return redirect("/insecuregbapp/")

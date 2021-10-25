from django.contrib.auth.models import User
from django.db import connection
from .models import Visitor

def insecure_user_transfer(new_visitor):
    new_user = User.objects.create_user(username=new_visitor.visitor_name, password=new_visitor.visitor_pass)
    new_user.is_superuser = new_visitor.admin_true
    new_user.is_staff = new_visitor.admin_true
    new_user.save()
    return new_user

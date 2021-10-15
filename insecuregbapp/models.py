from django.db import models

class Visitor(models.Model):
    visitor_name = models.CharField(max_length=200)
    visitor_pass = models.CharField(max_length=8)
    admin_true = models.IntegerField(default=1)

class Message(models.Model):
    content = models.CharField(max_length=5000)
    timestamp = models.DateTimeField()
    author = models.ForeignKey(Visitor, on_delete=models.CASCADE)
    def __str__(self):
        return self.content

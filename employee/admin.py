from django.contrib import admin
from .models import CustomUser, FormField, Employee

admin.site.register(CustomUser)
admin.site.register(FormField)
admin.site.register(Employee)
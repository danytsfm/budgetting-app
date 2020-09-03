from django.contrib import admin
from .models import Project, Expenses, Category, UserProfile

admin.site.register(Project)
admin.site.register(Expenses)
admin.site.register(Category)
admin.site.register(UserProfile)


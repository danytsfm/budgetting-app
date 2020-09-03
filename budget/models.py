from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User


class Project(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    budget = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    status = models.CharField(max_length=20, null='active')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Project, self).save(*args, **kwargs)

    def budget_left(self):
        expense_list = Expenses.objects.filter(project=self)
        total_expense_amount = 0
        for expense in expense_list:
            total_expense_amount += expense.amount
        return self.budget - total_expense_amount

    def total_transactions(self):
        expense_list = Expenses.objects.filter(project=self)
        return len(expense_list)

    def __str__(self):
        return f'{self.name}'


class Category(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.name}'


class Expenses(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='expenses')
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='categories')

    class Meta:
        ordering = ('-amount',)

    def __str__(self):
        return f' {self.title}'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    profile_pic = models.ImageField(upload_to=user, blank=True)

    def __str__(self):
        return f'{self.user}'

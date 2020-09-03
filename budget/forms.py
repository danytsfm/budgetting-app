from django import forms

class ExpensesForm(forms.Form):
    title = forms.CharField()
    amount = forms.IntegerField()
    category = forms.CharField()


class SignupForm(forms.Form):
    first_name = forms.CharField(label='First Name', max_length=100)
    last_name = forms.CharField(label='Last Name', max_length=100)
    email = forms.CharField(label='Email', max_length=100, widget=forms.EmailInput)
    password = forms.CharField(label='Password', max_length=32, widget=forms.PasswordInput)
    profile_pic = forms.ImageField(label='PhotoVerify ID  ')


class LoginForm(forms.Form):
    email = forms.CharField(label='Email', widget=forms.EmailInput, required=True)
    password = forms.CharField(label='Password', widget=forms.PasswordInput, required=True)
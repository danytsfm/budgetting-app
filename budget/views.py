import json
import os


import face_recognition
import cv2
import numpy as np

from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.urls import reverse, path, include
from django.shortcuts import render, get_object_or_404

from .forms import ExpensesForm, SignupForm, LoginForm
from .models import Project, Category, Expenses, UserProfile
from django.views.generic import CreateView
from django.utils.text import slugify



# Create your views here.


def index(request):
    return render(request, 'budget/index.html')


@login_required(login_url='user_login')
def home(request):
    project_list = Project.objects.values('id', 'name', 'slug', 'budget').filter(user=request.user.id, status='active')
    return render(request, 'budget/home.html', {'project_list': project_list})


@login_required(login_url='user_login')
def project_detail(request, project_slug):
    project = get_object_or_404(Project, slug=project_slug)

    if request.method == 'GET':
        category_list = Category.objects.filter(project=project)
        return render(request, 'budget/project_detail.html',
                      {'project': project, 'expense_list': project.expenses.all(), 'category_list': category_list})

    elif request.method == 'POST':
        form = ExpensesForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            amount = form.cleaned_data['amount']
            category_name = form.cleaned_data['category']

            category = get_object_or_404(Category, project=project, name=category_name)

            Expenses.objects.create(
                project=project,
                title=title,
                amount=amount,
                category=category
            ).save()

    elif request.method == 'DELETE':
        id = json.loads(request.body)['id']
        expense = get_object_or_404(Expenses, id=id)
        expense.delete()
        return HttpResponseRedirect(project_slug)

    return HttpResponseRedirect(project_slug)


@login_required(login_url='user_login')
def archived_projects(request):
    project_list = Project.objects.values('id', 'name', 'slug', 'budget').filter(user=request.user.id, status='done')
    return render(request, 'budget/archived_projects.html', {'project_list': project_list})


@login_required(login_url='user_login')
def update_status(request, project_id):
    project = Project.objects.get(id=project_id)
    project.status = 'done'
    project.save()
    return HttpResponseRedirect(reverse('home'))


class ProjectCreateView(CreateView):

    model = Project
    template_name = 'budget/add-project.html'
    fields = ('name', 'budget')

    def form_valid(self, form):

        # self.object = form.save(commit=False)
        # self.object.save()
        name = self.request.POST['name']
        budget = self.request.POST['budget']
        user = self.request.user.id
        self.object = Project.objects.create(
            name=name,
            budget=budget,
            user=User.objects.get(id=user),
            status='active'
        )
        self.object.save()
        categories = self.request.POST['categoriesString'].split(',')
        for category in categories:
            Category.objects.create(
                project=Project.objects.get(id=self.object.id),
                name=category
            ).save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return slugify(self.request.POST['name'])


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        try:
            if form.is_valid():
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                profile_pic = form.cleaned_data['profile_pic']
                user = User.objects.create_user(email, email, password, first_name=first_name, last_name=last_name)
                UserProfile.objects.create(user=user, profile_pic=profile_pic)
                return render(request, 'budget/signup.html', {'message': 'Account successfully created', 'form':form})
        except IntegrityError:
            form = SignupForm()
            return render(request, 'budget/signup.html', {'message': 'Email already registered', 'form': form})
    else:
        form = SignupForm()
    return render(request, 'budget/signup.html', {'form': form})


def face_dect(location):
    cam = cv2.VideoCapture(0)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MEDIA_ROOT = os.path.join(BASE_DIR, '')
    location = (str(MEDIA_ROOT) + location)
    face_name = face_recognition.load_image_file(location)
    face_name_encoding = face_recognition.face_encodings(face_name)[0]
    process_this_frame = True
    while True:
        das, frame = cam.read()
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]
        if process_this_frame:
            cv2.imshow('frame', frame)
            cv2.waitKey(delay=50)
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            matches = face_recognition.compare_faces(face_name_encoding, face_encodings, tolerance=0.5)
            face_distances = face_recognition.face_distance(face_name_encoding, face_encodings)
            best_match_index = np.argmin(face_distances)
            cam.release()
            cv2.destroyAllWindows()
            if matches[best_match_index]:
                return True
            else:
                return False


def user_login(request):
    if request.method == "POST":
        try:
            form = LoginForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                user = authenticate(request, username=email, password=password)
                if user is not None:
                    if face_dect(user.userprofile.profile_pic.url):
                        login(request, user)
                        return HttpResponseRedirect(reverse('home'))
                    else:
                        return render(request, 'budget/login.html',
                                      {'form': form,
                                       'message': "Your picture doesn't match. Please try again"})
                else:
                    return render(request, 'budget/login.html',
                                  {'form': form, 'message': "Your username and password didn't match. Please try again"})
        except ValueError:
            return render(request, 'budget/login.html',
                          {'form': form, 'message': "Your username and password didn't match. Please try again"})
    else:
        form = LoginForm()
    return render(request, 'budget/login.html', {'form': form})


def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

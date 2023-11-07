from django.shortcuts import render,redirect 
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q 
from .models import Room,Topic ,Message 
from .forms import RoomForm ,UserForm
from django.contrib.auth.models import User 
from django.contrib.auth import authenticate,login ,logout 
from django.contrib import messages 
# Create your views here.

# rooms = [
#      {'id': 1, 'name': 'learn python'},
#      {'id': 2, 'name': 'Design with me'},
#      {'id': 3, 'name': 'front end'},
#      {'id': 4, 'name': 'backend development '},
# ]
def loginPage(request):
     page = 'login'
     if request.user.is_authenticated: 
          return redirect('home')
     if request.method == 'POST':
          username = request.POST.get('username').lower()
          password = request.POST.get('password')
          try : 
               user = User.objects.get(username=username)
          except : 
               # messages.add_message(request,message="user doesnot exist")
               messages.error(request,"user doesnot exist")
          user = authenticate(request,username=username,password=password)
          if user is not None : 
               login(request,user)
               return redirect('home')
          else : 
               messages.error(request,"Username or password is doesnot exist")

     context = {'page':page}
     return render(request,'base/login_register.html',context)

def logoutUser(request):
     logout(request)
     return redirect('home')

def registerUser(request):
     form = UserCreationForm()
     if request.method == 'POST':
          form = UserCreationForm(request.POST)
          if form.is_valid():
               user = form.save(commit=False)
               user.username = user.username.lower()
               user.save()
               login(request,user)
               return redirect('home')
          else : 
               messages.error(request,'An error occured while registering')
     return render(request,'base/login_register.html',{'form' : form})

def home(request):
     q = request.GET.get('q')
     activity_messages=Message.objects.all()
     if q is not None: 
          rooms = Room.objects.filter(
               Q(topic__name__icontains=q)| 
               Q(name__icontains=q)
               )
          activity_messages = Message.objects.filter(
          Q(room__topic__name__icontains=q)
          )    
     else : rooms = Room.objects.all()
     topic = Topic.objects.all()
     room_count = rooms.count()
     
     return render(request,'base/home.html',{'rooms' : rooms,'topics':topic,'room_count':room_count,'activity_messages':activity_messages})

def room(request,pk):
     curr = Room.objects.get(id=pk)
     room_message = curr.message_set.all().order_by('-created')
     participants = curr.participants.all()
     if request.method == "POST":
          message = Message.objects.create(
               user=request.user,
               room = curr,
               body=request.POST.get('body')
          )
          curr.participants.add(request.user)
          return redirect('room',pk=curr.id)
     
     context = {'room':curr,'room_message':room_message,'participants':participants}
     return render(request,'base/room.html',context)

def userProfile(request,pk):
     # print(pk)
     user = User.objects.get(id=pk)
     rooms = user.room_set.all()
     activity_messages = user.message_set.all()
     topics = Topic.objects.all()
     context = {'user':user,'rooms':rooms,'activity_messages':activity_messages,'topics':topics}
     return render(request,'base/profile.html',context)

@login_required(login_url='login')
def createroom(request):
     form = RoomForm()
     # print(form)
     topics = Topic.objects.all()
     if request.method == 'POST' : 
          topic_name = request.POST.get('topic')
          topic,create = Topic.objects.get_or_create(name=topic_name)
          # form = RoomForm(request.POST) 
          Room.objects.create(
               host=request.user,
               topic=topic,
               name=request.POST.get('name'),
               description=request.POST.get('description')
          )
          
          return redirect('home')
     context = {'form':form,'topics':topics}
     return render(request,'base/room_form.html',context)

@login_required(login_url='login')
def updateroom(request,pk):
     room = Room.objects.get(id=pk)
     form = RoomForm(instance=room)
     topics = Topic.objects.all()
     if request.user != room.host : 
          return HttpResponse("your are not allowed here")
     if request.method == 'POST' : 
          topic_name = request.POST.get('topic')
          topic,create = Topic.objects.get_or_create(name=topic_name)
          room.name = request.POST.get('name')
          room.topic = topic 
          room.description = request.POST.get('description')
          room.save()
          return redirect('home')
     
     context = {'form':form,'topics':topics}
     return render(request,'base/room_form.html',context)

@login_required(login_url='login')
def deleteroom(request,pk):
     room = Room.objects.get(id=pk)
     
     # print(room.host,request.user)
     # if request.user != room.host : 
          # return HttpResponse("your are not allowed here")
     if request.method == 'POST' : 
          room.delete()
          return redirect('home')
     return render(request,'base/delete.html',{'obj':room})

@login_required(login_url='login')
def deleteMessage(request,pk):
     message = Message.objects.get(id=pk)
     if request.user != message.user : 
          return HttpResponse("your are not allowed here")
     if request.method == 'POST' : 
          message.delete()
          return redirect('home')
     return render(request,'base/delete.html',{'obj':message})


@login_required(login_url='login')
def updateUser(request):
     user = request.user 
     form = UserForm(instance=user)
     if request.method == 'POST' : 
          form = UserForm(request.POST,instance=user)
          if form.is_valid() :
               form.save()
               return redirect('user-profile',pk=user.id)
     return render(request,'base/update-user.html',{'form':form})
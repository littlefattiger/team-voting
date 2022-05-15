from django.shortcuts import render, redirect



# Create your views here.

def index(request):
    user = request.GET.get('user')
    if not user:
        return redirect('login/')
    return render(request, 'index.html')

def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        try:
            user = request.POST["user"]
            if user and len(user) > 0:
                return redirect('/index/',{"user":user})
            else:
                return render(request, 'login.html')
        except:
            return render(request, 'login.html')


from django.shortcuts import render, redirect


# Create your views here.

def index(request):
    user = request.GET.get('user')
    if not user:
        return redirect('/login/')
    context = {
        "user": user,
        "group": 31415126
    }
    return render(request, 'index.html', context)


def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        try:
            user = request.POST["user"]
            print(user)
            if user and len(user) > 0:
                return redirect(f"/index/?user={user}")
            else:
                return render(request, 'login.html')
        except:
            return render(request, 'login.html')

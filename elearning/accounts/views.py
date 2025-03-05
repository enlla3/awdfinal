from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CustomUserCreationForm, StatusUpdateForm
from .models import CustomUser, StatusUpdate

# User registration view
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registration successful.")
            login(request, user)
            return redirect('accounts:home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

# User login view
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('accounts:home')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'accounts/login.html')

# User logout view
@login_required
def user_logout(request):
    logout(request)
    return redirect('accounts:login')

# Home view with status update
@login_required
def home(request):
    if request.method == 'POST':
        form = StatusUpdateForm(request.POST)
        if form.is_valid():
            status = form.save(commit=False)
            status.user = request.user
            status.save()
            messages.success(request, "Status update posted!")
            return redirect('accounts:home')
    else:
        form = StatusUpdateForm()
    statuses = request.user.status_updates.all().order_by('-created_at')
    return render(request, 'accounts/home.html', {'user': request.user, 'form': form, 'statuses': statuses})

# User search view for teachers
@login_required
def search_users(request):
    if request.user.role != 'teacher':
        messages.error(request, "Only teachers can search for users.")
        return redirect('accounts:home')

    query = request.GET.get('q', '')
    results = None
    if query:
        results = CustomUser.objects.filter(
            Q(username__icontains=query) | Q(real_name__icontains=query)
        )
    return render(request, 'accounts/search_users.html', {'results': results, 'query': query})

# Public profile view
@login_required
def public_profile(request, username):
    User = get_user_model()
    profile_user = get_object_or_404(User, username=username)

    # Get status updates for this user
    statuses = profile_user.status_updates.all().order_by('-created_at')

    # If teacher, show courses they created, if student, show courses they enrolled in.
    if profile_user.role == 'teacher':
        courses = profile_user.courses.all()
    else:
        # For students
        courses = profile_user.enrolled_courses.all()

    context = {
        'profile_user': profile_user,
        'statuses': statuses,
        'courses': courses,
    }
    return render(request, 'accounts/public_profile.html', context)

from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate, logout
from django.contrib.auth.forms import PasswordResetForm, AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import PasswordResetView, LoginView, LogoutView
from django.urls import reverse
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from .forms import CustomUserCreationForm, CustomLoginForm, CustomPasswordResetForm
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from apps.users.models import User
from apps.users.serializers import UserSerializer
from rest_framework.permissions import IsAdminUser
from apps.articles.views import IsAdmin


def homepage(request):
    return render(request, 'users/homepage.html')
    
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account has been created. You can now log in.")
            return redirect('users:login')  # Replace 'login' with your login URL name
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})



def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                print(f"User authenticated: {user.is_authenticated}")  # Debugging
                print(f"Redirecting user: {user.username}")
                if user.role == 'admin':
                    print("Redirecting to Admin Dashboard")
                    return redirect('users:admin_dashboard')
                elif user.role == 'editor':
                    print("Redirecting to Editor Dashboard")
                    return redirect('users:editor_dashboard')
                elif user.role == 'journalist':
                    print("Redirecting to Journalist Dashboard")
                    return redirect('users:journalist_dashboard')
                else:
                    print("Redirecting to Default Dashboard")
                    return redirect('users:default_dashboard')
            else:
                form.add_error(None, "Invalid credentials")
        else:
            form.add_error(None, "Invalid credentials")
    else:
        form = AuthenticationForm()

    return render(request, 'users/login.html', {'form': form})

@login_required
# @user_passes_test(lambda u: u.role == 'Admin', login_url='users:login')
def admin_dashboard(request):
    return render(request, 'users/admin_dashboard.html')

@login_required
# @user_passes_test(lambda u: u.role == 'Editor', login_url='users:login')
def editor_dashboard(request):
    return render(request, 'users/editor_dashboard.html')

@login_required
# @user_passes_test(lambda u: u.role == 'Journalist', login_url='users:login')
def journalist_dashboard(request):
    return render(request, 'users/journalist_dashboard.html')





# form = CustomLoginForm()
# @login_required
# def login_view(request):
#     if request.user.is_staff:  # Assuming 'is_staff' identifies admin users
#         return redirect('admin:index')  # Redirects to Django's built-in admin dashboard
#     return redirect('users:dashboard')

def custom_password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({"error": "Email not found"}, status=400)

        # Generate reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(user.pk.encode())

        # Create the reset password URL
        reset_link = request.build_absolute_uri(
            f'/reset/{uid}/{token}/'
        )

        # Send the email
        subject = "Password Reset Request"
        message = render_to_string(
            'registration/password_reset_email.html',
            {'user': user, 'reset_link': reset_link}
        )
        send_mail(subject, message, settings.EMAIL_HOST_USER, [email])

        return JsonResponse({"message": "Password reset email sent successfully"}, status=200)

    return render(request, 'password_reset_form.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('users:login')

class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    authentication_form = CustomLoginForm

class CustomLogoutView(LogoutView):
    template_name = 'users/logout.html'

class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy('users:password_reset_done')
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'

# class PasswordResetDoneView(PasswordResetView):
#     template_name = 'users/password_reset_done.html'
#     success_url = reverse_lazy('users:password_reset_complete')

# def dashboard_view(request):
#     return render(request, 'users/dashboard.html')

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated & IsAdmin]

    @action(detail=True, methods=['post'])
    def approve_user(self, request, pk=None):
        user = self.get_object()
        user.is_approved = True
        user.save()
        return Response({"detail": f"User {user.username} approved successfully."})
 

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import render, redirect
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import CustomUser, FormField, Employee
from .serializers import (
    MyTokenObtainPairSerializer, 
    RegisterSerializer, 
    ChangePasswordSerializer,
    UpdateUserSerializer,
    FormFieldSerializer,
    EmployeeSerializer
)

class MyTokenObtainPairView(TokenObtainPairView):
    """Custom token obtain view that uses MyTokenObtainPairSerializer for JWT authentication."""
    serializer_class = MyTokenObtainPairSerializer

class RegisterView(APIView):
    """API view for user registration that returns JWT tokens upon successful registration."""
    
    def post(self, request, *args, **kwargs):
        """
        Handle user registration.
        
        Args:
            request: The HTTP request containing user registration data.
            
        Returns:
            Response: Contains user data and JWT tokens if successful, 
                     or validation errors if registration fails.
        """
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': serializer.data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(generics.UpdateAPIView):
    """API view for changing user password."""
    queryset = CustomUser.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        """Get the currently authenticated user."""
        return self.request.user

    def update(self, request, *args, **kwargs):
        """
        Handle password change logic.
        
        Args:
            request: The HTTP request containing old and new password.
            
        Returns:
            Response: Success message if password changed successfully,
                     or error messages if validation fails.
        """
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response({"status": "success"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateProfileView(generics.UpdateAPIView):
    """API view for updating user profile information."""
    queryset = CustomUser.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UpdateUserSerializer

    def get_object(self):
        """Get the currently authenticated user."""
        return self.request.user

class FormFieldListCreateView(generics.ListCreateAPIView):
    """API view for listing and creating form fields."""
    queryset = FormField.objects.all()
    serializer_class = FormFieldSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """Associate the created form field with the current user."""
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        """Return only form fields created by the current user."""
        return self.queryset.filter(created_by=self.request.user)

class FormFieldRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """API view for retrieving, updating and deleting form fields."""
    queryset = FormField.objects.all()
    serializer_class = FormFieldSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return only form fields created by the current user."""
        return self.queryset.filter(created_by=self.request.user)

class EmployeeListCreateView(generics.ListCreateAPIView):
    """API view for listing and creating employees."""
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Create an employee and associate it with the current user.
        Also ensures the user has an employee profile.
        """
        user = self.request.user
        employee = serializer.save(user=user)
        
        # Create a corresponding CustomUser if needed
        if not hasattr(user, 'employee'):
            Employee.objects.create(user=user, fields={})

class EmployeeRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """API view for retrieving, updating and deleting employees."""
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return only employees associated with the current user."""
        return self.queryset.filter(user=self.request.user)


def login_view(request):
    """
    Handle user login via web interface.
    
    Args:
        request: The HTTP request containing login credentials.
        
    Returns:
        HttpResponse: Rendered login page or redirect to profile on success.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            return render(request, 'login.html', {'error': 'Please enter both email and password.'})

        user = CustomUser.objects.filter(email=email).first()

        if user and user.check_password(password):
            login(request, user)
            return redirect('profile')
        else:
            return render(request, 'login.html', {'error': 'Incorrect email or password.'})

    return render(request, 'login.html')


def register_view(request):
    """
    Handle user registration via web interface.
    
    Args:
        request: The HTTP request containing registration data.
        
    Returns:
        HttpResponse: Rendered registration page or redirect to login on success.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        if password != password2:
            return render(request, 'register.html', {'error': 'Passwords do not match'})
        
        if CustomUser.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error': 'Email already exists'})
        
        user = CustomUser.objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password
        )
        return render(request, 'login.html')
    return render(request, 'login.html')

@login_required
def profile_view(request):
    """
    Display the user's profile page.
    
    Args:
        request: The HTTP request.
        
    Returns:
        HttpResponse: Rendered profile page with user data.
    """
    user = request.user
    return render(request, 'profile.html', {'user': user})

@login_required
def change_password_view(request):
    """
    Handle password change via web interface.
    
    Args:
        request: The HTTP request containing old and new passwords.
        
    Returns:
        HttpResponse: Rendered password change page or redirect to login on success.
    """
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        new_password2 = request.POST.get('new_password2')
        
        if new_password != new_password2:
            return render(request, 'change_password.html', {'error': 'New passwords do not match'})
        
        if not request.user.check_password(old_password):
            return render(request, 'change_password.html', {'error': 'Old password is incorrect'})
        
        request.user.set_password(new_password)
        request.user.save()
        return redirect('login')
    
    return render(request, 'change_password.html')

@login_required
def logout_view(request):
    """
    Handle user logout.
    
    Args:
        request: The HTTP request.
        
    Returns:
        HttpResponseRedirect: Redirect to login page.
    """
    logout(request)
    return redirect('login')

@login_required
def form_design_view(request):
    """
    Handle form field creation and display via web interface.
    
    Args:
        request: The HTTP request containing form field data.
        
    Returns:
        HttpResponse: Rendered form design page with existing fields.
    """
    if request.method == 'POST':
        label = request.POST.get('label')
        field_type = request.POST.get('field_type')
        required = request.POST.get('required') == 'on'
        
        FormField.objects.create(
            label=label,
            field_type=field_type,
            required=required,
            created_by=request.user
        )
        return redirect('form_design')
    
    fields = FormField.objects.filter(created_by=request.user).order_by('order')
    return render(request, 'form_design.html', {'fields': fields})

@login_required
def employee_create_view(request):
    """
    Handle employee creation via web interface using custom form fields.
    
    Args:
        request: The HTTP request containing employee data.
        
    Returns:
        HttpResponse: Rendered employee creation page or redirect to employee list on success.
    """
    if request.method == 'POST':
        fields = {}
        form_fields = FormField.objects.filter(created_by=request.user)
        
        for field in form_fields:
            field_value = request.POST.get(f'field_{field.id}')
            fields[field.label] = {
                'value': field_value,
                'type': field.field_type
            }
        
        Employee.objects.create(
            user=request.user,
            fields=fields
        )
        return redirect('employee_list')
    
    form_fields = FormField.objects.filter(created_by=request.user)
    return render(request, 'employee_create.html', {'fields': form_fields})

@login_required
def employee_list_view(request):
    """
    Display list of employees with search functionality.
    
    Args:
        request: The HTTP request, optionally containing search query.
        
    Returns:
        HttpResponse: Rendered employee list page with search results.
    """
    employees = Employee.objects.filter(user=request.user)
    form_fields = FormField.objects.filter(created_by=request.user)
    
    search_query = request.GET.get('search', '')
    if search_query:
        employees = employees.filter(fields__icontains=search_query)
    
    return render(request, 'employee_list.html', {
        'employees': employees,
        'fields': form_fields,
        'search_query': search_query
    })

@login_required
def employee_edit_view(request, pk):
    """
    Handle employee data editing via web interface.
    
    Args:
        request: The HTTP request containing updated employee data.
        pk: Primary key of the employee to edit.
        
    Returns:
        HttpResponse: Rendered employee edit page or redirect to employee list on success.
    """
    employee = Employee.objects.get(pk=pk, user=request.user)
    
    if request.method == 'POST':
        fields = {}
        form_fields = FormField.objects.filter(created_by=request.user)
        
        for field in form_fields:
            field_value = request.POST.get(f'field_{field.id}')
            fields[field.label] = {
                'value': field_value,
                'type': field.field_type
            }
        
        employee.fields = fields
        employee.save()
        return redirect('employee_list')
    
    form_fields = FormField.objects.filter(created_by=request.user)
    return render(request, 'employee_edit.html', {
        'employee': employee,
        'fields': form_fields
    })

@login_required
def employee_delete_view(request, pk):
    """
    Handle employee deletion.
    
    Args:
        request: The HTTP request.
        pk: Primary key of the employee to delete.
        
    Returns:
        HttpResponseRedirect: Redirect to employee list.
    """
    employee = Employee.objects.get(pk=pk, user=request.user)
    employee.delete()
    return redirect('employee_list')

@login_required
def update_field_order(request):
    """
    Handle AJAX request for updating form field order.
    
    Args:
        request: The AJAX POST request containing new field order.
        
    Returns:
        JsonResponse: Success or error status.
    """
    if request.method == 'POST' and request.is_ajax():
        order = request.POST.getlist('order[]')
        for idx, field_id in enumerate(order):
            FormField.objects.filter(id=field_id, created_by=request.user).update(order=idx)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)
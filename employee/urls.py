from django.urls import path
from .views import (
    MyTokenObtainPairView,
    RegisterView,
    ChangePasswordView,
    UpdateProfileView,
    FormFieldListCreateView,
    FormFieldRetrieveUpdateDestroyView,
    EmployeeListCreateView,
    EmployeeRetrieveUpdateDestroyView,
    login_view,
    register_view,
    profile_view,
    change_password_view,
    logout_view,
    form_design_view,
    employee_create_view,
    employee_list_view,
    employee_edit_view,
    employee_delete_view,
    update_field_order
)

urlpatterns = [
    # API Endpoints
    path('api/login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('api/update-profile/', UpdateProfileView.as_view(), name='update_profile'),
    path('api/form-fields/', FormFieldListCreateView.as_view(), name='form_field_list_create'),
    path('api/form-fields/<int:pk>/', FormFieldRetrieveUpdateDestroyView.as_view(), name='form_field_retrieve_update_destroy'),
    path('api/employees/', EmployeeListCreateView.as_view(), name='employee_list_create'),
    path('api/employees/<int:pk>/', EmployeeRetrieveUpdateDestroyView.as_view(), name='employee_retrieve_update_destroy'),
    
    # HTML Views
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('profile/', profile_view, name='profile'),
    path('change-password/', change_password_view, name='change_password'),
    path('logout/', logout_view, name='logout'),
    
    # Form and Employee Management
    path('form-design/', form_design_view, name='form_design'),
    path('employee/create/', employee_create_view, name='employee_create'),
    path('employee/list/', employee_list_view, name='employee_list'),
    path('employee/edit/<int:pk>/', employee_edit_view, name='employee_edit'),
    path('employee/delete/<int:pk>/', employee_delete_view, name='employee_delete'),
    path('update-field-order/', update_field_order, name='update_field_order'),
]
from django.urls import path
from .import views

urlpatterns = [
    path('',views.dashboard,name='dashboard'),
    path('register/',views.register,name='register'),
    path('login/',views.login,name='login'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('forgotpassword/',views.forgotpassword,name='forgotpassword'),
    path('resetpassword/',views.resetpassword,name='resetpassword'),
    path('checkout/',views.checkout,name='checkout'),
    

    path('activate/<uidb64>/<token>/',views.activate, name='activate'),
    path('reset_validation/<uidb64>/<token>/',views.reset_validation, name='reset_validation'),

    path('myorders/',views.myorders,name='myorders'),
    path('editprofile/',views.editprofile,name='editprofile'),
    path('changepassword/',views.changepassword,name='changepassword'),
    path('orderdetails/<str:order_number>/',views.orderdetails,name='orderdetails')


]
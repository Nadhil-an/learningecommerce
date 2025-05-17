from django.urls import path
from . import views

urlpatterns = [
    path('placeorder/', views.placeorder, name='placeorder'),
    path('payments/',views.payments,name='payments'),
    path('ordercomplete/',views.ordercomplete,name='ordercomplete'),
    path('download-invoice/<str:order_number>/', views.download_invoice_pdf, name='download_invoice'),


]


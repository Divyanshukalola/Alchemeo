# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from app import views


app_name = "main"

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('dashboard/', views.dashboard, name='homdashboarde'),
    path('Invoice_dashboard/', views.Invoice_dashboard, name='Invoice_dashboard'),
    path('Inventory_dashboard/', views.Inventory_dashboard, name='Inventory_dashboard'),
    path('save_invoice/', views.save_invoice, name='save_invoice'),
    path('delete_invoice/', views.delete_invoice, name='delete_invoice'),
    path('add_item/', views.add_item, name='add_item'),
    path('editProduct/', views.editProduct, name='editProduct'),
    path('deleteProduct/', views.deleteProduct, name='deleteProduct'),
    path('Profile/', views.Profile, name='Profile'),
    path('ProfUpdate/', views.ProfUpdate, name='ProfUpdate'),
    path('Messages/', views.Messages, name='Messages'),
    path('AccessRequest1/', views.AccessRequest1, name='AccessRequest1'),
    path('ProfPicUpdate/', views.ProfPicUpdate, name='ProfPicUpdate'),
    path('edit_invoice/', views.edit_invoice, name='edit_invoice'),
    path('download_csv_data/', views.download_csv_data, name='download_csv_data'),
    path('add_tag/', views.add_tag, name='add_tag'),
    path('import_items/', views.import_items, name='import_items'),
    path('DeleteItems/', views.DeleteItems, name='DeleteItems'),
    path('view_invoice/', views.html2pdf, name='html2pdf'),
    path('bankUpdate/', views.bankUpdate, name='bankUpdate'),
    path('ProfInfoUpdate/', views.ProfInfoUpdate, name='ProfInfoUpdate'),
    path('tocUpdate/', views.tocUpdate, name='tocUpdate'),
    path('aboutus/', views.aboutus, name='aboutus'),
    path('invoices/', views.invoices, name='invoices'),



  
    

    # Matches any html file
    # re_path(r'^.*\.*', views.pages, name='pages'),


]

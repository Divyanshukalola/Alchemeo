# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from os import stat
from typing import Tuple
from django.contrib.auth.decorators import login_required
from django.db.models.fields import NullBooleanField
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django import template
from . models import Inventory,Product,SalesUser,Invoice,InvoiceItem,AccessRequest,ItemStock,DefinedTags,ProductTags,TagsTotal
import uuid, random, string
from datetime import date,datetime
import re
from django.contrib import messages
from django.core.mail import send_mail
from core import settings
import csv
from django.utils.encoding import smart_str
from decimal import *
import csv


from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
import math

from django.http import HttpResponse
from django.views.generic import View

from .utils import Render #created in step 4

from xhtml2pdf import pisa


def ran_gen(size, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

    # USE = "ran_gen(8, "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890")""


def index(request):
    return render(request, 'home.html')

def sort_dict_by_value(d, reverse = False):
  return dict(sorted(d.items(), key = lambda x: x[1], reverse = reverse))

@login_required(login_url="/login/")
def dashboard(request):
  
    try:
        Salesuser = request.user.salesuser

    except:
        inventory = Inventory(Inventory_user=request.user,
                                    Inventory_name =request.user.username,
                                    Inventory_ID=ran_gen(8, "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"))
        inventory.save()
        Salesuser = SalesUser(Sales_User = request.user,Inventory_access=True,SalesUser_Inventory=inventory,SalesUser_ID= ran_gen(10, "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"))
        Salesuser.save()

        messages.info(request, f"Welcome to Alchemeo! Enjoy Billing!")

    try:
        
        Inventory_items = request.user.salesuser.SalesUser_Inventory.product_set.all().count()
    
    except:
        Inventory_c = 0
        Inventory_items = 0

    Invoices_c = Salesuser.invoice_set.all().count()
    
    Invoice_total = 0
    
    Invoices_values = [0,0,0,0,0,0,0,0,0,0,0,0]
    Invoices_Number = [0,0,0,0,0,0,0,0,0,0,0,0]
    todays_date = date.today()
    Invoice_year = todays_date.year
    TagsTot = {}
    Items_sales = {}
    Item_names = {}
    confirmed = 0
    pending = 0
  

    for tg in request.user.salesuser.SalesUser_Inventory.definedtags_set.all():
        key = str(tg.Tag_Title)
        TagsTot.update({key:0})
    
    for i in request.user.salesuser.invoice_set.all():
        if i.Invoice_Total_Amount != 0:
            Invoice_total = Invoice_total + i.Invoice_Total_Amount
        
        if i.Invoice_Date.year == Invoice_year:
            Invoices_values[i.Invoice_Date.month-1]=float(Invoices_values[i.Invoice_Date.month-1]) + float(i.Invoice_Total_Amount)
            Invoices_Number[i.Invoice_Date.month-1]=Invoices_Number[i.Invoice_Date.month-1] + 1
        
        if i.Invoice_status:
            confirmed = confirmed +1
        else:
            pending = pending +1

        for t in i.tagstotal_set.all():
            TagsTot[t.Defined_Tags] = round(float(TagsTot[t.Defined_Tags]) + float(t.Tag_total),2)

        for item in i.invoiceitem_set.all():
            if item.Item_Quantity > 0:
                total = 0
                try:
                    total = Items_sales[item.Item_ID] + item.Item_Quantity
                except:
                    total = item.Item_Quantity
                
                Items_sales.update({(item.Item_ID):total})
        
                
            
    sort = sort_dict_by_value(Items_sales, True)
    IDS = []
    SalesValues = []
    stat1 = False
    stat2 = False
    for i in sort:
        IDS.append(str(i))
        SalesValues.append(sort[i])
    
    for i in Invoices_values:
        if i > 0:
            stat1 = True
    
    for i in Invoices_Number:
        if i > 0:
            stat2 = True
        
    followers = 0

    for i in request.user.inventory.salesuser_set.all():
        if i.Inventory_access:
            followers = followers + 1


    Item_ID = []
    Invoice_names = []
    MemberID = []
    Products = {}
    list_product = request.user.salesuser.SalesUser_Inventory.product_set.all()

    try:

        if request.user.salesuser.Inventory_access:
            Inventory_products = request.user.salesuser.SalesUser_Inventory.product_set.all()
            for i in Inventory_products:
                text = f"{i.Product_ID} : {i.Product_name}"
                Item_ID.append(text[:50])
                key = i.Product_ID+' : '+i.Product_name
                
                Products.update({key:[i.Product_mrp,
                                        i.Product_sprice,
                                        ((i.Product_gst_per/100)+1),
                                        [str(t.Defined_Tags.Tag_Title)+"-"+str(t.Tag_value) for t in i.producttags_set.all()],
                                        i.Product_stock]})
    
        else:
            Inventory_products = 0
        Invoices = request.user.salesuser.invoice_set.all().order_by('-Invoice_Date')
        for i in Invoices:
            Invoice_names.append(i.Invoice_Title)
            MemberID.append(i.Invoice_member_ID)
        
    except:
        Inventory_products = 0
        Invoices = 0
    
    
    SaleUser = request.user.salesuser



    res = []
    for i in MemberID:
        if i not in res:
            res.append(i)
    
    MemberID = res


    res1 = []
    for i in Invoice_names:
        if i not in res1:
            res1.append(i)
    Invoice_names = res1
    
  
    context = {'Invoices_c' : Invoices_c,
                'Invoice_total' :Invoice_total,
                'Inventory_items' :Inventory_items,
                'Invoices_values' :Invoices_values,
                'Invoices_Number' :Invoices_Number,
                'TagsTot' :TagsTot,
                'Tags' :request.user.salesuser.SalesUser_Inventory.definedtags_set.all(),
                'ItemsIDs': IDS,
                'ItemSales': SalesValues,
                'stat1': stat1,
                'stat2': stat2,
                'followers':followers,
                'confirmed':confirmed,
                'pending':pending,
                'Invoice_year':Invoice_year,
                'Inventory_products':Inventory_products,
                'Invoices':Invoices,
                'Item_ID_main':Item_ID,
                'Invoice_names':Invoice_names,
                'MemberID':MemberID,
                'SaleUser':SaleUser,
                'Products': Products,
                'list_product':list_product,

                }
    context['segment'] = 'dashboard'

    html_template = loader.get_template( 'dashboard.html' )
    return HttpResponse(html_template.render(context, request))

# @login_required(login_url="/login/")
# def pages(request):
    
#     Item_ID = []
#     Invoice_names = []
#     MemberID = []
#     Products = {}

#     try:

#         Inventory_products = request.user.inventory.product_set.all()
#         Invoices = request.user.salesuser.invoice_set.all()
#         SaleUser = request.user.salesuser
#     except:
#         Inventory_products = 0
#         Invoices = 0
    
#     for i in Inventory_products:
#         Item_ID.append(f"{i.Product_ID} - {i.Product_name}")
#         print(Item_ID)
#         Products.update({i.Product_ID:[i.Product_mrp,i.Product_sprice]})
    
#     for i in Invoices:
#         Invoice_names.append(i.Invoice_Title)
#         MemberID.append(i.Invoice_member_ID)

    

#     context = {'Inventory_products':Inventory_products,
#                 'Invoices':Invoices,
#                 'Item_ID_main':Item_ID,
#                 'Invoice_names':Invoice_names,
#                 'MemberID':MemberID,
#                 'SaleUser':SaleUser,
#                 'Products': Products}
#     # All resource paths end in .html.
#     # Pick out the html file name from the url. And load that template.
   
    
#     load_template      = request.path.split('/')[-1]
#     if load_template.endswith('.html'):
#         context['segment'] = load_template
        
#         html_template = loader.get_template( load_template )
#         return HttpResponse(html_template.render(context, request))
#     else:
#         image_data = open(request.path, "rb").read()
#         return HttpResponse(image_data, mimetype="image/png")

@login_required(login_url="/login/")
def Invoice_dashboard(request):
    
    
    Item_ID = []
    Invoice_names = []
    MemberID = []
    Products = {}
    list_product = request.user.salesuser.SalesUser_Inventory.product_set.all()

    try:

        if request.user.salesuser.Inventory_access:
            Inventory_products = request.user.salesuser.SalesUser_Inventory.product_set.all()
            for i in Inventory_products:
                text = f"{i.Product_ID} : {i.Product_name}"
                Item_ID.append(text[:50])
                key = i.Product_ID+' : '+i.Product_name
                
                Products.update({key:[i.Product_mrp,
                                        i.Product_sprice,
                                        ((i.Product_gst_per/100)+1),
                                        [str(t.Defined_Tags.Tag_Title)+"-"+str(t.Tag_value) for t in i.producttags_set.all()],
                                        i.Product_stock]})
    
        else:
            Inventory_products = 0
        Invoices = request.user.salesuser.invoice_set.all().order_by('-Invoice_Date')
        for i in Invoices:
            Invoice_names.append(i.Invoice_Title)
            MemberID.append(i.Invoice_member_ID)
        
    except:
        Inventory_products = 0
        Invoices = 0
    
    
    SaleUser = request.user.salesuser



    res = []
    for i in MemberID:
        if i not in res:
            res.append(i)
    
    MemberID = res


    res1 = []
    for i in Invoice_names:
        if i not in res1:
            res1.append(i)
    Invoice_names = res1




    try:
        Salesuser = request.user.salesuser

    except:
        inventory = Inventory(Inventory_user=request.user,
                                    Inventory_name =request.user.username,
                                    Inventory_ID=ran_gen(8, "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"))
        inventory.save()
        Salesuser = SalesUser(Sales_User = request.user,Inventory_access=True,SalesUser_Inventory=inventory,SalesUser_ID= ran_gen(10, "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"))
        Salesuser.save()

        messages.info(request, f"Welcome to Alchemeo! Enjoy Billing!")

    try:
        
        Inventory_items = request.user.salesuser.SalesUser_Inventory.product_set.all().count()
    
    except:
        Inventory_c = 0
        Inventory_items = 0

    Invoices_c = Salesuser.invoice_set.all().count()
    
    Invoice_total = 0
    
    Invoices_values = [0,0,0,0,0,0,0,0,0,0,0,0]
    Invoices_Number = [0,0,0,0,0,0,0,0,0,0,0,0]
    todays_date = date.today()
    Invoice_year = todays_date.year
    TagsTot = {}
    Items_sales = {}
    Item_names = {}
    confirmed = 0
    pending = 0
  

    for tg in request.user.salesuser.SalesUser_Inventory.definedtags_set.all():
        key = str(tg.Tag_Title)
        TagsTot.update({key:0})
    
    for i in request.user.salesuser.invoice_set.all():
        if i.Invoice_Total_Amount != 0:
            Invoice_total = Invoice_total + i.Invoice_Total_Amount
        
        if i.Invoice_Date.year == Invoice_year:
            Invoices_values[i.Invoice_Date.month-1]=float(Invoices_values[i.Invoice_Date.month-1]) + float(i.Invoice_Total_Amount)
            Invoices_Number[i.Invoice_Date.month-1]=Invoices_Number[i.Invoice_Date.month-1] + 1
        
        if i.Invoice_status:
            confirmed = confirmed +1
        else:
            pending = pending +1

        for t in i.tagstotal_set.all():
            TagsTot[t.Defined_Tags] = round(float(TagsTot[t.Defined_Tags]) + float(t.Tag_total),2)

        for item in i.invoiceitem_set.all():
            if item.Item_Quantity > 0:
                total = 0
                try:
                    total = Items_sales[item.Item_ID] + item.Item_Quantity
                except:
                    total = item.Item_Quantity
                
                Items_sales.update({(item.Item_ID):total})
        
                
            
    sort = sort_dict_by_value(Items_sales, True)
    IDS = []
    SalesValues = []
    stat1 = False
    stat2 = False
    for i in sort:
        IDS.append(str(i))
        SalesValues.append(sort[i])
    
    for i in Invoices_values:
        if i > 0:
            stat1 = True
    
    for i in Invoices_Number:
        if i > 0:
            stat2 = True
        
    followers = 0

    for i in request.user.inventory.salesuser_set.all():
        if i.Inventory_access:
            followers = followers + 1

        
            


    context = {'Inventory_products':Inventory_products,
                'Invoices':Invoices,
                'Item_ID_main':Item_ID,
                'Invoice_names':Invoice_names,
                'MemberID':MemberID,
                'SaleUser':SaleUser,
                'Products': Products,
                'list_product':list_product,
                'Invoices_values':Invoices_values,
                'Invoices_Number':Invoices_Number}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
   
    
    load_template      = 'Invoices.html'
    if load_template.endswith('.html'):
        context['segment'] = load_template
        
        html_template = loader.get_template( load_template )
        return HttpResponse(html_template.render(context, request))
    else:
        image_data = open(request.path, "rb").read()
        return HttpResponse(image_data, mimetype="image/png")

@login_required(login_url="/login/")
def Inventory_dashboard(request):
    status = False
    if request.user.inventory.Inventory_ID == request.user.salesuser.SalesUser_Inventory.Inventory_ID:
        status = True
    
    
    Item_ID = []
    Invoice_names = []
    MemberID = []
    Products = {}
    tags = request.user.inventory.definedtags_set.all()
    

    

    try:
        if request.user.salesuser.Inventory_access:
            Inventory_products = request.user.salesuser.SalesUser_Inventory.product_set.all()
            for i in Inventory_products:
                Item_ID.append(f"{i.Product_ID} : {i.Product_name}")
                
                Products.update({i.Product_ID:[i.Product_mrp,i.Product_sprice]})
                

    
        else:
            Inventory_products = 0
        Invoices = request.user.salesuser.invoice_set.all()
        for i in Invoices:
            Invoice_names.append(i.Invoice_Title)
       
        
    except:
        Inventory_products = 0
        Invoices = 0
    
    SaleUser = request.user.salesuser
   

    context = {'Inventory_products':Inventory_products,
                'Invoices':Invoices,
                'Item_ID_main':Item_ID,
                'Invoice_names':Invoice_names,
                'MemberID':MemberID,
                'SaleUser':SaleUser,
                'Products': Products,
                'status':status,
                'tags':tags}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
   
    
    load_template      = 'Inventory.html'
    if load_template.endswith('.html'):
        context['segment'] = load_template
        
        html_template = loader.get_template( load_template )
        return HttpResponse(html_template.render(context, request))
    else:
        image_data = open(request.path, "rb").read()
        return HttpResponse(image_data, mimetype="image/png")



@login_required(login_url="/login/")
def Profile(request):
    
    try:

        Inventory_products = request.user.salesuser.SalesUser_Inventory.product_set.all()
        Invoices = request.user.salesuser.invoice_set.all()
        
    except:
        Inventory_products = 0
        Invoices = 0
    SaleUser = request.user.salesuser

    requestFound = False
    Inventorystatus = False

    RejectedStatus = False

    # if


    # if SaleUser.accessrequest_set.all().count:
    #     requestFound = True
    # elif SaleUser.Inventory_access == False:
    #     RejectedStatus = True
    # else:
    #     RejectedStatus = False
    context = {'SaleUser':SaleUser,
                'RejectedStatus':RejectedStatus
                }
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
   
    
    load_template = 'profile.html'
    if load_template.endswith('.html'):
        context['segment'] = load_template
        
        html_template = loader.get_template( load_template )
        return HttpResponse(html_template.render(context, request))
    else:
        image_data = open(request.path, "rb").read()
        return HttpResponse(image_data, mimetype="image/png")
        

@login_required(login_url="/login/")
def Messages(request):
    
    try:

        Messages = request.user.inventory.accessrequest_set.all()
        
    except:
        Messages = 0
        
    
    

    context = {'Messages':Messages,
                }
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
   
    
    load_template      = 'messages.html'
    if load_template.endswith('.html'):
        context['segment'] = load_template
        
        html_template = loader.get_template( load_template )
        return HttpResponse(html_template.render(context, request))
    else:
        image_data = open(request.path, "rb").read()
        return HttpResponse(image_data, mimetype="image/png")
        
# saves the invoice 

def save_invoice(request):
    if request.method == 'POST':

        # for inv in request.user.salesuser.invoice_set.all():
        #     if len(request.user.salesuser.invoice_set.filter(Invoice_ID=inv.Invoice_ID)) > 1:
        #         pass
        #     else:
        #         pass

        status  = False
        check = False
        if request.POST.get('customCheck2') == 'on':
            check = True
        else:
            check = False



        if (len(request.POST.get('invoiceID')) > 0):
            status = True
        else:
            status = False
        
        print("-------------",status,'-------------',request.POST.get('invoiceID'))

        if status == False:
            numberofitems = request.POST.get('numberofitems')
            print("Status = New")
        
            Invoice_info = [
                request.POST.get('InvoiceName').capitalize(),
                request.POST.get('MemberID1').upper(),
                request.POST.get('cinfo'),
                request.POST.get('SubTotal'),
                request.POST.get('FinalTotal'),
                request.POST.get('gstnumber').upper(),
                request.POST.get('comments'),
                check
            ]
           
            
            if Invoice_info[3] != '':
                Invoices = request.user.salesuser.invoice_set.all().order_by('-Invoice_ID')
                print(Invoices)

                NewInvoice = Invoice(Invoice_Title=Invoice_info[0],
                                    Invoice_ContactInfo=Invoice_info[2],
                                    Invoice_member_ID=Invoice_info[1],
                                    Invoice_User=request.user.salesuser,
                                    Invoice_ID = str(datetime.now().strftime('%y'))+"-"+str(int(datetime.now().strftime('%y'))+1)+"-"+str(int(Invoices[0].Invoice_ID.split('-')[2])+1),
                                    Invoice_Inventory = request.user.salesuser.SalesUser_Inventory,
                                    Invoice_Date = datetime.now(),
                                    Invoice_Total_Amount = Invoice_info[4],
                                    Invoice_SubTotal_Amount = Invoice_info[3],
                                    Invoice_gst_number = request.user.salesuser.Invoice_GST_no,
                                    Invoice_comments=Invoice_info[6],
                                    Invoice_status = Invoice_info[7]
                                    )

                NewInvoice.save()

                for tg in request.user.salesuser.SalesUser_Inventory.definedtags_set.all():
                    getcontext().prec = 5
                    
                    tagtotal = TagsTotal(Defined_Tags = tg.Tag_Title,
                                            Tag_Invoice = NewInvoice,
                                            Tag_total = float(str(request.POST.get('tag'+tg.Tag_Title))))
                    tagtotal.save()

                Inventory_products = request.user.salesuser.SalesUser_Inventory.product_set.all()
            
                for i in range(0,int(numberofitems)):
            
                    Quantity = 'Quantity'+str(i)
                    Qprice = 'priceperQuantity'+str(i)
                    ItemName = 'ItemName'+str(i)
                    ItemID = request.POST.get(ItemName).split(' : ')
                    print(request.POST.get(ItemName),"-------------------------------",i)
                
                    for p in Inventory_products:
                        
                        if (str(p.Product_ID) == str(ItemID[0])):
                            if NewInvoice.invoiceitem_set.all().filter(Item_ID=ItemID[0]):
                                updateItem = NewInvoice.invoiceitem_set.filter(Item_ID=ItemID[0])[0]
                                updateItem.Item_Quantity = int(updateItem.Item_Quantity) + int(request.POST.get(Quantity))
                                if p.Product_stock > 0:
                                    updateItem.Item_stock = p.Product_stock - int(request.POST.get(Quantity))
                                else:
                                    updateItem.Item_stock = 0
                                updateItem.save(update_fields=['Item_Quantity','Item_stock'])

                            else:
                                newItem = InvoiceItem(Item_Invoice = NewInvoice,
                                                        Item_ID=p.Product_ID,
                                                        Item_stock=p.Product_stock - int(request.POST.get(Quantity)),
                                                        Item_name = p.Product_name,
                                                        Item_gst = p.Product_gst_per,
                                                        Item_Quantity=request.POST.get(Quantity),
                                                        Item_price=request.POST.get(Qprice))
                                
                                if len(NewInvoice.Invoice_member_ID) == 9:
                                    newItem.Member = True
                                
                                if p.Product_stock > 0:
                                    newItem.save()
                                    p.Product_stock = p.Product_stock - int(request.POST.get(Quantity))
                                    p.save(update_fields=['Product_stock'])
                                else:
                                    p.Product_stock = 0
                                    p.save(update_fields=['Product_stock'])
                    
                #ItemList.append([request.POST.get(ItemName),request.POST.get(Qprice),request.POST.get(Quantity),request.POST.get(Tprice)])

                messages.success(request, f"Your Invoice '{NewInvoice.Invoice_Title} {NewInvoice.Invoice_ID}' was Successfully Created!")
                
                
            else:
                pass
            return redirect('main:Invoice_dashboard')
        else:
            print("Status = Edit")
            numberofitems = request.POST.get('numberofitems')
            
            Invoice_info = [
                request.POST.get('InvoiceName').capitalize(),
                request.POST.get('MemberID1').upper(),
                request.POST.get('cinfo'),
                request.POST.get('SubTotal'),
                request.POST.get('FinalTotal'),
                request.POST.get('gstnumber').upper(),
                request.POST.get('comments'),
                check
            ]

            print("This is a check : ",check)
            
        
            EditInvoice = Invoice.objects.filter(Invoice_ID=request.POST.get('invoiceID'))[0]
            
            EditInvoice.Invoice_Title=Invoice_info[0]
            EditInvoice.Invoice_ContactInfo=Invoice_info[2]
            EditInvoice.Invoice_member_ID=Invoice_info[1]
            EditInvoice.Invoice_User=request.user.salesuser
            
            EditInvoice.Invoice_Inventory = request.user.salesuser.SalesUser_Inventory
            EditInvoice.Invoice_Date = datetime.now()  #Change is the date must be updates
            EditInvoice.Invoice_Total_Amount = Invoice_info[4]
            EditInvoice.Invoice_SubTotal_Amount = Invoice_info[3]
            EditInvoice.Invoice_gst_number = request.user.salesuser.Invoice_GST_no
            EditInvoice.Invoice_comments = Invoice_info[6]
            EditInvoice.Invoice_status = check

            EditInvoice.save(update_fields=['Invoice_comments','Invoice_Title','Invoice_ContactInfo','Invoice_status','Invoice_member_ID','Invoice_User','Invoice_ID','Invoice_Inventory','Invoice_Total_Amount','Invoice_SubTotal_Amount','Invoice_gst_number'])

            Inventory_products = request.user.salesuser.SalesUser_Inventory.product_set.all()

            for invoitem in  EditInvoice.invoiceitem_set.all():
                prod = request.user.salesuser.SalesUser_Inventory.product_set.filter(Product_ID = invoitem.Item_ID)[0]
                if prod != None:
                    prod.Product_stock = prod.Product_stock + invoitem.Item_Quantity
                    prod.save(update_fields=['Product_stock'])
                    #messages.info(request, f"Stocks Updated {prod.Product_stock}")
                else:
                    pass

            EditInvoice.invoiceitem_set.all().delete()
            EditInvoice.tagstotal_set.all().delete()

            for tg in request.user.salesuser.SalesUser_Inventory.definedtags_set.all():
                getcontext().prec = 5
                
                tagtotal = TagsTotal(Defined_Tags = tg.Tag_Title,
                                        Tag_Invoice = EditInvoice,
                                        Tag_total = float(str(request.POST.get('tag'+tg.Tag_Title))))
                tagtotal.save()
            

            
            
            for i in range(int(numberofitems)):
                try:
                    Quantity = 'Quantity'+str(i)
                    Qprice = 'priceperQuantity'+str(i)
                    ItemName = 'ItemName'+str(i)
                    ItemID = request.POST.get(ItemName).split(' : ')
                    

                    for p in Inventory_products:
                        
                        if (str(p.Product_ID) == str(ItemID[0])):
                            if EditInvoice.invoiceitem_set.all().filter(Item_ID=ItemID[0]):
                                updateItem = EditInvoice.invoiceitem_set.filter(Item_ID=ItemID[0])[0]
                                updateItem.Item_Quantity = int(updateItem.Item_Quantity) + int(request.POST.get(Quantity))
                                if p.Product_stock > 0:
                                    updateItem.Item_stock = p.Product_stock - int(request.POST.get(Quantity))
                                else:
                                    updateItem.Item_stock = 0
                                updateItem.save(update_fields=['Item_Quantity','Item_stock'])
                            else:
                                newItem = InvoiceItem(Item_Invoice = EditInvoice,
                                                        Item_ID=p.Product_ID,
                                        
                                                        Item_name = p.Product_name,
                                                        Item_gst = p.Product_gst_per,
                                                        Item_Quantity=request.POST.get(Quantity),
                                                        Item_price=request.POST.get(Qprice))
                            
                            if len(EditInvoice.Invoice_member_ID) == 9:
                                newItem.Member = True

                            if p.Product_stock > 0:
                                newItem.save()
                                p.Product_stock = p.Product_stock - int(request.POST.get(Quantity))
                                p.save(update_fields=['Product_stock'])
                            else:
                                p.Product_stock = 0
                                p.save(update_fields=['Product_stock'])
                            #messages.info(request, f"Item saved {p.Product_name}")
                except:
                    pass
            messages.success(request, f"Your Invoice '{EditInvoice.Invoice_Title} {EditInvoice.Invoice_ID}' was Successfully Edited!")
            return redirect('main:Invoice_dashboard')
    else:
        messages.error(request, f"System Error!")



def delete_invoice(request):
    if request.method == 'POST':
        for i in request.user.salesuser.invoice_set.all():
            if i.Invoice_ID == request.POST.get('ID'):
                messages.success(request, f"Your Invoice {i.Invoice_ID} is Deleted!")
                i.delete()
    else:
        messages.error(request, f"System Error!")
    return redirect('main:Invoice_dashboard')


def add_item(request):
    if request.method == "POST" and request.user.salesuser.Inventory_access:
        try:
            image = request.FILES['productimage']
        except:
            image = False
        typep = 'Goods'
        if request.POST.get('goods'):
            typep = 'Goods'
        elif request.POST.get('services'):
            typep = 'Services'
        else:
            pass
        data = [
            request.POST.get('productname'), #0
            request.POST.get('productid').upper(), #1
            request.POST.get('skucode').upper(), #2
            request.POST.get('ppu'), #3
            request.POST.get('unit'), #4
            
            request.POST.get('substituteprice'), #5
            
            request.POST.get('Description'), #7
            request.POST.get('gst'), #8
            request.POST.get('discount'), #9
            request.POST.get('stock') #10
            
        ]
        if request.user.salesuser.Inventory_access == False:
            messages.success(request, f"You don't have access to this inventory!")
            return redirect('main:Inventory_dashboard')

        if image != False:
            product = Product(
                Product_inventory = request.user.salesuser.SalesUser_Inventory,
                Product_image = image,
                Product_name = data[0],
                Product_ID = data[1],
                Product_mrp = data[3]+((data[8]/100)*data[3]),
                Product_sprice = data[5],
                Product_description = data[7],
                Product_gst_per = data[8],
                Product_stock = data[10],
                Product_type = typep,
                Product_SKU_Code = data[2],
                Product_price_unit = data[3],
                Product_discount = data[9],
                Product_unit = data[4]
            )
            product.save()
            for t in request.user.salesuser.SalesUser_Inventory.definedtags_set.all():
                value = "tag"+t.Tag_Title
                ProductTag = ProductTags(Defined_Tags = t,
                                            Tag_Item = product,
                                            Tag_value = request.POST.get(value))
                ProductTag.save()
            messages.success(request, f"Your Item {product.Product_ID} is Added to your Inventory Successful!")
        else:
            product = Product(
                Product_inventory = request.user.salesuser.SalesUser_Inventory,
                Product_name = data[0],
                Product_ID = data[1],
                Product_mrp = int(data[3])+((int(data[8])/100)*int(data[3])),
                Product_sprice = data[5],
                Product_description = data[7],
                Product_gst_per = data[8],
                Product_stock = data[10],
                Product_type = typep,
                Product_SKU_Code = data[2],
                Product_price_unit = data[3],
                Product_discount = data[9],
                Product_unit = data[4]
            )
            product.save()
            for t in request.user.salesuser.SalesUser_Inventory.definedtags_set.all():
                value = "tag"+t.Tag_Title
                ProductTag = ProductTags(Defined_Tags = t,
                                            Tag_Item = product,
                                            Tag_value = request.POST.get(value))
                ProductTag.save()
            messages.success(request, f"Your Item {product.Product_ID} is Added to your Inventory Successful!")

       
    else:
        messages.error(request, f"Permission Error!")
    return redirect('main:Inventory_dashboard')


def editProduct(request):
    if request.method == "POST" and request.user.salesuser.Inventory_access:
        if request.user.inventory.Inventory_ID == request.user.salesuser.SalesUser_Inventory.Inventory_ID:
            try:
                image = request.FILES['productimage']
            except:
                image = False
            data = [
                request.POST.get('productname'),
                request.POST.get('productid').upper(),
                request.POST.get('mrp'),
                request.POST.get('substituteprice'),
                request.POST.get('substitutepricetags'),
                request.POST.get('Description'),
                request.POST.get('gst'),
                request.POST.get('pstock')

            ]

            for d in range(len(data)-1):
                if data[d] == '' and d != 5:
                    data[d] = '0'
                elif d == 5 and data[d] == '':
                    data[d] == 'N/A'
                else:
                    pass

            for p in request.user.salesuser.SalesUser_Inventory.product_set.all():
                if p.Product_ID == data[1]:

                    for tg in p.producttags_set.all():
                        tg.Tag_value = request.POST.get('tag'+tg.Defined_Tags.Tag_Title)
                        tg.save(update_fields=['Tag_value'])

                    try:
                            if image != False:
                                p.Product_image = image
                            else:
                                pass
                            p.Product_name = data[0]
                            p.Product_ID = data[1]
                            p.Product_mrp = data[2]
                            p.Product_sprice = data[3]
                            p.Product_description = data[5]
                            p.Product_gst_per = data[6]
                            p.Product_stock = data[7]
                            p.save(update_fields=["Product_name","Product_ID","Product_mrp","Product_sprice","Product_description","Product_image","Product_gst_per","Product_stock"])
                            messages.success(request, f"Your Item {p.Product_ID} is Updated!")
                            return redirect('main:Inventory_dashboard')
                    except:
                        
                            
                            p.Product_name = data[0]
                            p.Product_ID = data[1]
                            p.Product_mrp = data[2]
                            p.Product_sprice = data[3]
                            p.Product_description = data[5]
                            p.Product_gst_per = data[6]

                            p.save(update_fields=["Product_name","Product_ID","Product_mrp","Product_sprice","Product_description","Product_gst_per"])
                            messages.success(request, f"Your Item {p.Product_ID} is Updated!")
                            return redirect('main:Inventory_dashboard')
                    
                    
                        

        else:
            messages.error(request, f"You are not allowed to make any changes in this inventory!")
                
    else:
        messages.error(request, f"System Error!")
    return redirect('main:Inventory_dashboard')

def deleteProduct(request):
    if request.method == "POST" and request.user.salesuser.Inventory_access:
        if request.user.inventory.Inventory_ID == request.user.salesuser.SalesUser_Inventory.Inventory_ID:
            for p in request.user.salesuser.SalesUser_Inventory.product_set.all():
                if p.Product_ID == request.POST.get('itemid'):
                    messages.success(request, f"Your Item {p.Product_ID} is Deleted!")
                    p.delete()
        else:
            messages.error(request, f"You are not the owner of this inventory, you cannot make any changes!")
    else:
        messages.error(request, f"Permission Error!")
    return redirect('main:Inventory_dashboard')


def ProfUpdate(request):
   
    
    if request.method == "POST":
        username = (request.POST.get('username'))
        email = (request.POST.get('user_email'))
        gst_number = (request.POST.get('gst_number'))
        inventory_id = (request.POST.get('inventory_id'))
        Address = request.POST.get('address')
       
        if inventory_id == request.user.inventory.Inventory_ID:
            SU = request.user.salesuser


            SU.SalesUser_Inventory = request.user.inventory
            SU.Inventory_access = True
            SU.save(update_fields=["SalesUser_Inventory","Inventory_access"])
        else:
            status = True
            if request.user.salesuser.Inventory_access == False:

                for r in request.user.salesuser.accessrequest_set.all():
                    if r.Requested_Inventory.Inventory_ID == inventory_id:
                        status = False

                for i in Inventory.objects.all():
                    if i.Inventory_ID == inventory_id:
                        if status:
                            RA = AccessRequest( Requested_Inventory = i,
                                                Request_from = request.user.salesuser,
                                                Request_ID = ran_gen(10, "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"))
                            RA.save()
                        else:
                            messages.info(request, f"Your request had already been placed!")

                        salesuser = request.user.salesuser

                        salesuser.SalesUser_Inventory = i
                        salesuser.Inventory_access = False
                        salesuser.save(update_fields=["SalesUser_Inventory","Inventory_access"])
        
        request.user.salesuser.SalesUser_Address = Address
        user_update = request.user
        user_update.username = username
        user_update.email = email
        user_update.save(update_fields=["username","email"])
        request.user.salesuser.save(update_fields=["SalesUser_Address"])

        
        salesuser = request.user.salesuser
        if len(gst_number) >5:
            salesuser.Invoice_GST_no = gst_number
        else:
            salesuser.Invoice_GST_no = "N/A"
       
        
        salesuser.save(update_fields=["Invoice_GST_no"])
    else:
        messages.error(request, f"System Error!")
    return redirect('main:Profile')

def AccessRequest1(request):
    if request.method == 'POST':
        status = (request.POST.get('action'))
        print(status,"=========================")
        for m in request.user.inventory.accessrequest_set.all():
            if m.Request_ID == request.POST.get('actionid'):
                if status == 'accept':
                    print('-------accept--------')
                    user_prof = m.Request_from
                    user_prof.Inventory_access = True

                    user_prof.save(update_fields=["Inventory_access"])

                
                    
                    m.delete()
                
                elif status == 'delete':
                    print('xxxxxxxxxxxxxxxxxxx')
                    m.delete()
                else:
                    pass
            else:
                pass

    else:
        messages.error(request, f"System Error!")
    page = request.POST.get('page')
    return redirect(f'main:{page}')


def ProfPicUpdate(request):
    if request.method == "POST":
        image = request.FILES['profpic']
        r_user = request.user.salesuser

        r_user.Sales_User_image = image
        r_user.save(update_fields=["Sales_User_image"])
    else:
        messages.error(request, f"System Error!")
    return redirect('main:Profile')



def edit_invoice(request):
    if request.method == "POST":
        
        for i in Invoice.objects.all():
            if i.Invoice_ID == request.POST.get('invoiceid'):
                if i.Invoice_User.SalesUser_ID == request.user.salesuser.SalesUser_ID:
                    Inventory_products = request.user.salesuser.SalesUser_Inventory.product_set.all()
                    invoice = i
                    total_amount = 0
                    subtotal_amount = 0
                    for p in invoice.invoiceitem_set.all():
                        p.delete()

                    for i in range(0,int(request.POST.get('numberofitems1'+i.Invoice_ID))):
                        Quantity = 'Quantity1'+str(i)
                        Qprice = 'priceperQuantity1'+str(i)
                        ItemName = 'ItemName1'+str(i)
                        ItemID = request.POST.get(ItemName).split(' : ')
                        print(ItemID[0])

                        
                        
                        for p in Inventory_products:
                            str1 = re.sub(' +', ' ', p.Product_ID)
                            str2 = re.sub(' +', ' ', ItemID[0])
                            print("Match  ------ ",str1,", ", str2,"----", str1 != str2)
                            if (str(p.Product_ID) == str(ItemID[0])) and p.Product_name == ItemID[1]:
                                newItem = InvoiceItem(Item_Invoice = invoice,
                                                        Item_ID=p.Product_ID,
                                                        Item_name = p.Product_name,
                                                        Item_gst = p.Product_gst_per,
                                                        Item_Quantity=request.POST.get(Quantity),
                                                        Item_price=request.POST.get(Qprice))
                                if len(request.user.salesuser.Invoice_GST_no) > 5:
                                    subtotal_amount = subtotal_amount + (int(request.POST.get(Quantity))*int(request.POST.get(Qprice)))
                                    total_amount = total_amount + (int(request.POST.get(Quantity))*int(request.POST.get(Qprice))*((p.Product_gst_per/100)+1))
                                else:
                                    subtotal_amount = subtotal_amount + (int(request.POST.get(Quantity))*int(request.POST.get(Qprice)))
                                    total_amount = total_amount + (int(request.POST.get(Quantity))*int(request.POST.get(Qprice)))

                                if len(invoice.Invoice_member_ID) > 5:
                                    newItem.Member = True
                                else:
                                    pass
                                newItem.save()
                    invoice.Invoice_SubTotal_Amount = subtotal_amount
                    invoice.Invoice_Total_Amount = total_amount
                    invoice.save(update_fields=["Invoice_SubTotal_Amount","Invoice_Total_Amount"])
    else:
        messages.error(request, f"System Error!")

    return redirect('main:Invoice_dashboard')


def download_csv_data(request):
    if request.method == "POST":
        start = request.POST.get('startdate')
        end = request.POST.get('enddate')
        print("-------",start,end)
        start = start.replace("/", "")
        end = end.replace("/", "")
        datetimeobject = datetime.strptime(start,'%m%d%Y')
        start = datetimeobject.strftime('%Y-%m-%d')

        datetimeobject = datetime.strptime(end,'%m%d%Y')
        end = datetimeobject.strftime('%Y-%m-%d')
        
        # response content type
        response = HttpResponse(content_type='text/csv')
        #decide the file name
        response['Content-Disposition'] = f'attachment; filename="Invoice-{start}-{end}.csv"'

        writer = csv.writer(response, csv.excel)
        response.write(u'\ufeff'.encode('utf8'))

        #write the headers
        writer.writerow([
            smart_str(u"Date"),
            smart_str(u"Invoice ID"),
            smart_str(u"Invoice Name"),
            smart_str(u"CT Info."),
            smart_str(u"Inventory ID"),
            smart_str(u"Member ID"),
            smart_str(u"Sub Total"),
            smart_str(u"Total"),
            smart_str(u"Items [Item ID, Item Name, Quantity, Price, Amount, Member] "),
        
        ])
        #get data from database or from text file....
        invoices = request.user.salesuser.invoice_set.filter(Invoice_Date__range=[start, end])
        print("Length = ",len(invoices))
        
        for i in invoices:
           
            items = [[it.Item_ID,it.Item_name,it.Item_Quantity,it.Item_price,(it.Item_price*it.Item_Quantity),it.Member] for it in i.invoiceitem_set.all()]
            
            writer.writerow([
                smart_str(i.Invoice_Date),
                smart_str(i.Invoice_ID),
                smart_str(i.Invoice_Title),
                smart_str(i.Invoice_ContactInfo),
                smart_str(i.Invoice_Inventory.Inventory_ID),
                smart_str(i.Invoice_member_ID),
                smart_str(i.Invoice_SubTotal_Amount),
                smart_str(i.Invoice_Total_Amount),
                smart_str(items),
                
            ])
        return response
    else:
        messages.error(request, f"System Error!")

def add_tag(request):
    if request.method == "POST" and request.user.salesuser.Inventory_access:
        if request.user.salesuser.SalesUser_Inventory.Inventory_ID == request.user.inventory.Inventory_ID:
            tags = [tg for tg in request.user.inventory.definedtags_set.all()]
            for i in range(int(request.POST.get('numberofitems1'))+1):
                TagName = request.POST.get('TagName'+str(i))
                Tagd = request.POST.get('Tagd'+str(i))
                print("--Status--",i,"--",TagName,"--",type(TagName), TagName == "")
                if TagName is not None:
                    if len(tags) == 0:
                        Tag = DefinedTags(Tag_Title=TagName.upper(),
                                            Tag_inventory=request.user.inventory,
                                            Tag_description=Tagd)
                        Tag.save()

                        for p in request.user.inventory.product_set.all():
                            pt = ProductTags(Defined_Tags=Tag,
                                            Tag_Item = p)
                            pt.save()
                        messages.success(request, f"Tags {TagName.upper()} Added!")
                    elif len(tags) < i:
                        Tag = DefinedTags(Tag_Title=TagName.upper(),
                                            Tag_inventory=request.user.inventory,
                                            Tag_description=Tagd)
                        Tag.save()

                        for p in request.user.inventory.product_set.all():
                            pt = ProductTags(Defined_Tags=Tag,
                                            Tag_Item = p)
                            pt.save()
                        messages.success(request, f"Tag {TagName.upper()} Added!")
                    elif (TagName == ""):
                        tags[i].delete()
                        messages.info(request, f"{TagName.upper()} Tag Deleted")

                    elif tags[i].Tag_Title == TagName and tags[i].Tag_description == Tagd:
                        tags[i].Tag_description = Tagd
                        tags[i].save(update_fields=['Tag_description'])

                    elif tags[i].Tag_Title == TagName:
                        tags[i].Tag_description = Tagd
                        tags[i].save(update_fields=['Tag_description'])
                        
                    elif tags[i].Tag_Title != TagName:
                        tags[i].Tag_Title = TagName
                        tags[i].Tag_description = Tagd
                        tags[i].save(update_fields=['Tag_Title','Tag_description'])
                        messages.success(request, f"Tags updated!")
                    else:
                        messages.info(request, f"System Error! No changes were made.")
                else:
                    pass
                        
        else:
            messages.error(request, f"You are not authorized to make any changes!")
        
    else:
        messages.error(request, f"Permission Error! ")
    
    

    return redirect('main:Inventory_dashboard')


def import_items(request):
    with open('MDItems.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 1
        for row in csv_reader:
            if line_count == 1:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                # print(f'\t{row[0]} ,{row[1]} , {row[2]}, {row[3]} , {row[4]} , {row[5]}')

                if row[0] != '':
                   
                
                    Item = Product(Product_inventory=request.user.inventory,
                                    Product_description=row[1],
                                    Product_name=row[1],
                                    Product_ID=row[0],
                                    Product_mrp=float(row[2]),
                                    Product_sprice=float(row[3]))
                else:
                    print("Found")

                Item.save()
                #print(Item.Product_ID)
                for tg in request.user.inventory.definedtags_set.all():
                    if tg.Tag_Title == 'BV':
                        pt = ProductTags(Defined_Tags=tg,
                                            Tag_Item=Item,
                                            Tag_value=row[4])
                        #print("Tags: ", pt.Defined_Tags)
                        pt.save()
                    elif tg.Tag_Title == 'PV':
                        pt = ProductTags(Defined_Tags=tg,
                                            Tag_Item=Item,
                                            Tag_value=row[5])
                        #print("Tags: ", pt.Defined_Tags)
                        pt.save()
                    else:
                        pass
                line_count += 1
        print(f'Processed {line_count} lines.')
    return redirect('main:Inventory_dashboard')

def DeleteItems(request):
    if request.user.salesuser.Inventory_access:
        request.user.inventory.product_set.all().delete()
    return redirect('main:Inventory_dashboard')



def html2pdf(request):
    
    salesuser = SalesUser.objects.filter(SalesUser_ID=request.GET.get('salesuserid'))[0]
    invoice = salesuser.invoice_set.filter(Invoice_ID=request.GET.get('invid'))[0]
    list_product = salesuser.SalesUser_Inventory.product_set.all()

    context = {'invoice':invoice,
                'list_product':list_product}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
   
    
    load_template      = 'html2pdf.html'
    if load_template.endswith('.html'):
        context['segment'] = load_template
        
        html_template = loader.get_template( load_template )
        return HttpResponse(html_template.render(context, request))
    else:
        image_data = open(request.path, "rb").read()
        return HttpResponse(image_data, mimetype="image/png")

def renderpdf(request):
    
    invoice = Invoice.objects.filter(Invoice_ID='21-22-3')[0]
    list_product = request.user.salesuser.SalesUser_Inventory.product_set.all()

    context = {'invoice':invoice,
            'list_product':list_product}
    pdf = Render.render('html2pdf.html', context)
    return HttpResponse(pdf, content_type='application/pdf')


def bankUpdate(request):
    
    if request.method == "POST":
        check = False
        if request.POST.get('customCheck2') == 'on':
            check = True
        else:
            check = False

        updatebank = request.user.salesuser
        updatebank.Sales_User_bnk_accnt_no = request.POST.get('actnumber')
        updatebank.Sales_User_bnk_code = request.POST.get('bnkcode')
        updatebank.Sales_User_bnk_name = request.POST.get('bnkname')
        updatebank.Sales_User_include_bnkdetails = check
       

        updatebank.save(update_fields=['Sales_User_bnk_accnt_no','Sales_User_bnk_code','Sales_User_bnk_name',"Sales_User_include_bnkdetails"])
        return redirect('main:Profile')
    else:
        return redirect('main:Profile')

def tocUpdate(request):
    
    if request.method == "POST":
        updatebank = request.user.salesuser
        
        updatebank.Sales_User_Terms_condition = request.POST.get('usertoc')

        updatebank.save(update_fields=['Sales_User_Terms_condition'])
        return redirect('main:Profile')
    else:
        return redirect('main:Profile')


def ProfInfoUpdate(request):

    
    if request.method == "POST":
        inventory = Inventory.objects.filter(Inventory_ID=request.POST.get("inventoryID"))[0]
        updatebank = request.user.salesuser
        updatebank.SalesUser_Address = request.POST.get('busadress')
        updatebank.Invoice_GST_no = request.POST.get('gstno')

        if inventory.Inventory_ID == request.user.inventory.Inventory_ID:
            updatebank.SalesUser_Inventory = inventory
            updatebank.Inventory_access = True
            updatebank.save(update_fields=['SalesUser_Address','Inventory_access','Invoice_GST_no','SalesUser_Inventory'])
        else:
            ar = AccessRequest(Requested_Inventory = inventory,
                                Request_from=request.user.salesuser,
                                Request_ID = ran_gen(8, "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"))
            ar.save()
            updatebank.SalesUser_Inventory = inventory
            updatebank.Inventory_access = False
            updatebank.save(update_fields=['SalesUser_Address','Invoice_GST_no','SalesUser_Inventory','Inventory_access'])

        

        user_update = request.user
        user_update.email = request.POST.get('email')
        user_update.username = request.POST.get('username')

        user_update.save(update_fields=['email','username'])

        return redirect('main:Profile')
    else:
        return redirect('main:Profile')



class Pdf(View):

    def get(self, request):
        invoice = Invoice.objects.filter(Invoice_ID='21-22-3')[0]
        list_product = request.user.salesuser.SalesUser_Inventory.product_set.all()

        context = {'invoice':invoice,
                'list_product':list_product}
        return Render.render('html2pdf.html', context)





def aboutus(request):
  
    context = {

                }
    context['segment'] = 'aboutus'

    html_template = loader.get_template( 'aboutus.html' )
    return HttpResponse(html_template.render(context, request))



def invoices(request):
  
    Item_ID = []
    Invoice_names = []
    MemberID = []
    Products = {}
    list_product = request.user.salesuser.SalesUser_Inventory.product_set.all()

    try:

        if request.user.salesuser.Inventory_access:
            Inventory_products = request.user.salesuser.SalesUser_Inventory.product_set.all()
            for i in Inventory_products:
                text = f"{i.Product_ID} : {i.Product_name}"
                Item_ID.append(text[:50])
                key = i.Product_ID+' : '+i.Product_name
                
                Products.update({key:[i.Product_mrp,
                                        i.Product_sprice,
                                        ((i.Product_gst_per/100)+1),
                                        [str(t.Defined_Tags.Tag_Title)+"-"+str(t.Tag_value) for t in i.producttags_set.all()],
                                        i.Product_stock]})
    
        else:
            Inventory_products = 0
        Invoices = request.user.salesuser.invoice_set.all().order_by('-Invoice_Date')
        for i in Invoices:
            Invoice_names.append(i.Invoice_Title)
            MemberID.append(i.Invoice_member_ID)
        
    except:
        Inventory_products = 0
        Invoices = 0
    
    
    SaleUser = request.user.salesuser



    res = []
    for i in MemberID:
        if i not in res:
            res.append(i)
    
    MemberID = res


    res1 = []
    for i in Invoice_names:
        if i not in res1:
            res1.append(i)
    Invoice_names = res1




    try:
        Salesuser = request.user.salesuser

    except:
        inventory = Inventory(Inventory_user=request.user,
                                    Inventory_name =request.user.username,
                                    Inventory_ID=ran_gen(8, "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"))
        inventory.save()
        Salesuser = SalesUser(Sales_User = request.user,Inventory_access=True,SalesUser_Inventory=inventory,SalesUser_ID= ran_gen(10, "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"))
        Salesuser.save()

        messages.info(request, f"Welcome to Alchemeo! Enjoy Billing!")

    try:
        
        Inventory_items = request.user.salesuser.SalesUser_Inventory.product_set.all().count()
    
    except:
        Inventory_c = 0
        Inventory_items = 0

    Invoices_c = Salesuser.invoice_set.all().count()
    
    Invoice_total = 0
    
    Invoices_values = [0,0,0,0,0,0,0,0,0,0,0,0]
    Invoices_Number = [0,0,0,0,0,0,0,0,0,0,0,0]
    todays_date = date.today()
    Invoice_year = todays_date.year
    TagsTot = {}
    Items_sales = {}
    Item_names = {}
    confirmed = 0
    pending = 0
  

    for tg in request.user.salesuser.SalesUser_Inventory.definedtags_set.all():
        key = str(tg.Tag_Title)
        TagsTot.update({key:0})
    
    for i in request.user.salesuser.invoice_set.all():
        if i.Invoice_Total_Amount != 0:
            Invoice_total = Invoice_total + i.Invoice_Total_Amount
        
        if i.Invoice_Date.year == Invoice_year:
            Invoices_values[i.Invoice_Date.month-1]=float(Invoices_values[i.Invoice_Date.month-1]) + float(i.Invoice_Total_Amount)
            Invoices_Number[i.Invoice_Date.month-1]=Invoices_Number[i.Invoice_Date.month-1] + 1
        
        if i.Invoice_status:
            confirmed = confirmed +1
        else:
            pending = pending +1

        for t in i.tagstotal_set.all():
            TagsTot[t.Defined_Tags] = round(float(TagsTot[t.Defined_Tags]) + float(t.Tag_total),2)

        for item in i.invoiceitem_set.all():
            if item.Item_Quantity > 0:
                total = 0
                try:
                    total = Items_sales[item.Item_ID] + item.Item_Quantity
                except:
                    total = item.Item_Quantity
                
                Items_sales.update({(item.Item_ID):total})
        
                
            
    sort = sort_dict_by_value(Items_sales, True)
    IDS = []
    SalesValues = []
    stat1 = False
    stat2 = False
    for i in sort:
        IDS.append(str(i))
        SalesValues.append(sort[i])
    
    for i in Invoices_values:
        if i > 0:
            stat1 = True
    
    for i in Invoices_Number:
        if i > 0:
            stat2 = True
        
    followers = 0

    for i in request.user.inventory.salesuser_set.all():
        if i.Inventory_access:
            followers = followers + 1

        
            


    context = {'Inventory_products':Inventory_products,
                'Invoices':Invoices,
                'Item_ID_main':Item_ID,
                'Invoice_names':Invoice_names,
                'MemberID':MemberID,
                'SaleUser':SaleUser,
                'Products': Products,
                'list_product':list_product,
                'Invoices_values':Invoices_values,
                'Invoices_Number':Invoices_Number}
    context['segment'] = 'listinvoices'

    html_template = loader.get_template( 'listinvoices.html' )
    return HttpResponse(html_template.render(context, request))
# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils.html import strip_tags

# Create your models here.
class Inventory(models.Model):

    Inventory_user = models.OneToOneField(User,on_delete=models.CASCADE, null=True)
    Inventory_name = models.CharField("Inventory Name",max_length=200,blank=True)
    Inventory_ID = models.CharField("Inventory ID",max_length=8, default="ABCD1234", unique=True)
    Inventory_followers = models.IntegerField("Inventory Followers",default=0,blank=True)

    def __str__(self):
        return strip_tags(f'{self.Inventory_name} - {self.Inventory_ID} ')

class SalesUser(models.Model):

    Sales_User = models.OneToOneField(User,on_delete=models.CASCADE, null=True)
    SalesUser_ID = models.CharField("Sales User ID",max_length=10, default="ABCDE12345", unique=True)
    SalesUser_Inventory = models.ForeignKey(Inventory,on_delete=models.DO_NOTHING, null=True)
    Invoice_GST_no = models.CharField("GST Number",max_length=20, default=' ', blank=True)
    # Invoice_GST_perc = models.IntegerField("Invoicne GST Percentage(eg: 10 for 10%)",default=18,blank=True)
    Sales_User_image = models.ImageField(upload_to='sales_user_images',default = 'sales_user_images/default_sales_user.png', height_field=None, width_field=None, max_length=100,blank=True)
    Inventory_access = models.BooleanField(default=False)
    SalesUser_Address = models.TextField("Address",blank=True)
    Sales_User_info = models.TextField("Information",blank=True)
    Sales_User_bnk_accnt_no =models.CharField("Bank Account Number",max_length=20,null=True, blank=True)
    Sales_User_bnk_code =models.CharField("Bank Code",max_length=500,null=True, blank=True)
    Sales_User_bnk_name =models.CharField("Bank Name",max_length=500,null=True, blank=True)
    Sales_User_Terms_condition = models.TextField("Terms and Condition",blank=True)
    Sales_User_include_bnkdetails = models.BooleanField(default=True)

    def __str__(self):
        return strip_tags(f'{self.Sales_User} - {self.SalesUser_ID} ')

class Product(models.Model):
    
    Product_inventory = models.ForeignKey(Inventory,on_delete=models.CASCADE, null=True)
    Product_description = models.TextField(blank=True)
    Product_image = models.ImageField(upload_to='product_images',default = 'product_images/default_product.png', height_field=None, width_field=None, max_length=100,blank=True)
    Product_name = models.CharField("Product Name",max_length=200,blank=False)
    Product_ID = models.CharField("Product ID",max_length=6, default="AB1000",blank=False)
    Product_mrp = models.IntegerField("Product MRP",default=0,blank=False)
    Product_sprice = models.IntegerField("Product Substitute Price",default=0,blank=True)
    Product_sprice_tag = models.CharField("Product Substitute Price tag (Make sure to have commong Product tag)",max_length=200,blank=True, default="Member")
    Product_gst_per = models.IntegerField("Product GST percentage:",default=0,blank=True)
    Product_stock = models.IntegerField("Product Stock",default=0,blank=True) # new
    def __str__(self):
        return strip_tags(f'{self.Product_name} - {self.Product_ID} ')

class Invoice(models.Model):

    Invoice_Title = models.CharField("Invoice Title/Name",max_length=200,blank=False)
    Invoice_ContactInfo = models.CharField("Invoice Contact Info",max_length=200,blank=True)
    Invoice_ID = models.CharField("Invoice ID",max_length=9, default=" ", blank=False) 
    Invoice_User = models.ForeignKey(SalesUser,on_delete=models.CASCADE, null=True)
    Invoice_Inventory = models.ForeignKey(Inventory,on_delete=models.DO_NOTHING, null=True)
    Invoice_Date = models.DateTimeField("Date of invoice",auto_now=False, auto_now_add=False, blank=True, null=True , default=datetime.now())
    Invoice_Total_Amount = models.DecimalField("Invoicne Total Amount",default=0,max_digits=20,blank=True,decimal_places=2)
    Invoice_SubTotal_Amount = models.DecimalField("Invoicne Sub Total Amount",default=0,max_digits=20,blank=True,decimal_places=2)
    Invoice_member_ID = models.CharField("Member ID",max_length=20, blank=True)
    Invoice_gst_number = models.CharField("Invoice GST Number",max_length=20, blank=True)
    Invoice_comments = models.TextField("Invoice Comments",blank=True)
    Invoice_status = models.BooleanField(default=True)
    Invoice_reference = models.CharField("Invoice Reference Number",max_length=500, blank=True)
    

    def __str__(self):
        return strip_tags(f'{self.Invoice_ID} - {self.Invoice_Date} ')

class InvoiceItem(models.Model):

    Item_Invoice = models.ForeignKey(Invoice,on_delete=models.CASCADE, null=True)
    # Item_p = models.ForeignKey(Product,on_delete=models.DO_NOTHING, null=True,blank=True)
    Member = models.BooleanField(default=False)
    Item_Quantity = models.IntegerField("Quantity",default=0,blank=True)
    Item_price = models.IntegerField("Price",default=0,blank=True)
    Item_ID = models.CharField("Item ID",max_length=6,blank=True)
    Item_name = models.CharField("Item Name",max_length=200,blank=True)
    Item_gst = models.IntegerField("Item GST",default=0,blank=True)
    Item_stock = models.IntegerField("After Stock",default=0,blank=True)
    

    def __str__(self):
        return strip_tags(f'{self.Item_ID} - {self.Item_Invoice} ')

class AccessRequest(models.Model):

    Requested_Inventory = models.ForeignKey(Inventory,on_delete=models.CASCADE, null=True)
    Request_from = models.ForeignKey(SalesUser,on_delete=models.CASCADE, null=True)
    Request_date = models.DateTimeField("Date of Request",auto_now=False, auto_now_add=False, blank=True, null=True , default=datetime.now())
    Request_ID = models.CharField("Request ID",max_length=20, blank=True)

    def __str__(self):
        return strip_tags(f'{self.Requested_Inventory} - {self.Request_from} ')


class ItemStock(models.Model):
    Item = models.ForeignKey(Product,on_delete=models.CASCADE, null=True)
    Item_Count = models.IntegerField("Quantity",default=0,blank=True)
    Stock_User = models.ForeignKey(SalesUser,on_delete=models.CASCADE, null=True)
    
    def __str__(self):
        return strip_tags(f'{self.Item} - {self.Stock_User} ')

class DefinedTags(models.Model):
    Tag_Title = models.CharField("Tag Title",max_length=20, blank=True)
    Tag_inventory = models.ForeignKey(Inventory,on_delete=models.CASCADE, null=True)
    Tag_description = models.TextField("Tag Description",blank=True)
    
    def __str__(self):
        return strip_tags(f'{self.Tag_Title} - {self.Tag_inventory} ')

class ProductTags(models.Model):
     
    Defined_Tags = models.ForeignKey(DefinedTags,on_delete=models.CASCADE, null=True)
    Tag_Item = models.ForeignKey(Product,on_delete=models.CASCADE, null=True)
    Tag_value = models.DecimalField("Tag Value",default=0,blank=True,max_digits = 13,decimal_places = 2)
    
    def __str__(self):
        return strip_tags(f'{self.Defined_Tags} - {self.Tag_Item} ')

class TagsTotal(models.Model):
     
    Defined_Tags = models.CharField("Tag Title",max_length=20, blank=True)
    Tag_Invoice = models.ForeignKey(Invoice,on_delete=models.CASCADE, null=True,blank=True)
    Tag_total = models.DecimalField("Tag Total",default=0,blank=True,max_digits = 13,decimal_places = 2)
    
    def __str__(self):
        return strip_tags(f'{self.Defined_Tags} - {self.Tag_Invoice} ')

class NewsUpdate(models.Model):
     
    Title = models.TextField("Title", blank=True)
    Breif = models.TextField("Brief", blank=True)
    Picture = models.ImageField(upload_to='New_image',default = 'New_image/default-news.png', height_field=None, width_field=None, max_length=100,blank=True)
    Link = models.URLField(max_length = 200)
    active = models.BooleanField(default=False)
    
    def __str__(self):
        return strip_tags(f'{self.Title} - {self.active} ')

# class PaymentMethod(models.Model):
     
#     Defined_method = models.CharField("Method Title",max_length=20, blank=True)
#     Method_user = models.ForeignKey(SalesUser,on_delete=models.CASCADE, null=True,blank=True)
#     Method_description = models.TextField("Method Description",blank=True)
    
#     def __str__(self):
#         return strip_tags(f'{self.Defined_Tags} - {self.Tag_Invoice} ')
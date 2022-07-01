# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from . models import Inventory,Product,SalesUser,Invoice,InvoiceItem,AccessRequest,ItemStock,DefinedTags,ProductTags,TagsTotal,NewsUpdate
from django.db import models

# Register your models here.

class InventoryAdmin(admin.ModelAdmin):
    fieldsets = [
		("Details",{"fields":["Inventory_user","Inventory_name","Inventory_ID","Inventory_followers"]}),
		]

class ProductAdmin(admin.ModelAdmin):
    fieldsets = [
		("Details",{"fields":["Product_inventory","Product_name","Product_ID","Product_stock","Product_mrp","Product_gst_per","Product_image","Product_description","Product_sprice","Product_sprice_tag"]}),
		]

class SalesUserAdmin(admin.ModelAdmin):
    fieldsets = [
		("Details",{"fields":["Sales_User","SalesUser_ID","SalesUser_Address","Sales_User_image","Invoice_GST_no","SalesUser_Inventory","Sales_User_info","Sales_User_bnk_accnt_no","Sales_User_bnk_name","Sales_User_bnk_code","Sales_User_include_bnkdetails","Sales_User_Terms_condition","Inventory_access"]}),
		]

class InvoiceAdmin(admin.ModelAdmin):
    fieldsets = [
		("Details",{"fields":["Invoice_Title","Invoice_ID","Invoice_gst_number","Invoice_member_ID","Invoice_User","Invoice_Inventory","Invoice_ContactInfo","Invoice_Date","Invoice_SubTotal_Amount","Invoice_Total_Amount","Invoice_status","Invoice_reference","Invoice_comments"]}),
		]

class InvoiceItenAdmin(admin.ModelAdmin):
    fieldsets = [
		("Details",{"fields":["Item_Invoice","Item_ID","Item_name","Item_gst","Item_price","Item_Quantity","Item_stock",'Member']}),
		]

class AccessRequestAdmin(admin.ModelAdmin):
    fieldsets = [
		("Details",{"fields":["Requested_Inventory","Request_from","Request_date",'Request_ID']}),
		]

class ItemStockAdmin(admin.ModelAdmin):
    fieldsets = [
		("Details",{"fields":["Item","Stock_User","Item_Count"]}),
		]

class DefinedTagsAdmin(admin.ModelAdmin):
    fieldsets = [
		("Details",{"fields":["Tag_Title","Tag_inventory"]}),
		]

class ProductTagsAdmin(admin.ModelAdmin):
    fieldsets = [
		("Details",{"fields":["Defined_Tags","Tag_Item","Tag_value"]}),
		]

class TagsTotalAdmin(admin.ModelAdmin):
    fieldsets = [
		("Details",{"fields":["Defined_Tags","Tag_Invoice","Tag_total"]}),
		]

class NewsUpdateAdmin(admin.ModelAdmin):
    fieldsets = [
		("Details",{"fields":["Title","Breif","Picture","Link","active"]}),
		]

admin.site.register(Inventory, InventoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(SalesUser, SalesUserAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(InvoiceItem, InvoiceItenAdmin)
admin.site.register(AccessRequest, AccessRequestAdmin)
admin.site.register(ItemStock, ItemStockAdmin)
admin.site.register(DefinedTags, DefinedTagsAdmin)
admin.site.register(ProductTags, ProductTagsAdmin)
admin.site.register(TagsTotal, TagsTotalAdmin)
admin.site.register(NewsUpdate, NewsUpdateAdmin)
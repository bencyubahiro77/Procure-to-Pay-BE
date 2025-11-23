from django.contrib import admin
from procure.models import PurchaseRequest, RequestItem, Approval, PurchaseOrder, ReceiptValidation

admin.site.register(PurchaseRequest)
admin.site.register(RequestItem)
admin.site.register(Approval)
admin.site.register(PurchaseOrder)
admin.site.register(ReceiptValidation)

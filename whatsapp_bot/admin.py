from django.contrib import admin
from whatsapp_bot.models import Friends,Transactions,Feedback

# Register your models here.

admin.site.register(Friends)
admin.site.register(Transactions)
admin.site.register(Feedback)
from django.contrib import admin

from models import Server


class ServerAdmin(admin.ModelAdmin):
    list_display = ("name", "active", "ip", "port", "available_reports")
    list_filter = ("name", "ip", "port", "active")
    ordering = ("name", "ip", "active")


admin.site.register(Server, ServerAdmin)

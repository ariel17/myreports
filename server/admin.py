from django.contrib import admin

from models import Server


class ServerAdmin(admin.TabularInline):
    list_display = ("name", "ip", "port", "username", "password", "active")
    list_filter = ("name", "ip", "port", "username", "password", "active")
    ordering = ("name", "ip", "active")


admin.site.register(Server, ServerAdmin)

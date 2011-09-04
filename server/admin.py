from django.contrib import admin

from models import Server, ReportByServer


class ServerAdmin(admin.ModelAdmin):
    list_display = ("name", "active", "ip", "port", "available_reports")
    list_filter = ("name", "ip", "port", "active")
    ordering = ("name", "ip", "active")

class ReportByServerAdmin(admin.ModelAdmin):
    list_display = ("server", "report",)


admin.site.register(Server, ServerAdmin)
admin.site.register(ReportByServer, ReportByServerAdmin)

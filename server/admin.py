#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: TODO
"""
__author__ = "Ariel Gerardo Ríos (ariel.gerardo.rios@gmail.com)"


from django.contrib import admin
from models import Server, ReportByServer


class ReportByServerInline(admin.TabularInline):
    model = ReportByServer


# class DatabaseInline(admin.TabularInline):
#     model = Database


class ServerAdmin(admin.ModelAdmin):
    list_display = ("name", "active", "ip", "port", "available_reports", \
            "url_launcher")
    list_filter = ("port", "active")
    ordering = ("name", "ip", "active")
    inlines = [ReportByServerInline, ]  # DatabaseInline, ]

    def url_launcher(self, object):
        url = object.url()
        return "<a href=\"%s\">%s</a>" % (url, url)
    url_launcher.allow_tags = True
    url_launcher.short_description = "URL"
    url_launcher.admin_order_field = "url"

    fieldsets = (
            ('Server properties', {'fields': (("name", "active"), ("ip",
                "port"), ("username", "password"))}),
            )


class ReportByServerAdmin(admin.ModelAdmin):
    list_display = ("assigned", "server_4_list", "report_4_list", "order")

    def assigned(self, object):
        if object.report:
            return "<a href=\"%s\">%s / %s</a>" % \
                    ("/admin/server/reportbyserver/%s/" % (object.id,), \
                    object.server, object.report)
        else:
            return 'N/A'
    assigned.allow_tags = True
    assigned.short_description = "Assigned"
    assigned.admin_order_field = 'server'

    def server_4_list(self, object):
        if object.report:
            return "<a href=\"%s\">%s</a>" % ("/admin/server/server/%s/" \
                % (object.server.id,), object.server,)
        else:
            return 'N/A'
    server_4_list.allow_tags = True
    server_4_list.short_description = "Server"
    server_4_list.admin_order_field = 'server'

    def report_4_list(self, object):
        if object.report:
            return "<a href=\"%s\">%s</a>" % ("/admin/server/report/%s/" \
                % (object.report.id,), object.report,)
        else:
            return 'N/A'
    report_4_list.allow_tags = True
    report_4_list.short_description = "Report"
    report_4_list.admin_order_field = 'report'

    fieldsets = (
            ('Asignation', {'fields': (('server', 'report'),)}),
            ('Properties', {'fields': ('order',)}),
            )


# class DatabaseAdmin(admin.ModelAdmin):
#     list_display = ("server", "name")
#     list_filter = ("server", "name")
#     ordering = ("server", "name")


admin.site.register(Server, ServerAdmin)
admin.site.register(ReportByServer, ReportByServerAdmin)
# admin.site.register(Database, DatabaseAdmin)

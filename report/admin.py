from django.conf import settings
from django.contrib import admin

from models import Report, Section, Variable, SectionByReport


class SectionByReportInline(admin.TabularInline):
    model = SectionByReport


class ReportAdmin(admin.ModelAdmin):
    list_display = ("title", "sections_involved",)
    list_filter = ("server", "sections",)
    ordering = ("title",)
    inlines = [SectionByReportInline, ]


class SectionAdmin(admin.ModelAdmin):
    list_display = ("title", "variables_involved",)
    list_filter = ("variables",)
    ordering = ("title",)


class VariableAdmin(admin.ModelAdmin):
    list_display = ("name", "description",)
    ordering = ("name",)


class SectionByReportAdmin(admin.ModelAdmin):
    list_display = ("report", "section", "order")


admin.site.register(Report, ReportAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Variable, VariableAdmin)
admin.site.register(SectionByReport, SectionByReportAdmin)

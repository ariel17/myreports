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
    list_display = ("assigned", "report_4_list", "section_4_list", "order")

    def assigned(self, object):
        if object.report:
            return "<a href=\"%s\">%s / %s</a>" % \
                    ("/admin/report/sectionbyreport/%s/" % (object.id,), \
                    object.report, object.section)
        else:
            return 'N/A'
    assigned.allow_tags = True
    assigned.short_description = "Assigned"
    assigned.admin_order_field = 'report'

    def report_4_list(self, object):
        if object.report:
            return "<a href=\"%s\">%s</a>" % ("/admin/report/report/%s/" \
                % (object.report.id,), object.report,)
        else:
            return 'N/A'
    report_4_list.allow_tags = True
    report_4_list.short_description = "Server"
    report_4_list.admin_order_field = 'server'

    def section_4_list(self, object):
        if object.report:
            return "<a href=\"%s\">%s</a>" % ("/admin/report/section/%s/" \
                % (object.section.id,), object.section,)
        else:
            return 'N/A'
    section_4_list.allow_tags = True
    section_4_list.short_description = "Server"
    section_4_list.admin_order_field = 'server'


admin.site.register(Report, ReportAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Variable, VariableAdmin)
admin.site.register(SectionByReport, SectionByReportAdmin)

from django.db import models

from server.models import Server
from report.models import Report


class ServerReport(object):
    server = models.ForeignKey(Server)
    reports = models.ManyToManyField(Report, help_text="Selected reports for "\
            "this server")

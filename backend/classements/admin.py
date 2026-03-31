from django.contrib import admin
from classements.models import Classement


class ClassementAdmin(admin.ModelAdmin):
    pass


admin.site.register(Classement, ClassementAdmin)

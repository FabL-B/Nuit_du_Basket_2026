from django.contrib import admin
from core.models import Edition


class EditionAdmin(admin.ModelAdmin):
    pass


admin.site.register(Edition, EditionAdmin)

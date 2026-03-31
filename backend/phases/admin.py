from django.contrib import admin
from phases.models import PhaseGlobale, SousPhase


class PhaseGlobaleAdmin(admin.ModelAdmin):
    pass


class SousPhaseAdmin(admin.ModelAdmin):
    pass


admin.site.register(PhaseGlobale, PhaseGlobaleAdmin)
admin.site.register(SousPhase, SousPhaseAdmin)

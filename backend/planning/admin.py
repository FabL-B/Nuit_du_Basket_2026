from django.contrib import admin
from planning.models import Terrain, Creneau, PausePlanning, PlanningSlot


class TerrainAdmin(admin.ModelAdmin):
    pass


class CreneauAdmin(admin.ModelAdmin):
    pass


class PausePlanningAdmin(admin.ModelAdmin):
    pass


class PlanningSlotAdmin(admin.ModelAdmin):
    pass


admin.site.register(Terrain, TerrainAdmin)
admin.site.register(Creneau, CreneauAdmin)
admin.site.register(PausePlanning, PausePlanningAdmin)
admin.site.register(PlanningSlot, PlanningSlotAdmin)

from wise.worksheet.models import Equation,Workspace,MathematicalObject,MathematicalTransform,MathematicalIdentity

from django.contrib import admin

class EquationInline(admin.StackedInline):
    model = Equation
    extra = 3
    inlines = [Equation]

class WorkspaceAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name']}),
#        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    inlines = [EquationInline]

admin.site.register(Workspace,WorkspaceAdmin)
admin.site.register(Equation)
admin.site.register(MathematicalObject)
admin.site.register(MathematicalTransform)
admin.site.register(MathematicalIdentity)

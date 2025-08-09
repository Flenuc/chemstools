from django.contrib import admin
from .models import MolecularStructure


@admin.register(MolecularStructure)
class MolecularStructureAdmin(admin.ModelAdmin):
    list_display = ['formula', 'created_at']
    list_filter = ['created_at']
    search_fields = ['formula']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('formula', 'created_at')
        }),
        ('Structure Data', {
            'fields': ('mol_data', 'lewis_data'),
            'classes': ('collapse',)
        })
    )
from django.contrib import admin
from .models import Aluno, Relatorio
from django.contrib.admin import DateFieldListFilter
from datetime import datetime
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class AlunoResource(resources.ModelResource):
    class Meta:
        model = Aluno

class UsuarioAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'nome', 'faculdade', 'curso', 'turno')
    search_fields = ('nome', 'faculdade', 'curso', 'turno' )
    filter = ('faculdade',)
    resource_class = AlunoResource

class RelatorioResource(resources.ModelResource):
    class Meta:
        model = Relatorio

class RelatorioAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('nome', 'curso', 'data', 'status')
    search_fields = ('nome', 'curso',)
    list_filter = (
        ('data', DateFieldListFilter),
    )
    resource_class = RelatorioResource

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        try:
            dt = datetime.strptime(search_term, "%d/%m/%Y")
            queryset |= self.model.objects.filter(data__date=dt.date())
            return queryset, use_distinct
        except:
            pass

        try:
            dt = datetime.strptime(search_term, "%d/%m")
            queryset |= self.model.objects.filter(
                data__day=dt.day,
                data__month=dt.month
            )
            return queryset, use_distinct
        except:
            pass


        try:
            dt = datetime.strptime(search_term, "%H:%M")
            queryset |= self.model.objects.filter(
                data__hour=dt.hour,
                data__minute=dt.minute
            )
            return queryset, use_distinct
        except:
            pass

        if search_term.isdigit() and 1 <= int(search_term) <= 31:
            queryset |= self.model.objects.filter(data__day=int(search_term))
            return queryset, use_distinct

        if search_term.isdigit() and 1 <= int(search_term) <= 12:
            queryset |= self.model.objects.filter(data__month=int(search_term))
            return queryset, use_distinct

        return queryset, use_distinct


admin.site.register(Aluno, UsuarioAdmin)
admin.site.register(Relatorio, RelatorioAdmin)

admin.site.site_header = "Painel de administração"

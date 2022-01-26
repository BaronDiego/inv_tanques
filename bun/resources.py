from import_export import resources
from .models import AforoTanque

class AforoTanqueResourse(resources.ModelResource):
    class Meta:
        model = AforoTanque


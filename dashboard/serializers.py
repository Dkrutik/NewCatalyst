from rest_framework import serializers
from .models import Industry,CompanyData

class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = '__all__'

class CompanyDataSerializer(serializers.ModelSerializer):
    index = serializers.SerializerMethodField()

    class Meta:
        model = CompanyData
        fields = ['index'] + [field.name for field in CompanyData._meta.fields]

    def get_index(self, obj):
        return self.context.get('index_map', {}).get(obj.id, -1)
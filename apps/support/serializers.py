from rest_framework import serializers
from .models import *


class BannersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banners
        fields = '__all__'


class EmailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Emails
        fields = '__all__'


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = link
        fields = '__all__'


class QQSerializer(serializers.ModelSerializer):
    class Meta:
        model = QQ
        fields = '__all__'


class SEOSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seo
        fields = '__all__'

from rest_framework import serializers
from .models import Article

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'

    def validate_publish_date(self, value):
        from datetime import date
        if value <= date.today():
            raise serializers.ValidationError("Publish date must be a future date.")
        return value

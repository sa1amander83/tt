from rest_framework import serializers
from .models import PromoCode

class PromoCodeSerializer(serializers.ModelSerializer):
    user_full_name = serializers.SerializerMethodField()
    is_currently_valid = serializers.SerializerMethodField()

    class Meta:
        model = PromoCode
        fields = [
            'id', 'code', 'description', 'discount_percent',
            'valid_from', 'valid_to', 'is_active', 'usage_limit',
            'used_count', 'user', 'user_full_name', 'is_currently_valid'
        ]

    def get_user_full_name(self, obj):
        return obj.user.get_full_name() if obj.user else None

    def get_is_currently_valid(self, obj):
        return obj.is_valid()

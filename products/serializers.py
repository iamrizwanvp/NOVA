# Product management serializers

# products/serializers.py
from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    # return basic owner info
    owner = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "title", "description", "category",
            "price", "image1", "image2", "image3", "image4", "image5",
            "owner", "created_at"
        ]
        read_only_fields = ["owner", "created_at"]

    def get_owner(self, obj):
        u = obj.owner
        if not u:
            return None
        # adapt depending on your User model fields
        return {"id": u.id, "email": getattr(u, "email", ""), "username": getattr(u, "username", "")}

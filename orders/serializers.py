from rest_framework import serializers


class SideDishSerializer(serializers.Serializer):
    side_dish_uuid = serializers.UUIDField()


class DishOrderSerializer(serializers.Serializer):
    dish_uuid = serializers.UUIDField()
    amount = serializers.FloatField()
    dish_note = serializers.CharField(required=False)
    side_dishes = serializers.ListField(child=SideDishSerializer())


class OrderSerializer(serializers.Serializer):
    ticket = serializers.IntegerField()
    dishes = serializers.ListField(child=DishOrderSerializer())
    general_note = serializers.CharField(required=False)

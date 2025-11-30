from django.db.models import Prefetch
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Dish, SideDishOption


class MenuViewSet(APIView):
    """
    Retorna todos os itens do cardápio sem paginação para prefetch no frontend.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        options_qs = SideDishOption.objects.select_related(
            "default_side_dish"
        ).prefetch_related("side_dishes")
        dishes_qs = Dish.objects.prefetch_related(
            Prefetch("side_dish_options", queryset=options_qs)
        )
        categories = Category.objects.prefetch_related(
            Prefetch("dish_set", queryset=dishes_qs)
        )

        menu = []
        for category in categories:
            items = [
                {
                    "uuid": dish.uuid,
                    "name": dish.name,
                    "description": dish.description,
                    "is_available": dish.is_available,
                    "price": dish.price,
                    "department": dish.department,
                    "side_dish_options": [
                        {
                            "uuid": option.uuid,
                            "side_dishes": [
                                {"uuid": sd.uuid, "name": sd.name}
                                for sd in option.side_dishes.all()
                            ],
                            "default_side_dish": (
                                {
                                    "uuid": option.default_side_dish.uuid,
                                    "name": option.default_side_dish.name,
                                }
                                if option.default_side_dish
                                else None
                            ),
                        }
                        for option in dish.side_dish_options.all()
                    ],
                }
                for dish in category.dish_set.all()
            ]
            menu.append(
                {
                    "category": {
                        "uuid": category.uuid,
                        "name": category.name,
                        "color": category.color,
                    },
                    "items": items,
                }
            )

        return Response({"menu": menu})

from django.db.models import Prefetch
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Category,
    CategoryTranslation,
    DEFAULT_LANGUAGE_CODE,
    Dish,
    DishTranslation,
    SideDishOption,
    SUPPORTED_LANGUAGE_CODES,
)


class MenuViewSet(APIView):
    """
    Retorna todos os itens do cardápio sem paginação para prefetch no frontend.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        public_only_param = request.query_params.get("public_only")
        filter_public_only = (
            isinstance(public_only_param, str)
            and public_only_param.lower() in {"1", "true", "t", "yes"}
        )

        language_code = request.query_params.get("lang") or DEFAULT_LANGUAGE_CODE
        if language_code not in SUPPORTED_LANGUAGE_CODES:
            language_code = DEFAULT_LANGUAGE_CODE

        def translated_attr(obj, attr):
            translations = getattr(obj, "requested_translations", None)
            if translations:
                translated_value = getattr(translations[0], attr, None)
                if translated_value is not None:
                    return translated_value
            return getattr(obj, attr)

        category_translations_prefetch = Prefetch(
            "translations",
            queryset=CategoryTranslation.objects.filter(language=language_code),
            to_attr="requested_translations",
        )
        dish_translations_prefetch = Prefetch(
            "translations",
            queryset=DishTranslation.objects.filter(language=language_code),
            to_attr="requested_translations",
        )

        options_qs = SideDishOption.objects.select_related(
            "default_side_dish"
        ).prefetch_related("side_dishes")
        dishes_qs = Dish.objects.prefetch_related(
            dish_translations_prefetch,
            Prefetch("side_dish_options", queryset=options_qs),
        )
        if filter_public_only:
            dishes_qs = dishes_qs.filter(show_on_public_menu=True)

        categories = Category.objects.prefetch_related(
            category_translations_prefetch,
            Prefetch("dish_set", queryset=dishes_qs),
        )

        menu = []
        for category in categories:
            items = [
                {
                    "uuid": dish.uuid,
                    "name": translated_attr(dish, "name"),
                    "description": translated_attr(dish, "description"),
                    "is_available": dish.is_available,
                    "show_on_public_menu": dish.show_on_public_menu,
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
            if filter_public_only and not items:
                continue
            menu.append(
                {
                    "category": {
                        "uuid": category.uuid,
                        "name": translated_attr(category, "name"),
                        "color": category.color,
                    },
                    "items": items,
                }
            )

        return Response({"menu": menu})

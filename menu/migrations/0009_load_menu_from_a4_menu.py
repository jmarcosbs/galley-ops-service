from decimal import Decimal

from django.db import migrations


CATEGORY_DATA = [
    {
        "name": "Entradas",
        "color": "F2C57C",
        "department": "kitchen",
        "items": [
            {
                "name": "Camarão à milanesa",
                "price": "132.00",
                "description": "",
                "ncm": "16052900",
            },
            {
                "name": "Camarão ao alho e óleo sem casca",
                "price": "145.00",
                "description": "",
                "ncm": "16052900",
            },
            {
                "name": "Lula à milanesa",
                "price": "86.00",
                "description": "",
                "ncm": "16055400",
            },
            {
                "name": "Torpedo de siri (2 unidades)",
                "price": "39.00",
                "description": "",
                "ncm": "16051000",
            },
            {
                "name": "Isca de frango",
                "price": "62.00",
                "description": "",
                "ncm": "16023220",
            },
            {
                "name": "Isca de peixe",
                "price": "78.00",
                "description": "",
                "ncm": "16041900",
            },
            {
                "name": "Peixe frito em postas",
                "price": "85.00",
                "description": "",
                "ncm": "16041900",
            },
            {
                "name": "Aipim frito",
                "price": "40.00",
                "description": "",
                "ncm": "20059900",
            },
            {
                "name": "Batata Frita",
                "price": "45.00",
                "description": "",
                "ncm": "20052000",
            },
        ],
    },
    {
        "name": "Camarao",
        "color": "F08A5D",
        "department": "kitchen",
        "items": [
            {
                "name": "Camarão Catupiry",
                "price": "217.00",
                "description": "Camarões refogados com manteiga, cebola, molho branco e Catupiry, cobertos com queijo muçarela e parmesão. Acompanhamentos: Arroz, fritas e salada.",
                "ncm": "16052900",
            },
            {
                "name": "Camarão à Grega",
                "price": "207.00",
                "description": "Camarão à milanesa gratinado com queijo muçarela e parmesão. Acompanhamentos: Arroz à grega, fritas e salada.",
                "ncm": "16052900",
            },
            {
                "name": "Camarão à milanesa",
                "price": "193.00",
                "description": "Camarão à milanesa tradicional. Acompanhamentos: Arroz, fritas e salada.",
                "ncm": "16052900",
            },
            {
                "name": "Camarão à Moda Marinheiro's",
                "price": "217.00",
                "description": "Camarões refogados com cebola, tomate, azeitonas e creme de leite, finalizados com salsinha fresca. Acompanhamentos: Arroz, fritas e salada.",
                "ncm": "16052900",
            },
            {
                "name": "Strogonoff de camarão",
                "price": "217.00",
                "description": "Camarões servidos em um molho especial de creme de leite e champignon, finalizados com salsinha fresca. Acompanhamentos: Arroz, fritas e salada.",
                "ncm": "16052900",
            },
            {
                "name": "Camarão à Praia Brava",
                "price": "239.00",
                "description": "Camarões refogados com arroz, queijo, ervilha, molho branco e Catupiry, finalizados com queijo muçarela, queijo parmesão e camarões à milanesa. Acompanhamentos: Fritas e salada.",
                "ncm": "16052900",
            },
        ],
    },
    {
        "name": "Lula",
        "color": "F7A9A8",
        "department": "kitchen",
        "items": [
            {
                "name": "Lula à milanesa",
                "price": "129.00",
                "description": "Lula à milanesa tradicional. Acompanhamentos: Arroz, fritas e salada.",
                "ncm": "16055400",
            },
        ],
    },
    {
        "name": "Salmao",
        "color": "FF928B",
        "department": "kitchen",
        "items": [
            {
                "name": "Salmão Grelhado",
                "price": "199.00",
                "description": "Filé de salmão grelhado na chapa. Acompanhamentos: Arroz, legumes salteados e pirão.",
                "ncm": "16041100",
            },
            {
                "name": "Salmão ao molho de alcaparras",
                "price": "219.00",
                "description": "Filé de salmão grelhado na chapa, servido com molho de alcaparras. Acompanhamentos: Arroz, batata sauté e pirão.",
                "ncm": "16041100",
            },
            {
                "name": "Salmão à Belle Meunière",
                "price": "238.00",
                "description": "Filé de salmão grelhado na chapa, servido com molho especial de alcaparras, champignon, camarão e shoyu. Acompanhamentos: Arroz, batata sauté e pirão.",
                "ncm": "16041100",
            },
            {
                "name": "Salmão ao molho de laranja",
                "price": "240.00",
                "description": "Filé de salmão grelhado na chapa, servido com molho especial de laranja, mel e cabernet branco. Finalizado com salsinha fresca. Acompanhamentos: Arroz, legumes salteados e salada.",
                "ncm": "16041100",
            },
        ],
    },
    {
        "name": "Cacarolas e Moquecas",
        "color": "D8A47F",
        "department": "kitchen",
        "items": [
            {
                "name": "Caçarola de frutos do mar",
                "price": "217.00",
                "description": "Frutos do mar ao molho de tomate, cebola, pimentões, azeite de dendê e leite de coco. Acompanhamentos: Arroz, fritas e salada.",
                "ncm": "16056900",
            },
            {
                "name": "Moqueca de peixes",
                "price": "214.00",
                "description": "Filé de peixe ao molho de tomate, cebola, pimentões, azeite de dendê e leite de coco. Acompanhamentos: Arroz, fritas e salada.",
                "ncm": "16041900",
            },
            {
                "name": "Moqueca de peixes com camarão",
                "price": "225.00",
                "description": "Filé de peixe e camarões ao molho de tomate, cebola, azeite de dendê e leite de coco. Acompanhamentos: Arroz, fritas e salada.",
                "ncm": "16042090",
            },
        ],
    },
    {
        "name": "Anchova",
        "color": "6DAEDB",
        "department": "kitchen",
        "items": [
            {
                "name": "Anchova grelhada",
                "price": "148.00",
                "description": "Anchova grelhada na chapa. Acompanhamentos: Arroz, batata sauté e pirão.",
                "ncm": "16041600",
            },
            {
                "name": "Anchova ao molho de alcaparras",
                "price": "168.00",
                "description": "Anchova grelhada na chapa, servida com molho de alcaparras. Acompanhamentos: Arroz, batata sauté e pirão.",
                "ncm": "16041600",
            },
            {
                "name": "Anchova à Belle Meunière",
                "price": "187.00",
                "description": "Anchova grelhada na chapa, servida com molho especial de alcaparras, champignon, camarão e shoyu. Acompanhamentos: Arroz, batata sauté e pirão.",
                "ncm": "16041600",
            },
        ],
    },
    {
        "name": "Linguado",
        "color": "9BC53D",
        "department": "kitchen",
        "items": [
            {
                "name": "Linguado grelhado",
                "price": "184.00",
                "description": "Filé de linguado grelhado na chapa. Acompanhamentos: Arroz, batata sauté e pirão.",
                "ncm": "16041900",
            },
            {
                "name": "Linguado ao molho de alcaparras",
                "price": "204.00",
                "description": "Filé de linguado grelhado na chapa, servido com molho de alcaparras. Acompanhamentos: Arroz, batata sauté e pirão.",
                "ncm": "16041900",
            },
            {
                "name": "Linguado à Belle Meunière",
                "price": "223.00",
                "description": "Filé de linguado grelhado na chapa, servido com molho especial de alcaparras, champignon, camarão e shoyu. Acompanhamentos: Arroz, batata sauté e pirão.",
                "ncm": "16041900",
            },
            {
                "name": "Linguado ao molho de camarão",
                "price": "213.00",
                "description": "Filé de linguado à milanesa, servido com molho de camarão, finalizado com salsinha fresca. Acompanhamentos: Arroz, fritas e salada.",
                "ncm": "16041900",
            },
            {
                "name": "Linguado à Moda Marinheiro's",
                "price": "253.00",
                "description": "Filé de linguado grelhado na chapa, servido com molho especial de cebola, tomate, azeitonas e creme de leite. Finalizado com salsinha fresca. Acompanhamentos: Arroz, fritas e salada.",
                "ncm": "16041900",
            },
        ],
    },
    {
        "name": "Congrio Rosa",
        "color": "6E7E85",
        "department": "kitchen",
        "items": [
            {
                "name": "Congrio Rosa grelhado",
                "price": "219.00",
                "description": "Filé de Congrio Rosa grelhado na chapa. Acompanhamentos: Arroz, batata sauté e pirão.",
                "ncm": "16041900",
            },
            {
                "name": "Congrio Rosa ao molho de alcaparras",
                "price": "239.00",
                "description": "Filé de Congrio Rosa grelhado na chapa, servido com molho de alcaparras. Acompanhamentos: Arroz, batata sauté e pirão.",
                "ncm": "16041900",
            },
            {
                "name": "Congrio Rosa à Belle Meunière",
                "price": "258.00",
                "description": "Filé de Congrio Rosa grelhado na chapa, servido com molho especial de alcaparras, champignon, camarão e shoyu. Acompanhamentos: Arroz, batata sauté e pirão.",
                "ncm": "16041900",
            },
            {
                "name": "Congrio Rosa ao molho de camarão",
                "price": "248.00",
                "description": "Filé de Congrio Rosa à milanesa, servido com molho de camarão e finalizado com salsinha fresca. Acompanhamentos: Arroz, fritas e salada.",
                "ncm": "16041900",
            },
            {
                "name": "Congrio Rosa à Moda Marinheiro's",
                "price": "269.00",
                "description": "Filé de Congrio Rosa grelhado na chapa, servido com molho especial de cebola, tomate, azeitonas e creme de leite. Finalizado com salsinha fresca. Acompanhamentos: Arroz, fritas e salada.",
                "ncm": "16041900",
            },
        ],
    },
    {
        "name": "File de peixe",
        "color": "A2D2FF",
        "department": "kitchen",
        "items": [
            {
                "name": "Peixe grelhado",
                "price": "129.00",
                "description": "Filé de peixe grelhado na chapa. Acompanhamentos: Arroz, batata sauté e pirão.",
                "ncm": "16041900",
            },
            {
                "name": "Peixe ao molho de alcaparras",
                "price": "149.00",
                "description": "Filé de peixe grelhado na chapa, servido com molho de alcaparras. Acompanhamentos: Arroz, batata sauté e pirão.",
                "ncm": "16041900",
            },
            {
                "name": "Peixe à milanesa",
                "price": "129.00",
                "description": "Filé de peixe à milanesa tradicional. Acompanhamentos: Arroz, fritas e salada.",
                "ncm": "16041900",
            },
            {
                "name": "Peixe ao molho de camarão",
                "price": "158.00",
                "description": "Filé de peixe à milanesa, servido com molho de camarão e finalizado com salsinha fresca. Acompanhamentos: Arroz, fritas e salada.",
                "ncm": "16041900",
            },
            {
                "name": "Peixe à Moda Marinheiro's",
                "price": "169.00",
                "description": "Filé de peixe grelhado na chapa, servido com um molho especial de cebola, tomate, azeitonas e creme de leite. Finalizado com salsinha fresca. Acompanhamentos: Arroz, fritas e salada.",
                "ncm": "16041900",
            },
        ],
    },
    {
        "name": "Carne",
        "color": "CB997E",
        "department": "kitchen",
        "items": [
            {
                "name": "Filé mignon grelhado",
                "price": "174.00",
                "description": "Filé mignon grelhado na chapa. Acompanhamentos: Arroz, fritas e salada.",
                "ncm": "16025000",
            },
            {
                "name": "Filé mignon ao molho Madeira",
                "price": "207.00",
                "description": "Filé mignon grelhado na chapa com molho madeira de cabernet tinto e champignon. Finalizado com salsinha fresca. Acompanhamentos: Arroz, legumes salteados e salada.",
                "ncm": "16025000",
            },
            {
                "name": "Filé mignon acebolado",
                "price": "181.00",
                "description": "Filé mignon grelhado na chapa com cebolas na manteiga e shoyu. Acompanhamentos: Arroz, fritas e salada.",
                "ncm": "16025000",
            },
            {
                "name": "Filé mignon à Parmegiana",
                "price": "199.00",
                "description": "Filé mignon à milanesa com molho de tomate, milho, ervilha, queijo muçarela e queijo parmesão. Acompanhamentos: Arroz, fritas e salada.",
                "ncm": "16025000",
            },
            {
                "name": "Strogonoff de carne",
                "price": "207.00",
                "description": "Cubos de filé mignon servidos em um molho especial de creme de leite e champignon. Acompanhamentos: Arroz, fritas e salada.",
                "ncm": "16025000",
            },
        ],
    },
    {
        "name": "Frango",
        "color": "FFE156",
        "department": "kitchen",
        "items": [
            {
                "name": "Frango grelhado",
                "price": "118.00",
                "description": "Filé de peito de frango grelhado na chapa. Acompanhamentos: Arroz, legumes salteados e salada.",
                "ncm": "16023220",
            },
            {
                "name": "Frango à milanesa",
                "price": "118.00",
                "description": "Filé de peito de frango à milanesa tradicional. Acompanhamentos: Arroz, fritas e salada.",
                "ncm": "16023220",
            },
            {
                "name": "Frango à Romana",
                "price": "141.00",
                "description": "Filé de peito de frango grelhado na chapa, ao molho branco com ervilhas, gratinado com queijo muçarela e parmesão. Acompanhamentos: Arroz, fritas e salada.",
                "ncm": "16023220",
            },
            {
                "name": "Frango à Parmegiana",
                "price": "142.00",
                "description": "Filé de peito de frango à milanesa, com molho de tomate, milho, ervilha, queijo muçarela e queijo parmesão. Acompanhamentos: Arroz, fritas e salada.",
                "ncm": "16023220",
            },
        ],
    },
    {
        "name": "Bebidas",
        "color": "3A86FF",
        "department": "bar",
        "items": [
            {
                "name": "Suco",
                "price": "13.00",
                "description": "Sabores: Abacaxi, Laranja, Acerola, Limão, Maracujá e Morango.",
                "ncm": "20099000",
            },
            {
                "name": "Refrigerante",
                "price": "8.00",
                "description": "Opções: Coca-Cola, Coca-Cola Zero, Guaraná, Guaraná Zero, Fanta Uva, Fanta Laranja, Sprite, Tônica e H2O.",
                "ncm": "22021000",
            },
            {
                "name": "Cerveja",
                "price": "22.00",
                "description": "600 ml: Original ou Heineken.",
                "ncm": "22030000",
            },
            {
                "name": "Caipirinha",
                "price": "29.00",
                "description": "Preparo clássico com vodka.",
                "ncm": "22089000",
            },
            {
                "name": "Long neck",
                "price": "15.00",
                "description": "Heineken ou Malzbier long neck.",
                "ncm": "22030000",
            },
            {
                "name": "Água",
                "price": "5.00",
                "description": "Água com gás ou sem gás.",
                "ncm": "22011000",
            },
        ],
    },
]


def _get_ncm(cache, model, code: str):
    normalized = (code or "").replace(" ", "").replace(".", "")
    if normalized in cache:
        return cache[normalized]
    try:
        cache[normalized] = model.objects.get(code=normalized)
    except model.DoesNotExist as exc:  # type: ignore[attr-defined]
        raise ValueError(f"NCM {code} não encontrado para carga do cardápio.") from exc
    return cache[normalized]


def load_menu_items(apps, schema_editor):
    Category = apps.get_model("menu", "Category")
    Dish = apps.get_model("menu", "Dish")
    NCM = apps.get_model("nfce", "NCM")

    ncm_cache: dict[str, object] = {}

    for category_data in CATEGORY_DATA:
        category, _ = Category.objects.update_or_create(
            name=category_data["name"],
            defaults={"color": category_data["color"]},
        )
        for item in category_data["items"]:
            ncm = _get_ncm(ncm_cache, NCM, item["ncm"])
            price = Decimal(item["price"])
            defaults = {
                "description": item["description"],
                "price": price,
                "ncm": ncm,
                "department": category_data["department"],
                "show_on_public_menu": True,
                "is_available": True,
            }
            Dish.objects.update_or_create(
                category=category,
                name=item["name"],
                defaults=defaults,
            )


def remove_menu_items(apps, schema_editor):
    Category = apps.get_model("menu", "Category")
    Dish = apps.get_model("menu", "Dish")

    for category_data in CATEGORY_DATA:
        try:
            category = Category.objects.get(name=category_data["name"])
        except Category.DoesNotExist:
            continue
        for item in category_data["items"]:
            Dish.objects.filter(category=category, name=item["name"]).delete()
        if not category.dish_set.exists():
            category.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("menu", "0008_categorytranslation_dishtranslation"),
        ("nfce", "0002_load_ncm_data"),
    ]

    operations = [
        migrations.RunPython(load_menu_items, reverse_code=remove_menu_items),
    ]

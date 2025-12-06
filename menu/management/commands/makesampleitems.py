import json
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from random import Random
from typing import Any, cast
from contextlib import AbstractContextManager

from django.core.management.base import BaseCommand
from django.db import transaction

from menu.models import Category, DepartmentChoices, Dish, SideDish, SideDishOption
from nfce.models import NCM


class Command(BaseCommand):
    help = "Carrega itens de exemplo no cardápio a partir de um JSON embutido."

    SAMPLE_JSON = r"""
{
  "menu": [
    {
      "category": "🍲 Entradas",
      "departiment": "cozinha",
      "options": [],
      "color": "#BEADFA",
      "items": [
        { "id": 1, "departiment": "cozinha", "name": "Camarao a Milanesa AP" },
        { "id": 2, "departiment": "cozinha", "name": "Camarao ao Alho e Oleo" },
        { "id": 3, "departiment": "cozinha", "name": "Lula a Milanesa AP" },
        { "id": 4, "departiment": "cozinha", "name": "Torpedo de Siri" },
        { "id": 5, "departiment": "cozinha", "name": "Isca de Frango" },
        { "id": 6, "departiment": "cozinha", "name": "Isca de Peixe" },
        { "id": 7, "departiment": "cozinha", "name": "Peixe em postas" },
        { "id": 8, "departiment": "cozinha", "name": "Aipim Frito" },
        { "id": 9, "departiment": "cozinha", "name": "Batata Frita" }
      ]
    },
    {
      "category": "🍤 Camaroes",
      "departiment": "cozinha",
      "options": [
        ["Fritas", "Souté", "Legumes"],
        ["Salada", "Pirão"]
      ],
      "color": "#F9B572",
      "items": [
        {
          "id": 10,
          "departiment": "cozinha",
          "name": "Camarao Catupiry",
          "description": "Camarao refogado com cebola, manteiga, molho branco e catupiry. Acompanhamentos: Arroz, fritas e salada."
        },
        {
          "id": 11,
          "departiment": "cozinha",
          "name": "Camarao a Grega",
          "description": "Camarao a milanesa gratinado com queijo. Acompanhamentos: Arroz a grega, fritas e salada."
        },
        {
          "id": 12,
          "departiment": "cozinha",
          "name": "Camarao a Milanesa Comp.",
          "description": "Camarao a milanesa tradicional. Acompanhamentos: Arroz, fritas e salada."
        },
        {
          "id": 13,
          "departiment": "cozinha",
          "name": "Camarao a Moda",
          "description": "Camarao refogado com cebola, tomate, salsinha, azeitonas e creme de leite. Acompanhamentos: Arroz, fritas e salada."
        },
        {
          "id": 14,
          "departiment": "cozinha",
          "name": "Strogonoff de Camarao",
          "description": "Camarao servido em molho de creme de leite. Acompanhamentos: Arroz, fritas e salada."
        },
        {
          "id": 15,
          "departiment": "cozinha",
          "name": "Camarão Praia Brava",
          "description": "Sem descrição"
        }
      ]
    },
    {
      "category": "🍥 Lulas",
      "departiment": "cozinha",
      "options": [
        ["Fritas", "Souté", "Legumes"],
        ["Salada", "Pirão"]
      ],
      "color": "#E6A4B4",
      "items": [
        {
          "id": 21,
          "departiment": "cozinha",
          "name": "Lula a Milanesa Comp.",
          "description": "Lula a milanesa tradicional. Acompanhamentos: Arroz, fritas e salada."
        }
      ]
    },
    {
      "category": "🍵 Moquecas",
      "departiment": "cozinha",
      "options": [
        ["Fritas", "Souté", "Legumes"],
        ["Salada", "Pirão"]
      ],
      "color": "#B0A695",
      "items": [
        {
          "id": 31,
          "departiment": "cozinha",
          "name": "Cacarola F. Mar",
          "description": "Frutos do mar ao molho de tomate com cebola, azeite de dende e leite de coco. Acompanhamentos: Arroz, fritas e pirão."
        },
        {
          "id": 32,
          "departiment": "cozinha",
          "name": "Moqueca de Peixes",
          "description": "Peixe em posta com molho de tomate, leite de coco, azeite de dende e cebola. Acompanhamentos: Arroz, fritas e pirão."
        },
        {
          "id": 33,
          "departiment": "cozinha",
          "name": "Moqueca de Peixes com Camarao",
          "description": "Peixe em posta com camarao em molho de tomate, leite de coco, azeite de dende e cebola. Acompanhamentos: Arroz, fritas e pirão."
        }
      ]
    },
    {
      "category": "🐟 Anchovas",
      "departiment": "cozinha",
      "options": [
        ["Fritas", "Souté", "Legumes"],
        ["Salada", "Pirão"]
      ],
      "color": "#007fff",
      "items": [
        {
          "id": 41,
          "departiment": "cozinha",
          "name": "Anchova Grelhada",
          "description": "Anchova grelhada na chapa. Acompanhamentos: Arroz, batata sauté e pirão."
        },
        {
          "id": 42,
          "departiment": "cozinha",
          "name": "Anchova em Posta Comp.",
          "description": "Anchova grelhada na chapa. Acompanhamentos: Arroz, batata sauté e pirão."
        },
        {
          "id": 43,
          "departiment": "cozinha",
          "name": "Anchova Alcaparras",
          "description": "Anchova grelhada na chapa ao molho de alcaparras. Acompanhamentos: Arroz, batata sauté e pirão."
        },
        {
          "id": 44,
          "departiment": "cozinha",
          "name": "Anchova Belle Meuniere",
          "description": "Anchova grelhada com alcaparras, champignon e camarão. Acompanhamentos: Arroz, batata sauté e pirão."
        }
      ]
    },
    {
      "category": "🐟 Salmoes",
      "departiment": "cozinha",
      "options": [
        ["Fritas", "Souté", "Legumes"],
        ["Salada", "Pirão"]
      ],
      "color": "#007fff",
      "items": [
        {
          "id": 51,
          "departiment": "cozinha",
          "name": "Salmao Grelhado",
          "description": "File de Salmao grelhado na chapa. Acompanhamentos: Arroz, batata sauté e pirão."
        },
        {
          "id": 52,
          "departiment": "cozinha",
          "name": "Salmao Alcaparras",
          "description": "File de Salmao grelhado na chapa ao molho de alcaparras. Acompanhamentos: Arroz, batata sauté e pirão."
        },
        {
          "id": 53,
          "departiment": "cozinha",
          "name": "Salmao Belle Meunière",
          "description": "Salmao grelhado com alcaparras, champignon e camarão. Acompanhamentos: Arroz, batata sauté e pirão."
        },
        {
          "id": 54,
          "departiment": "cozinha",
          "name": "Salmao Molho de Laranja",
          "description": "Salmao grelhado com alcaparras, champignon e camarão. Acompanhamentos: Arroz, batata sauté e pirão."
        }
      ]
    },
    {
      "category": "🐟 Congrio Rosa",
      "departiment": "cozinha",
      "options": [
        ["Fritas", "Souté", "Legumes"],
        ["Salada", "Pirão"]
      ],
      "color": "#007fff",
      "items": [
        {
          "id": 61,
          "departiment": "cozinha",
          "name": "Congrio Grelhado",
          "description": "File de Congrio grelhado na chapa. Acompanhamentos: Arroz, batata sauté e pirão."
        },
        {
          "id": 62,
          "departiment": "cozinha",
          "name": "Congrio Alcaparras",
          "description": "File de Congrio grelhado ao molho de alcaparras. Acompanhamentos: Arroz, batata sauté e pirão."
        },
        {
          "id": 63,
          "departiment": "cozinha",
          "name": "Congrio Belle Meunière",
          "description": "Congrio grelhado com alcaparras, champignon e camarão. Acompanhamentos: Arroz, batata sauté e pirão."
        },
        {
          "id": 64,
          "departiment": "cozinha",
          "name": "Congrio Molho de Camarao",
          "description": "Congrio a milanesa com molho de camarao. Acompanhamentos: Arroz, fritas e salada."
        },
        {
          "id": 65,
          "departiment": "cozinha",
          "name": "Congrio à Moda",
          "description": "Congrio com molho de cebola, tomate, salsinha, azeitonas e creme de leite. Acompanhamentos: Arroz, fritas e salada."
        }
      ]
    },
    {
      "category": "🐟 Linguado",
      "departiment": "cozinha",
      "options": [
        ["Fritas", "Souté", "Legumes"],
        ["Salada", "Pirão"]
      ],
      "color": "#007fff",
      "items": [
        {
          "id": 71,
          "departiment": "cozinha",
          "name": "Linguado Grelhado",
          "description": "File de Linguado grelhado na chapa. Acompanhamentos: Arroz, batata sauté e pirão."
        },
        {
          "id": 72,
          "departiment": "cozinha",
          "name": "Linguado Alcaparras",
          "description": "File de Linguado grelhado ao molho de alcaparras. Acompanhamentos: Arroz, batata sauté e pirão."
        },
        {
          "id": 73,
          "departiment": "cozinha",
          "name": "Linguado Belle Meunière",
          "description": "Linguado grelhado com alcaparras, champignon e camarão. Acompanhamentos: Arroz, batata sauté e pirão."
        },
        {
          "id": 74,
          "departiment": "cozinha",
          "name": "Linguado Molho de Camarao",
          "description": "Linguado a milanesa com molho de camarao. Acompanhamentos: Arroz, fritas e salada."
        },
        {
          "id": 75,
          "departiment": "cozinha",
          "name": "Linguado à Moda",
          "description": "Congrio com molho de cebola, tomate, salsinha, azeitonas e creme de leite. Acompanhamentos: Arroz, fritas e salada."
        }
      ]
    },
    {
      "category": "🐟 File de Peixe",
      "departiment": "cozinha",
      "options": [
        ["Fritas", "Souté", "Legumes"],
        ["Salada", "Pirão"]
      ],
      "color": "#007fff",
      "items": [
        {
          "id": 81,
          "departiment": "cozinha",
          "name": "Peixe Grelhado",
          "description": "File de Peixe grelhado na chapa. Acompanhamentos: Arroz, batata sauté e pirão."
        },
        {
          "id": 82,
          "departiment": "cozinha",
          "name": "Peixe Alcaparras",
          "description": "File de Peixe grelhado ao molho de alcaparras. Acompanhamentos: Arroz, batata sauté e pirão."
        },
        {
          "id": 83,
          "departiment": "cozinha",
          "name": "Peixe Milanesa",
          "description": "Peixe grelhado com alcaparras, champignon e camarão. Acompanhamentos: Arroz, batata sauté e pirão."
        },
        {
          "id": 84,
          "departiment": "cozinha",
          "name": "Peixe Molho de Camarao",
          "description": "Peixe a milanesa com molho de camarao. Acompanhamentos: Arroz, fritas e salada."
        },
        {
          "id": 85,
          "departiment": "cozinha",
          "name": "Peixe à Moda",
          "description": "Peixe com molho de cebola, tomate, salsinha, azeitonas e creme de leite. Acompanhamentos: Arroz, fritas e salada."
        }
      ]
    },
    {
      "category": "🍖 Carnes",
      "departiment": "cozinha",
      "options": [
        ["Fritas", "Souté", "Legumes"],
        ["Salada", "Pirão"]
      ],
      "color": "#C96868",
      "items": [
        {
          "id": 91,
          "departiment": "cozinha",
          "name": "File Grelhado",
          "description": "File Mignon grelhado na chapa. Acompanhamentos: Arroz, fritas e salada."
        },
        {
          "id": 92,
          "departiment": "cozinha",
          "name": "File Molho Madeira",
          "description": "File Mignon a milanesa. Acompanhamentos: Arroz, fritas e salada."
        },
        {
          "id": 93,
          "departiment": "cozinha",
          "name": "File Acebolado",
          "description": "File Mignon a milanesa. Acompanhamentos: Arroz, fritas e salada."
        },
        {
          "id": 94,
          "departiment": "cozinha",
          "name": "File à Parmegiana",
          "description": "File Mignon a milanesa com molho de tomate e queijo gratinado. Acompanhamentos: Arroz, fritas e salada."
        },
        {
          "id": 95,
          "departiment": "cozinha",
          "name": "Strogonoff de Carne",
          "description": "File Mignon a milanesa com molho de tomate e queijo gratinado. Acompanhamentos: Arroz, fritas e salada."
        }
      ]
    },
    {
      "category": "🐔 Frango",
      "departiment": "cozinha",
      "options": [
        ["Fritas", "Souté", "Legumes"],
        ["Salada", "Pirão"]
      ],
      "color": "#FFB26F",
      "items": [
        {
          "id": 101,
          "departiment": "cozinha",
          "name": "Frango Grelhado",
          "description": "Frango Mignon grelhado na chapa. Acompanhamentos: Arroz, fritas e salada."
        },
        {
          "id": 102,
          "departiment": "cozinha",
          "name": "Frango Milanesa",
          "description": "Frango Mignon a milanesa. Acompanhamentos: Arroz, fritas e salada."
        },
        {
          "id": 103,
          "departiment": "cozinha",
          "name": "Frango a Romana",
          "description": "Frango Mignon a milanesa. Acompanhamentos: Arroz, fritas e salada."
        },
        {
          "id": 104,
          "departiment": "cozinha",
          "name": "Frango à Parmegiana",
          "description": "Frango Mignon a milanesa com molho de tomate e queijo gratinado. Acompanhamentos: Arroz, fritas e salada."
        }
      ]
    },
    {
      "category": "🥃 Sucos",
      "departiment": "copa",
      "options": [
        ["Sem açucar", "Pouco açucar", "Bem docinho"],
        ["Pouco gelo", "Sem gelo"]
      ],
      "color": "#8E7AB5",
      "items": [
        {
          "id": 110,
          "departiment": "copa",
          "name": "Abacaxi",
          "description": ""
        },
        {
          "id": 111,
          "departiment": "copa",
          "name": "Acerola",
          "description": ""
        },
        {
          "id": 112,
          "departiment": "copa",
          "name": "Laranja",
          "description": ""
        },
        {
          "id": 113,
          "departiment": "copa",
          "name": "Limao",
          "description": ""
        },
        {
          "id": 114,
          "departiment": "copa",
          "name": "Maracuja",
          "description": ""
        },
        {
          "id": 115,
          "departiment": "copa",
          "name": "Morango",
          "description": ""
        }
      ]
    },
    {
      "category": "🥤 Refrigerantes",
      "departiment": "copa",
      "options": [
        ["Só gelo", "Gelo e limão", "Gelo e laranja"]
      ],
      "color": "#bf2c2a",
      "items": [
        {
          "id": 120,
          "departiment": "copa",
          "name": "Coca",
          "description": ""
        },
        {
          "id": 121,
          "departiment": "copa",
          "name": "Coca Zero",
          "description": ""
        },
        {
          "id": 122,
          "departiment": "copa",
          "name": "Guaraná",
          "description": ""
        },
        {
          "id": 123,
          "departiment": "copa",
          "name": "Guaraná Zero",
          "description": ""
        },
        {
          "id": 124,
          "departiment": "copa",
          "name": "Fanta Uva",
          "description": ""
        },
        {
          "id": 125,
          "departiment": "copa",
          "name": "Fanta Laranja",
          "description": ""
        },
        {
          "id": 126,
          "departiment": "copa",
          "name": "Sprite",
          "description": ""
        },
        {
          "id": 127,
          "departiment": "copa",
          "name": "Tônica",
          "description": ""
        },
        {
          "id": 128,
          "departiment": "copa",
          "name": "H2O",
          "description": ""
        }
      ]
    },
    {
      "category": "💧 Água",
      "departiment": "copa",
      "options": [
        ["Só gelo", "Gelo e limão"]
      ],
      "color": "#48d1cc",
      "items": [
        {
          "id": 131,
          "departiment": "copa",
          "name": "Água com Gás",
          "description": ""
        },
        {
          "id": 132,
          "departiment": "copa",
          "name": "Água sem Gás",
          "description": ""
        }
      ]
    },
    {
      "category": "🍺 Cervejas",
      "departiment": "copa",
      "options": [
        ["1 copo", "2 copos", "3 copos", "4 copos", "5 copos", "6 copos"]
      ],
      "color": "#F6F193",
      "items": [
        {
          "id": 140,
          "departiment": "copa",
          "name": "Original",
          "description": ""
        },
        {
          "id": 141,
          "departiment": "copa",
          "name": "Heineken",
          "description": ""
        },
        {
          "id": 142,
          "departiment": "copa",
          "name": "Serra Malte",
          "description": ""
        }
      ]
    },
    {
      "category": "🍻 Longneck",
      "departiment": "copa",
      "options": [
        ["1 copo", "2 copos", "3 copos", "4 copos", "5 copos", "6 copos"]
      ],
      "color": "#F6F193",
      "items": [
        {
          "id": 150,
          "departiment": "copa",
          "name": "Longneck Heineken",
          "description": ""
        },
        {
          "id": 151,
          "departiment": "copa",
          "name": "Longneck Malzbier",
          "description": ""
        },
        {
          "id": 172,
          "departiment": "copa",
          "name": "Longneck Zero",
          "description": ""
        }
      ]
    },
    {
      "category": "🍹 Caipirinhas",
      "departiment": "copa",
      "options": [
        ["🍓 Morango", "🟠 Maracujá", "🍍 Abacaxi", "🍅 Acerola", "Mista"],
        ["Sem açucar", "Pouco açucar", "Bem docinho"],
        ["Pouco gelo", "Sem gelo"]
      ],
      "color": "#64b514",
      "items": [
        {
          "id": 160,
          "departiment": "copa",
          "name": "Caipirinha Vodka",
          "description": ""
        },
        {
          "id": 161,
          "departiment": "copa",
          "name": "Caipirinha Cachaça",
          "description": ""
        },
        {
          "id": 162,
          "departiment": "copa",
          "name": "Caipirinha Steinhaeger",
          "description": ""
        },
        {
          "id": 163,
          "departiment": "copa",
          "name": "Caipirinha Absolut",
          "description": ""
        }
      ]
    },
    {
      "category": "🍦 Picolés",
      "departiment": "copa",
      "options": [],
      "color": "#d7bab4",
      "items": [
        {
          "id": 171,
          "departiment": "copa",
          "name": "Picolé Ypy",
          "description": ""
        }
      ]
    },
    {
      "category": "#️⃣ Acompanhamentos",
      "departiment": "cozinha",
      "options": [],
      "color": "#f400a1",
      "items": [
        {
          "id": 173,
          "departiment": "cozinha",
          "name": "Arroz",
          "description": ""
        },
        {
          "id": 174,
          "departiment": "cozinha",
          "name": "Pirão",
          "description": ""
        },
        {
          "id": 175,
          "departiment": "cozinha",
          "name": "Salada",
          "description": ""
        },
        {
          "id": 176,
          "departiment": "cozinha",
          "name": "Legumes",
          "description": ""
        },
        {
          "id": 177,
          "departiment": "cozinha",
          "name": "Soute",
          "description": ""
        }
      ]
    }
  ]
}
    """

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--price",
            type=float,
            default=None,
            help=(
                "Preço fixo para os itens criados. Se omitido, gera preços "
                "aleatórios por item."
            ),
        )
        parser.add_argument(
            "--ncm",
            type=str,
            default="00000000",
            help="Código NCM a ser usado/criado para os itens de exemplo.",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=42,
            help="Seed para gerar preços aleatórios reprodutíveis.",
        )

    @staticmethod
    def _clean_color(raw: str) -> str:
        return (raw or "").replace("#", "")[:6]

    @staticmethod
    def _map_department(raw: str | None) -> str:
        mapping = {
            "cozinha": DepartmentChoices.KITCHEN,
            "copa": DepartmentChoices.BAR,
        }
        return mapping.get((raw or "").lower(), DepartmentChoices.KITCHEN)

    @staticmethod
    def _quantize_price(value: float | Decimal) -> Decimal:
        return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _price_bounds(
        self, department: str, category_name: str
    ) -> tuple[Decimal, Decimal]:
        normalized_category = (category_name or "").lower()

        if "acompanh" in normalized_category:
            return Decimal("8.00"), Decimal("32.00")

        if department == DepartmentChoices.KITCHEN:
            return Decimal("45.00"), Decimal("210.00")

        return Decimal("5.00"), Decimal("45.00")

    def _generate_item_price(
        self,
        base_seed: int,
        item_id: int,
        department: str,
        category_name: str,
    ) -> Decimal:
        min_price, max_price = self._price_bounds(department, category_name)
        rng = Random(base_seed + item_id)
        raw_price = rng.uniform(float(min_price), float(max_price))
        return self._quantize_price(raw_price)

    def _get_or_create_ncm(self, code: str) -> NCM:
        normalized = code.replace(" ", "").replace(".", "")
        ncm, _ = NCM.objects.get_or_create(
            code=normalized,
            defaults={
                "description": "NCM de exemplo",
                "national_tax": 0,
                "import_tax": 0,
                "state_tax": 0,
                "municipal_tax": 0,
                "vigency_start": date(2000, 1, 1),
                "vigency_end": date(2099, 12, 31),
            },
        )
        return ncm

    def handle(self, *args: Any, **options: Any) -> None:
        payload = json.loads(self.SAMPLE_JSON)
        fixed_price = options["price"]
        ncm_code = options["ncm"]
        price_seed = options["seed"]

        fixed_price_decimal = (
            self._quantize_price(fixed_price) if fixed_price is not None else None
        )

        ncm = self._get_or_create_ncm(ncm_code)

        side_dish_cache: dict[str, SideDish] = {}
        option_cache: dict[tuple[str, ...], SideDishOption] = {}

        created_dishes = 0
        updated_dishes = 0
        created_categories = 0
        created_options = 0
        trimmed_groups = 0

        with cast(AbstractContextManager, transaction.atomic()):
            for category_data in payload.get("menu", []):
                cat_name = category_data["category"]
                color = self._clean_color(category_data.get("color", ""))
                category, cat_created = Category.objects.get_or_create(
                    name=cat_name, defaults={"color": color}
                )
                if cat_created:
                    created_categories += 1
                elif category.color != color and color:
                    category.color = color
                    category.save(update_fields=["color", "updated_at"])

                raw_options: list[list[str]] = category_data.get("options", [])
                category_options: list[SideDishOption] = []
                for group in raw_options:
                    if not group:
                        continue
                    names = [name.strip() for name in group if name.strip()]
                    if not names:
                        continue
                    trimmed = names[:3]
                    if len(names) > 3:
                        trimmed_groups += 1
                    side_dishes = []
                    for name in trimmed:
                        if name not in side_dish_cache:
                            side_dish_cache[name], _ = SideDish.objects.get_or_create(
                                name=name
                            )
                        side_dishes.append(side_dish_cache[name])
                    if not side_dishes:
                        continue
                    key = tuple(sorted(sd.name for sd in side_dishes))
                    option = option_cache.get(key)
                    if not option:
                        option = SideDishOption.objects.create(
                            default_side_dish=side_dishes[0]
                        )
                        option.side_dishes.set(side_dishes)
                        option_cache[key] = option
                        created_options += 1
                    category_options.append(option)

                for item in category_data.get("items", []):
                    dept = self._map_department(item.get("departiment"))
                    dish_name = item["name"]
                    description = item.get("description") or ""
                    item_price = (
                        fixed_price_decimal
                        if fixed_price_decimal is not None
                        else self._generate_item_price(
                            price_seed, item["id"], dept, cat_name
                        )
                    )
                    dish, dish_created = Dish.objects.get_or_create(
                        name=dish_name,
                        defaults={
                            "description": description,
                            "ncm": ncm,
                            "category": category,
                            "department": dept,
                            "price": item_price,
                            "is_available": True,
                        },
                    )
                    if dish_created:
                        created_dishes += 1
                    else:
                        dish.description = description
                        dish.category = category
                        dish.department = dept
                        if dish.price != item_price:
                            dish.price = item_price
                        if not dish.is_available:
                            dish.is_available = True
                        dish.save(
                            update_fields=[
                                "description",
                                "category",
                                "department",
                                "price",
                                "is_available",
                                "updated_at",
                            ]
                        )
                        updated_dishes += 1

                    if category_options:
                        dish.side_dish_options.set(category_options)
                    else:
                        dish.side_dish_options.clear()

        self.stdout.write(
            self.style.SUCCESS(
                f"Categorias criadas: {created_categories} | Opções criadas: {created_options} | "
                f"Dishes criados: {created_dishes} | atualizados: {updated_dishes} | "
                f"Grupos de opções podados (>3): {trimmed_groups}"
            )
        )

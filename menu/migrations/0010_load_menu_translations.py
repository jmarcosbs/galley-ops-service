from django.db import migrations


CATEGORY_TRANSLATIONS = {
    "Entradas": {"en-US": "Starters", "es-ES": "Entradas"},
    "Camarao": {"en-US": "Shrimp", "es-ES": "Camarones"},
    "Lula": {"en-US": "Squid", "es-ES": "Calamares"},
    "Salmao": {"en-US": "Salmon", "es-ES": "Salmón"},
    "Cacarolas e Moquecas": {
        "en-US": "Casseroles & Moquecas",
        "es-ES": "Cazuelas y Moquecas",
    },
    "Anchova": {"en-US": "Anchova", "es-ES": "Anchova"},
    "Linguado": {"en-US": "Flounder", "es-ES": "Linguado"},
    "Congrio Rosa": {"en-US": "Congrio Rosa", "es-ES": "Congrio Rosa"},
    "File de peixe": {"en-US": "Fish Fillet", "es-ES": "Filete de pescado"},
    "Carne": {"en-US": "Beef", "es-ES": "Carnes"},
    "Frango": {"en-US": "Chicken", "es-ES": "Pollo"},
    "Bebidas": {"en-US": "Beverages", "es-ES": "Bebidas"},
}


DISH_TRANSLATIONS = [
    {
        "category": "Entradas",
        "dish": "Camarão à milanesa",
        "translations": {
            "en-US": {"name": "Breaded Shrimp", "description": ""},
            "es-ES": {"name": "Camarones empanizados", "description": ""},
        },
    },
    {
        "category": "Entradas",
        "dish": "Camarão ao alho e óleo sem casca",
        "translations": {
            "en-US": {
                "name": "Garlic Butter Shrimp (peeled)",
                "description": "",
            },
            "es-ES": {
                "name": "Camarones al ajo y aceite sin cáscara",
                "description": "",
            },
        },
    },
    {
        "category": "Entradas",
        "dish": "Lula à milanesa",
        "translations": {
            "en-US": {"name": "Breaded Squid", "description": ""},
            "es-ES": {"name": "Calamares empanizados", "description": ""},
        },
    },
    {
        "category": "Entradas",
        "dish": "Torpedo de siri (2 unidades)",
        "translations": {
            "en-US": {"name": "Crab torpedo (2 pcs)", "description": ""},
            "es-ES": {"name": "Torpedo de cangrejo (2 uds.)", "description": ""},
        },
    },
    {
        "category": "Entradas",
        "dish": "Isca de frango",
        "translations": {
            "en-US": {"name": "Chicken bites", "description": ""},
            "es-ES": {"name": "Bocados de pollo", "description": ""},
        },
    },
    {
        "category": "Entradas",
        "dish": "Isca de peixe",
        "translations": {
            "en-US": {"name": "Fish bites", "description": ""},
            "es-ES": {"name": "Bocados de pescado", "description": ""},
        },
    },
    {
        "category": "Entradas",
        "dish": "Peixe frito em postas",
        "translations": {
            "en-US": {"name": "Fried fish steaks", "description": ""},
            "es-ES": {"name": "Pescado frito en postas", "description": ""},
        },
    },
    {
        "category": "Entradas",
        "dish": "Aipim frito",
        "translations": {
            "en-US": {"name": "Fried cassava", "description": ""},
            "es-ES": {"name": "Yuca frita", "description": ""},
        },
    },
    {
        "category": "Entradas",
        "dish": "Batata Frita",
        "translations": {
            "en-US": {"name": "French fries", "description": ""},
            "es-ES": {"name": "Papas fritas", "description": ""},
        },
    },
    {
        "category": "Camarao",
        "dish": "Camarão Catupiry",
        "translations": {
            "en-US": {
                "name": "Shrimp with Catupiry",
                "description": "Shrimp sautéed with butter, onions, white sauce and Catupiry cheese, topped with mozzarella and Parmesan. Sides: rice, fries and salad.",
            },
            "es-ES": {
                "name": "Camarones con Catupiry",
                "description": "Camarones salteados con mantequilla, cebolla, salsa blanca y Catupiry, cubiertos con queso mozzarella y parmesano. Acompañamientos: arroz, papas fritas y ensalada.",
            },
        },
    },
    {
        "category": "Camarao",
        "dish": "Camarão à Grega",
        "translations": {
            "en-US": {
                "name": "Greek-style shrimp",
                "description": "Breaded shrimp au gratin with mozzarella and Parmesan. Sides: Greek rice, fries and salad.",
            },
            "es-ES": {
                "name": "Camarones al estilo griego",
                "description": "Camarones empanizados gratinados con queso mozzarella y parmesano. Acompañamientos: arroz a la griega, papas fritas y ensalada.",
            },
        },
    },
    {
        "category": "Camarao",
        "dish": "Camarão à milanesa",
        "translations": {
            "en-US": {
                "name": "Breaded shrimp platter",
                "description": "Traditional breaded shrimp. Sides: rice, fries and salad.",
            },
            "es-ES": {
                "name": "Camarones empanizados",
                "description": "Camarones empanizados tradicionales. Acompañamientos: arroz, papas fritas y ensalada.",
            },
        },
    },
    {
        "category": "Camarao",
        "dish": "Camarão à Moda Marinheiro's",
        "translations": {
            "en-US": {
                "name": "Marinheiro's-style shrimp",
                "description": "Shrimp sautéed with onions, tomatoes, olives and cream, finished with fresh parsley. Sides: rice, fries and salad.",
            },
            "es-ES": {
                "name": "Camarones a la Marinheiro's",
                "description": "Camarones salteados con cebolla, tomate, aceitunas y crema de leche, finalizados con perejil fresco. Acompañamientos: arroz, papas fritas y ensalada.",
            },
        },
    },
    {
        "category": "Camarao",
        "dish": "Strogonoff de camarão",
        "translations": {
            "en-US": {
                "name": "Shrimp stroganoff",
                "description": "Shrimp served in a special cream and mushroom sauce. Sides: rice, fries and salad.",
            },
            "es-ES": {
                "name": "Stroganoff de camarón",
                "description": "Camarones servidos en una salsa especial de crema de leche y champiñones. Acompañamientos: arroz, papas fritas y ensalada.",
            },
        },
    },
    {
        "category": "Camarao",
        "dish": "Camarão à Praia Brava",
        "translations": {
            "en-US": {
                "name": "Praia Brava shrimp",
                "description": "Shrimp sautéed with rice, cheese, peas, white sauce and Catupiry, finished with mozzarella, Parmesan and breaded shrimp. Sides: fries and salad.",
            },
            "es-ES": {
                "name": "Camarones Praia Brava",
                "description": "Camarones salteados con arroz, queso, arvejas, salsa blanca y Catupiry, finalizados con queso mozzarella, parmesano y camarones empanizados. Acompañamientos: papas fritas y ensalada.",
            },
        },
    },
    {
        "category": "Lula",
        "dish": "Lula à milanesa",
        "translations": {
            "en-US": {
                "name": "Breaded squid platter",
                "description": "Traditional breaded squid. Sides: rice, fries and salad.",
            },
            "es-ES": {
                "name": "Calamares empanizados",
                "description": "Calamares empanizados tradicionales. Acompañamientos: arroz, papas fritas y ensalada.",
            },
        },
    },
    {
        "category": "Salmao",
        "dish": "Salmão Grelhado",
        "translations": {
            "en-US": {
                "name": "Grilled salmon",
                "description": "Griddled salmon fillet. Sides: rice, sautéed vegetables and pirão.",
            },
            "es-ES": {
                "name": "Salmón a la parrilla",
                "description": "Filete de salmón a la plancha. Acompañamientos: arroz, vegetales salteados y pirão.",
            },
        },
    },
    {
        "category": "Salmao",
        "dish": "Salmão ao molho de alcaparras",
        "translations": {
            "en-US": {
                "name": "Salmon with caper sauce",
                "description": "Grilled salmon fillet served with caper sauce. Sides: rice, sautéed potatoes and pirão.",
            },
            "es-ES": {
                "name": "Salmón con salsa de alcaparras",
                "description": "Filete de salmón a la plancha servido con salsa de alcaparras. Acompañamientos: arroz, papas salteadas y pirão.",
            },
        },
    },
    {
        "category": "Salmao",
        "dish": "Salmão à Belle Meunière",
        "translations": {
            "en-US": {
                "name": "Belle Meunière salmon",
                "description": "Grilled salmon fillet served with a special sauce of capers, mushrooms, shrimp and soy sauce. Sides: rice, sautéed potatoes and pirão.",
            },
            "es-ES": {
                "name": "Salmón Belle Meunière",
                "description": "Filete de salmón a la plancha servido con una salsa especial de alcaparras, champiñones, camarones y salsa de soja. Acompañamientos: arroz, papas salteadas y pirão.",
            },
        },
    },
    {
        "category": "Salmao",
        "dish": "Salmão ao molho de laranja",
        "translations": {
            "en-US": {
                "name": "Salmon with orange sauce",
                "description": "Grilled salmon fillet served with a special sauce of orange, honey and white Cabernet, finished with fresh parsley. Sides: rice, sautéed vegetables and salad.",
            },
            "es-ES": {
                "name": "Salmón con salsa de naranja",
                "description": "Filete de salmón a la plancha servido con una salsa especial de naranja, miel y cabernet blanco, finalizado con perejil fresco. Acompañamientos: arroz, vegetales salteados y ensalada.",
            },
        },
    },
    {
        "category": "Cacarolas e Moquecas",
        "dish": "Caçarola de frutos do mar",
        "translations": {
            "en-US": {
                "name": "Seafood casserole",
                "description": "Seafood in tomato sauce with onions, peppers, dendê oil and coconut milk. Sides: rice, fries and salad.",
            },
            "es-ES": {
                "name": "Cazuela de mariscos",
                "description": "Mariscos en salsa de tomate con cebolla, pimientos, aceite de dendê y leche de coco. Acompañamientos: arroz, papas fritas y ensalada.",
            },
        },
    },
    {
        "category": "Cacarolas e Moquecas",
        "dish": "Moqueca de peixes",
        "translations": {
            "en-US": {
                "name": "Fish moqueca",
                "description": "Fish fillet in tomato sauce with onions, peppers, dendê oil and coconut milk. Sides: rice, fries and salad.",
            },
            "es-ES": {
                "name": "Moqueca de pescado",
                "description": "Filete de pescado en salsa de tomate con cebolla, pimientos, aceite de dendê y leche de coco. Acompañamientos: arroz, papas fritas y ensalada.",
            },
        },
    },
    {
        "category": "Cacarolas e Moquecas",
        "dish": "Moqueca de peixes com camarão",
        "translations": {
            "en-US": {
                "name": "Fish and shrimp moqueca",
                "description": "Fish fillet and shrimp in tomato sauce with onions, dendê oil and coconut milk. Sides: rice, fries and salad.",
            },
            "es-ES": {
                "name": "Moqueca de pescado con camarón",
                "description": "Filete de pescado y camarones en salsa de tomate con cebolla, aceite de dendê y leche de coco. Acompañamientos: arroz, papas fritas y ensalada.",
            },
        },
    },
    {
        "category": "Anchova",
        "dish": "Anchova grelhada",
        "translations": {
            "en-US": {
                "name": "Grilled Anchova",
                "description": "Bluefish Anchova on the griddle. Sides: rice, sautéed potatoes and pirão.",
            },
            "es-ES": {
                "name": "Anchova a la parrilla",
                "description": "Anchova a la plancha. Acompañamientos: arroz, papas salteadas y pirão.",
            },
        },
    },
    {
        "category": "Anchova",
        "dish": "Anchova ao molho de alcaparras",
        "translations": {
            "en-US": {
                "name": "Anchova with caper sauce",
                "description": "Grilled Anchova served with caper sauce. Sides: rice, sautéed potatoes and pirão.",
            },
            "es-ES": {
                "name": "Anchova con salsa de alcaparras",
                "description": "Anchova a la plancha servida con salsa de alcaparras. Acompañamientos: arroz, papas salteadas y pirão.",
            },
        },
    },
    {
        "category": "Anchova",
        "dish": "Anchova à Belle Meunière",
        "translations": {
            "en-US": {
                "name": "Belle Meunière Anchova",
                "description": "Grilled Anchova served with a special sauce of capers, mushrooms, shrimp and soy sauce. Sides: rice, sautéed potatoes and pirão.",
            },
            "es-ES": {
                "name": "Anchova Belle Meunière",
                "description": "Anchova a la plancha servida con una salsa especial de alcaparras, champiñones, camarones y salsa de soja. Acompañamientos: arroz, papas salteadas y pirão.",
            },
        },
    },
    {
        "category": "Linguado",
        "dish": "Linguado grelhado",
        "translations": {
            "en-US": {
                "name": "Grilled flounder",
                "description": "Flounder fillet grilled on the griddle. Sides: rice, sautéed potatoes and pirão.",
            },
            "es-ES": {
                "name": "Lenguado a la parrilla",
                "description": "Filete de lenguado a la plancha. Acompañamientos: arroz, papas salteadas y pirão.",
            },
        },
    },
    {
        "category": "Linguado",
        "dish": "Linguado ao molho de alcaparras",
        "translations": {
            "en-US": {
                "name": "Flounder with caper sauce",
                "description": "Grilled flounder served with caper sauce. Sides: rice, sautéed potatoes and pirão.",
            },
            "es-ES": {
                "name": "Lenguado con salsa de alcaparras",
                "description": "Lenguado a la plancha servido con salsa de alcaparras. Acompañamientos: arroz, papas salteadas y pirão.",
            },
        },
    },
    {
        "category": "Linguado",
        "dish": "Linguado à Belle Meunière",
        "translations": {
            "en-US": {
                "name": "Belle Meunière flounder",
                "description": "Grilled flounder served with a special sauce of capers, mushrooms, shrimp and soy sauce. Sides: rice, sautéed potatoes and pirão.",
            },
            "es-ES": {
                "name": "Lenguado Belle Meunière",
                "description": "Lenguado a la plancha servido con una salsa especial de alcaparras, champiñones, camarones y salsa de soja. Acompañamientos: arroz, papas salteadas y pirão.",
            },
        },
    },
    {
        "category": "Linguado",
        "dish": "Linguado ao molho de camarão",
        "translations": {
            "en-US": {
                "name": "Flounder with shrimp sauce",
                "description": "Breaded flounder fillet served with shrimp sauce, finished with fresh parsley. Sides: rice, fries and salad.",
            },
            "es-ES": {
                "name": "Lenguado con salsa de camarón",
                "description": "Filete de lenguado empanizado servido con salsa de camarón, finalizado con perejil fresco. Acompañamientos: arroz, papas fritas y ensalada.",
            },
        },
    },
    {
        "category": "Linguado",
        "dish": "Linguado à Moda Marinheiro's",
        "translations": {
            "en-US": {
                "name": "Marinheiro's-style flounder",
                "description": "Grilled flounder served with a special sauce of onions, tomatoes, olives and cream, finished with fresh parsley. Sides: rice, fries and salad.",
            },
            "es-ES": {
                "name": "Lenguado a la Marinheiro's",
                "description": "Lenguado a la plancha servido con una salsa especial de cebolla, tomate, aceitunas y crema de leche, finalizado con perejil fresco. Acompañamientos: arroz, papas fritas y ensalada.",
            },
        },
    },
    {
        "category": "Congrio Rosa",
        "dish": "Congrio Rosa grelhado",
        "translations": {
            "en-US": {
                "name": "Grilled Congrio Rosa",
                "description": "Congrio Rosa fillet grilled on the griddle. Sides: rice, sautéed potatoes and pirão.",
            },
            "es-ES": {
                "name": "Congrio Rosa a la parrilla",
                "description": "Filete de congrio rosa a la plancha. Acompañamientos: arroz, papas salteadas y pirão.",
            },
        },
    },
    {
        "category": "Congrio Rosa",
        "dish": "Congrio Rosa ao molho de alcaparras",
        "translations": {
            "en-US": {
                "name": "Congrio Rosa with caper sauce",
                "description": "Grilled Congrio Rosa served with caper sauce. Sides: rice, sautéed potatoes and pirão.",
            },
            "es-ES": {
                "name": "Congrio Rosa con salsa de alcaparras",
                "description": "Congrio Rosa a la plancha servido con salsa de alcaparras. Acompañamientos: arroz, papas salteadas y pirão.",
            },
        },
    },
    {
        "category": "Congrio Rosa",
        "dish": "Congrio Rosa à Belle Meunière",
        "translations": {
            "en-US": {
                "name": "Belle Meunière Congrio Rosa",
                "description": "Grilled Congrio Rosa served with a special sauce of capers, mushrooms, shrimp and soy sauce. Sides: rice, sautéed potatoes and pirão.",
            },
            "es-ES": {
                "name": "Congrio Rosa Belle Meunière",
                "description": "Congrio Rosa a la plancha servido con una salsa especial de alcaparras, champiñones, camarones y salsa de soja. Acompañamientos: arroz, papas salteadas y pirão.",
            },
        },
    },
    {
        "category": "Congrio Rosa",
        "dish": "Congrio Rosa ao molho de camarão",
        "translations": {
            "en-US": {
                "name": "Congrio Rosa with shrimp sauce",
                "description": "Breaded Congrio Rosa fillet served with shrimp sauce and finished with fresh parsley. Sides: rice, fries and salad.",
            },
            "es-ES": {
                "name": "Congrio Rosa con salsa de camarón",
                "description": "Filete de Congrio Rosa empanizado servido con salsa de camarón y finalizado con perejil fresco. Acompañamientos: arroz, papas fritas y ensalada.",
            },
        },
    },
    {
        "category": "Congrio Rosa",
        "dish": "Congrio Rosa à Moda Marinheiro's",
        "translations": {
            "en-US": {
                "name": "Marinheiro's-style Congrio Rosa",
                "description": "Grilled pink conger served with a special sauce of onions, tomatoes, olives and cream, finished with fresh parsley. Sides: rice, fries and salad.",
            },
            "es-ES": {
                "name": "Congrio Rosa a la Marinheiro's",
                "description": "Congrio Rosa a la plancha servido con una salsa especial de cebolla, tomate, aceitunas y crema de leche, finalizado con perejil fresco. Acompañamientos: arroz, papas fritas y ensalada.",
            },
        },
    },
    {
        "category": "File de peixe",
        "dish": "Peixe grelhado",
        "translations": {
            "en-US": {
                "name": "Grilled fish fillet",
                "description": "Fish fillet grilled on the griddle. Sides: rice, sautéed potatoes and pirão.",
            },
            "es-ES": {
                "name": "Filete de pescado a la parrilla",
                "description": "Filete de pescado a la plancha. Acompañamientos: arroz, papas salteadas y pirão.",
            },
        },
    },
    {
        "category": "File de peixe",
        "dish": "Peixe ao molho de alcaparras",
        "translations": {
            "en-US": {
                "name": "Fish fillet with caper sauce",
                "description": "Fish fillet grilled on the griddle served with caper sauce. Sides: rice, sautéed potatoes and pirão.",
            },
            "es-ES": {
                "name": "Filete de pescado con salsa de alcaparras",
                "description": "Filete de pescado a la plancha servido con salsa de alcaparras. Acompañamientos: arroz, papas salteadas y pirão.",
            },
        },
    },
    {
        "category": "File de peixe",
        "dish": "Peixe à milanesa",
        "translations": {
            "en-US": {
                "name": "Breaded fish fillet",
                "description": "Traditional breaded fish fillet. Sides: rice, fries and salad.",
            },
            "es-ES": {
                "name": "Filete de pescado empanizado",
                "description": "Filete de pescado empanizado tradicional. Acompañamientos: arroz, papas fritas y ensalada.",
            },
        },
    },
    {
        "category": "File de peixe",
        "dish": "Peixe ao molho de camarão",
        "translations": {
            "en-US": {
                "name": "Fish fillet with shrimp sauce",
                "description": "Breaded fish fillet served with shrimp sauce and finished with fresh parsley. Sides: rice, fries and salad.",
            },
            "es-ES": {
                "name": "Filete de pescado con salsa de camarón",
                "description": "Filete de pescado empanizado servido con salsa de camarón y finalizado con perejil fresco. Acompañamientos: arroz, papas fritas y ensalada.",
            },
        },
    },
    {
        "category": "File de peixe",
        "dish": "Peixe à Moda Marinheiro's",
        "translations": {
            "en-US": {
                "name": "Marinheiro's-style fish fillet",
                "description": "Fish fillet grilled on the griddle served with a special sauce of onions, tomatoes, olives and cream, finished with fresh parsley. Sides: rice, fries and salad.",
            },
            "es-ES": {
                "name": "Filete de pescado a la Marinheiro's",
                "description": "Filete de pescado a la plancha servido con una salsa especial de cebolla, tomate, aceitunas y crema de leche, finalizado con perejil fresco. Acompañamientos: arroz, papas fritas y ensalada.",
            },
        },
    },
    {
        "category": "Carne",
        "dish": "Filé mignon grelhado",
        "translations": {
            "en-US": {
                "name": "Grilled filet mignon",
                "description": "Filet mignon grilled on the griddle. Sides: rice, fries and salad.",
            },
            "es-ES": {
                "name": "Filet mignon a la parrilla",
                "description": "Filet mignon a la plancha. Acompañamientos: arroz, papas fritas y ensalada.",
            },
        },
    },
    {
        "category": "Carne",
        "dish": "Filé mignon ao molho Madeira",
        "translations": {
            "en-US": {
                "name": "Filet mignon with Madeira sauce",
                "description": "Filet mignon grilled on the griddle with Madeira sauce made with red cabernet and mushrooms, finished with fresh parsley. Sides: rice, sautéed vegetables and salad.",
            },
            "es-ES": {
                "name": "Filet mignon con salsa Madeira",
                "description": "Filet mignon a la plancha con salsa Madeira elaborada con cabernet tinto y champiñones, finalizado con perejil fresco. Acompañamientos: arroz, vegetales salteados y ensalada.",
            },
        },
    },
    {
        "category": "Carne",
        "dish": "Filé mignon acebolado",
        "translations": {
            "en-US": {
                "name": "Filet mignon with onions",
                "description": "Filet mignon grilled on the griddle with onions sautéed in butter and soy sauce. Sides: rice, fries and salad.",
            },
            "es-ES": {
                "name": "Filet mignon encebollado",
                "description": "Filet mignon a la plancha con cebollas salteadas en mantequilla y salsa de soja. Acompañamientos: arroz, papas fritas y ensalada.",
            },
        },
    },
    {
        "category": "Carne",
        "dish": "Filé mignon à Parmegiana",
        "translations": {
            "en-US": {
                "name": "Parmesan filet mignon",
                "description": "Breaded filet mignon with tomato sauce, corn, peas, mozzarella and Parmesan. Sides: rice, fries and salad.",
            },
            "es-ES": {
                "name": "Filet mignon a la parmesana",
                "description": "Filet mignon empanizado con salsa de tomate, maíz, arvejas, queso mozzarella y parmesano. Acompañamientos: arroz, papas fritas y ensalada.",
            },
        },
    },
    {
        "category": "Carne",
        "dish": "Strogonoff de carne",
        "translations": {
            "en-US": {
                "name": "Beef stroganoff",
                "description": "Filet mignon cubes served in a special cream and mushroom sauce. Sides: rice, fries and salad.",
            },
            "es-ES": {
                "name": "Stroganoff de carne",
                "description": "Cubos de filet mignon servidos en una salsa especial de crema de leche y champiñones. Acompañamientos: arroz, papas fritas y ensalada.",
            },
        },
    },
    {
        "category": "Frango",
        "dish": "Frango grelhado",
        "translations": {
            "en-US": {
                "name": "Grilled chicken breast",
                "description": "Chicken breast grilled on the griddle. Sides: rice, sautéed vegetables and salad.",
            },
            "es-ES": {
                "name": "Pechuga de pollo a la parrilla",
                "description": "Pechuga de pollo a la plancha. Acompañamientos: arroz, vegetales salteados y ensalada.",
            },
        },
    },
    {
        "category": "Frango",
        "dish": "Frango à milanesa",
        "translations": {
            "en-US": {
                "name": "Breaded chicken breast",
                "description": "Traditional breaded chicken breast. Sides: rice, fries and salad.",
            },
            "es-ES": {
                "name": "Pechuga de pollo empanizada",
                "description": "Pechuga de pollo empanizada tradicional. Acompañamientos: arroz, papas fritas y ensalada.",
            },
        },
    },
    {
        "category": "Frango",
        "dish": "Frango à Romana",
        "translations": {
            "en-US": {
                "name": "Roman-style chicken",
                "description": "Chicken breast grilled on the griddle with white sauce and peas, gratinéed with mozzarella and Parmesan. Sides: rice, fries and salad.",
            },
            "es-ES": {
                "name": "Pollo a la Romana",
                "description": "Pechuga de pollo a la plancha con salsa blanca y arvejas, gratinada con queso mozzarella y parmesano. Acompañamientos: arroz, papas fritas y ensalada.",
            },
        },
    },
    {
        "category": "Frango",
        "dish": "Frango à Parmegiana",
        "translations": {
            "en-US": {
                "name": "Parmesan chicken",
                "description": "Breaded chicken breast with tomato sauce, corn, peas, mozzarella and Parmesan. Sides: rice, fries and salad.",
            },
            "es-ES": {
                "name": "Pollo a la parmesana",
                "description": "Pechuga de pollo empanizada con salsa de tomate, maíz, arvejas, queso mozzarella y parmesano. Acompañamientos: arroz, papas fritas y ensalada.",
            },
        },
    },
    {
        "category": "Bebidas",
        "dish": "Suco",
        "translations": {
            "en-US": {
                "name": "Juice",
                "description": "Flavors: pineapple, orange, acerola, lime, passion fruit and strawberry.",
            },
            "es-ES": {
                "name": "Jugo",
                "description": "Sabores: piña, naranja, acerola, limón, maracuyá y fresa.",
            },
        },
    },
    {
        "category": "Bebidas",
        "dish": "Refrigerante",
        "translations": {
            "en-US": {
                "name": "Soda",
                "description": "Options: Coca-Cola, Coca-Cola Zero, Guaraná, Guaraná Zero, Fanta Grape, Fanta Orange, Sprite, Tônica and H2O.",
            },
            "es-ES": {
                "name": "Refresco",
                "description": "Opciones: Coca-Cola, Coca-Cola Zero, Guaraná, Guaraná Zero, Fanta Uva, Fanta Naranja, Sprite, Tónica y H2O.",
            },
        },
    },
    {
        "category": "Bebidas",
        "dish": "Cerveja",
        "translations": {
            "en-US": {
                "name": "Beer",
                "description": "600 ml: Original or Heineken.",
            },
            "es-ES": {
                "name": "Cerveza",
                "description": "600 ml: Original o Heineken.",
            },
        },
    },
    {
        "category": "Bebidas",
        "dish": "Caipirinha",
        "translations": {
            "en-US": {
                "name": "Caipirinha",
                "description": "Classic version prepared with vodka.",
            },
            "es-ES": {
                "name": "Caipirinha",
                "description": "Versión clásica preparada con vodka.",
            },
        },
    },
    {
        "category": "Bebidas",
        "dish": "Long neck",
        "translations": {
            "en-US": {
                "name": "Long neck beer",
                "description": "Heineken or Malzbier long neck bottles.",
            },
            "es-ES": {
                "name": "Cerveza long neck",
                "description": "Botellas long neck de Heineken o Malzbier.",
            },
        },
    },
    {
        "category": "Bebidas",
        "dish": "Água",
        "translations": {
            "en-US": {
                "name": "Water",
                "description": "Sparkling or still water.",
            },
            "es-ES": {
                "name": "Agua",
                "description": "Agua con gas o sin gas.",
            },
        },
    },
]


def load_translations(apps, schema_editor):
    Category = apps.get_model("menu", "Category")
    CategoryTranslation = apps.get_model("menu", "CategoryTranslation")
    Dish = apps.get_model("menu", "Dish")
    DishTranslation = apps.get_model("menu", "DishTranslation")

    for category_name, translations in CATEGORY_TRANSLATIONS.items():
        try:
            category = Category.objects.get(name=category_name)
        except Category.DoesNotExist:
            continue
        for language, translated_name in translations.items():
            CategoryTranslation.objects.update_or_create(
                category=category,
                language=language,
                defaults={"name": translated_name},
            )

    for dish_data in DISH_TRANSLATIONS:
        try:
            dish = Dish.objects.get(
                name=dish_data["dish"], category__name=dish_data["category"]
            )
        except Dish.DoesNotExist:
            continue
        for language, translated in dish_data["translations"].items():
            translated_name = translated["name"]
            original_name = dish.name
            display_name = (
                f"{translated_name} ({original_name})"
                if translated_name
                else original_name
            )
            DishTranslation.objects.update_or_create(
                dish=dish,
                language=language,
                defaults={
                    "name": display_name,
                    "description": translated["description"],
                },
            )


def remove_translations(apps, schema_editor):
    CategoryTranslation = apps.get_model("menu", "CategoryTranslation")
    Dish = apps.get_model("menu", "Dish")
    DishTranslation = apps.get_model("menu", "DishTranslation")

    for dish_data in DISH_TRANSLATIONS:
        DishTranslation.objects.filter(
            dish__name=dish_data["dish"],
            dish__category__name=dish_data["category"],
            language__in=dish_data["translations"].keys(),
        ).delete()

    for category_name, languages in CATEGORY_TRANSLATIONS.items():
        CategoryTranslation.objects.filter(
            category__name=category_name, language__in=languages.keys()
        ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("menu", "0009_load_menu_from_a4_menu"),
    ]

    operations = [
        migrations.RunPython(load_translations, reverse_code=remove_translations),
    ]

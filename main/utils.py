def calculate_order_price(order, model):
    base_price = float(model.base_price)

    material_coef = {
        'PLA': 1.0,
        'PETG': 1.2,
        'ABS': 1.35,
    }.get(order.material, 1.0)

    layer_coef = {
        100: 1.3,
        200: 1.0,
        300: 0.85,
    }.get(order.layer_height, 1.0)

    wall_coef = {
        1: 1.0,
        2: 1.15,
        3: 1.3,
    }.get(order.wall_thickness, 1.0)

    infill_coef = 1 + (order.infill / 100)

    size_coef = order.size / 10

    total = (
        base_price
        * material_coef
        * layer_coef
        * wall_coef
        * infill_coef
        * size_coef
        * order.quantity
    )

    return round(total, 2)

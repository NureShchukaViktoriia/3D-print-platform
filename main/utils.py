
def calculate_print_price(
    base_weight,
    complexity,
    supports_required,
    recommended_wall_thickness,
    size,
    base_size,
    infill,
    wall_thickness,
    material,
    quality,
    quantity=1
):
    from .models import MaterialPrice
    material_price = MaterialPrice.objects.get(
        material=material,
        quality=quality
    )

    size_coefficient = (float(size) / float(base_size)) ** 3

    infill_coefficient = 0.4 + float(infill) / 100

    wall_coefficient = (
        float(wall_thickness)
        / float(recommended_wall_thickness)
    )

    estimated_weight = (
        float(base_weight)
        * size_coefficient
        * infill_coefficient
        * wall_coefficient
        * float(complexity)
    )

    if supports_required:
        estimated_weight *= 1.15

    total_price = (
        estimated_weight
        * float(material_price.price_per_gram)
        * quantity
    )

    return {
        "weight": round(estimated_weight, 2),
        "price": round(total_price, 2)
    }
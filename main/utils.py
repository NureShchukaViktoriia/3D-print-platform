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
    
    # === ОСНОВНА ФІКСАЦІЯ ===
    # 1. Коефіцієнт масштабування (об'єм - кубічна залежність)
    scale_factor = float(size) / float(base_size)
    size_coefficient = scale_factor ** 3
    
    # 2. Коефіцієнт заповнення (нормалізований: 0% -> 0%, 100% -> 100%)
    #    Для стандартного PLA: 10% інфілу дає ~30% ваги суцільної моделі
    infill_coefficient = 0.3 + (float(infill) / 100) * 0.7
    
    # 3. Коефіцієнт товщини стінки (обмежений)
    wall_ratio = float(wall_thickness) / float(recommended_wall_thickness)
    wall_coefficient = max(0.6, min(1.8, wall_ratio))
    
    # 4. Коефіцієнт складності (помірний вплив, не квадратичний)
    #    Складність 2.0 означає +20% до ваги (підтримки, переміщення)
    complexity_coefficient = 1.0 + (float(complexity) - 1.0) * 0.2
    
    # 5. Розрахунок ваги
    #    ВАЖЛИВО: base_weight - це вага базової моделі (при size=base_size)
    estimated_weight = (
        float(base_weight) 
        * size_coefficient 
        * infill_coefficient 
        * wall_coefficient
    )
    
    # 6. Додаткові підтримки (+5% до ваги)
    if supports_required:
        estimated_weight *= 1.05
    
    # 7. Вплив складності
    final_weight = estimated_weight * complexity_coefficient
    
    # 8. Вартість матеріалу
    material_cost = final_weight * float(material_price.price_per_gram)
    
    # 9. Додаткові збори:
    #    - За високий інфіл (>70%)
    #    - За великий розмір (>20 см) - час друку
    extra_fee = 0
    if infill > 70:
        material_cost *= 1.10
    
    if size > 200:  # більше 20 см
        extra_fee += 30  # грн за довгий друк
    
    total_price = (material_cost + extra_fee) * quantity
    
    return {
        "weight": round(final_weight, 2),
        "price": round(total_price, 2)
    }
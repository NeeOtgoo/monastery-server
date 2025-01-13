import math
    
def custom_paginate(queryset, page_number, items_per_page):
    start_index = (page_number - 1) * items_per_page
    end_index = page_number * items_per_page
    paginated_data = queryset[start_index:end_index]
    total_count = queryset.count()
    page_count = math.ceil(total_count / items_per_page)
    return {
        "records": paginated_data,
        "page_count": page_count,
        "total_count": total_count
    }
    
def calculate_mongolian_zodiac(year):
    
    animals = ["Хулгана", "Үхэр", "Бар", "Туулай", "Луу", "Могой", 
               "Морь", "Хонь", "Бич", "Тахиа", "Нохой", "Гахай"]
    elements = ["Мод", "Гал", "Шороо", "Төмөр", "Ус"]

    
    animal_index = (year - 4) % 12  
    element_index = ((year - 4) % 10) // 2  # 

    
    animal = animals[animal_index]
    element = elements[element_index]

    
    return {
        "year": year,
        "animal": animal,
        "element": element
    }
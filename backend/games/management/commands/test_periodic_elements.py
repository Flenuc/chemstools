from django.core.management.base import BaseCommand
from games.utils import PeriodicSpeedEngine

class Command(BaseCommand):
    help = 'Test periodic table elements loading and categorization'
    
    def handle(self, *args, **options):
        try:
            elements = PeriodicSpeedEngine.get_periodic_table_data()
            
            self.stdout.write(f'Total elements loaded: {len(elements)}')
            
            # Categorizar elementos
            categories = {}
            for element in elements:
                category = element.get('category', 'unknown')
                if category not in categories:
                    categories[category] = []
                categories[category].append(element)
            
            self.stdout.write('\n📋 Elements by category:')
            for category, elem_list in categories.items():
                self.stdout.write(f'  {category}: {len(elem_list)} elements')
                
                # Mostrar algunos ejemplos
                examples = elem_list[:3]
                example_names = [f"{e['name']} ({e['symbol']})" for e in examples]
                self.stdout.write(f'    Examples: {", ".join(example_names)}')
            
            # Verificar elementos comunes
            self.stdout.write('\n🌟 Common elements (first 20 + some others):')
            common_numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 26, 29, 47, 79]
            common_elements = [e for e in elements if e['number'] in common_numbers]
            
            for element in common_elements:
                mapped_category = PeriodicSpeedEngine.ELEMENT_CATEGORIES.get(element['category'], 'unknown')
                self.stdout.write(f'  {element["number"]}. {element["name"]} ({element["symbol"]}) - {mapped_category}')
            
            # Verificar elementos raros
            self.stdout.write('\n💎 Rare elements (Z>80 or lanthanides/actinides):')
            rare_elements = [e for e in elements if e['number'] > 80 or (57 <= e['number'] <= 71) or (89 <= e['number'] <= 103)]
            
            for element in rare_elements[:10]:  # Solo primeros 10
                self.stdout.write(f'  {element["number"]}. {element["name"]} ({element["symbol"]})')
            
            self.stdout.write(f'\nTotal rare elements: {len(rare_elements)}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
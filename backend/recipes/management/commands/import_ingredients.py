import json
from django.core.management.base import BaseCommand
from recipes.models import Product

class Command(BaseCommand):
    help = 'Импорт ингредиентов из JSON-файла'

    def add_arguments(self, parser):
        parser.add_argument('json_path', type=str, help='Путь к JSON-файлу с ингредиентами')

    def handle(self, *args, **options):
        json_path = options['json_path']
        with open(json_path, encoding='utf-8') as f:
            data = json.load(f)
        count = 0
        for item in data:
            name = item.get('name')
            unit = item.get('measurement_unit')
            if name and unit:
                Product.objects.get_or_create(name=name, unit=unit)
                count += 1
        self.stdout.write(self.style.SUCCESS(f'Импортировано {count} ингредиентов.')) 
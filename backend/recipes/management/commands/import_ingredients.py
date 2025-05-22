import json
from django.core.management.base import BaseCommand
from recipes.models import Ingredient

class Command(BaseCommand):
    help = 'Импорт ингредиентов из JSON-файла'

    def add_arguments(self, parser):
        parser.add_argument('json_path', type=str, help='Путь к JSON-файлу с ингредиентами')

    def handle(self, *args, **options):
        try:
            with open(options['json_path'], encoding='utf-8') as f:
                ingredients = [
                    Ingredient(**item)
                    for item in json.load(f)
                    if all(key in item for key in ('name', 'measurement_unit'))
                ]
            Ingredient.objects.bulk_create(ingredients, ignore_conflicts=True)
            self.stdout.write(
                self.style.SUCCESS(f'Импортировано {len(ingredients)} ингредиентов.')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при импорте: {str(e)}')
            ) 
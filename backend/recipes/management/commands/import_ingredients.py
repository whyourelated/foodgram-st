import json
from django.core.management.base import BaseCommand
from recipes.models import Ingredient

class Command(BaseCommand):
    help = 'Импорт ингредиентов из JSON-файла'

    def add_arguments(self, parser):
        parser.add_argument('json_path', type=str, help='Путь к JSON-файлу с ингредиентами')

    def handle(self, *args, **options):
        json_path = options['json_path']
        try:
            with open(json_path, encoding='utf-8') as f:
                Ingredient.objects.bulk_create(
                    (
                        Ingredient(**item)
                        for item in json.load(f)
                    ),
                    ignore_conflicts=True
                )
            total = Ingredient.objects.count()
            self.stdout.write(
                self.style.SUCCESS(f'Ингредиенты успешно импортированы из {json_path}. Всего в базе: {total}.')
            )
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f'Ошибка при импорте из {json_path}: {e}')
            )

from django.core.management.base import BaseCommand
from core.models import AgreementType


class Command(BaseCommand):
    help = 'Populate agreement types for Agreement Studio'

    def handle(self, *args, **kwargs):
        types = [
            {
                'name': 'Love or Partnership',
                'slug': 'love-partnership',
                'description': 'For something worth keeping clear.',
                'icon': '❤️'
            },
            {
                'name': 'Friendship or Promise',
                'slug': 'friendship-promise',
                'description': 'For two people finding balance.',
                'icon': '🤝'
            },
            {
                'name': 'Work or Creative Collaboration',
                'slug': 'work-collaboration',
                'description': 'For shared vision and mutual respect.',
                'icon': '✨'
            },
            {
                'name': 'Living Together',
                'slug': 'living-together',
                'description': 'For harmony in shared space.',
                'icon': '🏠'
            },
            {
                'name': 'Personal Commitment',
                'slug': 'personal-commitment',
                'description': 'For a promise to yourself.',
                'icon': '🌱'
            }
        ]

        created_count = 0
        for type_data in types:
            obj, created = AgreementType.objects.get_or_create(
                slug=type_data['slug'],
                defaults=type_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {obj.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'- Already exists: {obj.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\n{created_count} new agreement types created!')
        )
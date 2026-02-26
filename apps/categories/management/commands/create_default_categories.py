"""
Management command to create default categories.
"""
from django.core.management.base import BaseCommand
from apps.categories.models import Category


class Command(BaseCommand):
    help = 'Create default event categories'
    
    def handle(self, *args, **options):
        """Create default categories."""
        default_categories = [
            {
                'name': 'Cultural & Arts',
                'description': 'Museums, galleries, concerts, theater, and cultural events',
                'icon': '🎨'
            },
            {
                'name': 'Sports & Fitness',
                'description': 'Sports events, fitness activities, tournaments, and competitions',
                'icon': '⚽'
            },
            {
                'name': 'Business & Professional',
                'description': 'Conferences, networking, workshops, and business meetings',
                'icon': '💼'
            },
            {
                'name': 'Technology & Science',
                'description': 'Tech conferences, hackathons, science fairs, and innovation events',
                'icon': '💻'
            },
            {
                'name': 'Social & Community',
                'description': 'Community gatherings, meetups, and social events',
                'icon': '👥'
            },
            {
                'name': 'Education',
                'description': 'Educational workshops, seminars, courses, and training',
                'icon': '📚'
            },
            {
                'name': 'Entertainment',
                'description': 'Parties, festivals, shows, and entertainment events',
                'icon': '🎉'
            },
            {
                'name': 'Food & Drink',
                'description': 'Food festivals, wine tasting, cooking classes, and culinary events',
                'icon': '🍽️'
            },
            {
                'name': 'Travel & Outdoor',
                'description': 'Adventure trips, hiking, camping, and outdoor activities',
                'icon': '🏕️'
            },
            {
                'name': 'Religious & Spiritual',
                'description': 'Religious ceremonies, spiritual gatherings, and faith-based events',
                'icon': '🕌'
            },
            {
                'name': 'Fashion & Lifestyle',
                'description': 'Fashion shows, beauty events, and lifestyle exhibitions',
                'icon': '👗'
            },
            {
                'name': 'Political & Government',
                'description': 'Political rallies, government events, and civic activities',
                'icon': '🏛️'
            },
        ]
        
        created_count = 0
        for category_data in default_categories:
            category, created = Category.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'description': category_data['description'],
                    'icon': category_data['icon']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created category: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'○ Category already exists: {category.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Successfully created {created_count} categories!')
        )
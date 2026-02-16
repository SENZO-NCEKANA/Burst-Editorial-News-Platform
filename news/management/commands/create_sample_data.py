"""
Management command to create sample data for testing.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from news.models import Publisher, Category, Article, Newsletter

User = get_user_model()


class Command(BaseCommand):
    """
    Command to create sample data for testing.
    """
    help = 'Create sample data for testing'

    def handle(self, *args, **options):
        """
        Create sample data.
        """
        # Create publishers
        publisher1, created = Publisher.objects.get_or_create(
            name='Tech News Daily',
            defaults={
                'description': 'Latest technology news and updates',
                'website': 'https://technewsdaily.com'
            }
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS('Created publisher: Tech News Daily')
            )

        publisher2, created = Publisher.objects.get_or_create(
            name='World Affairs',
            defaults={
                'description': 'Global news and current events',
                'website': 'https://worldaffairs.com'
            }
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS('Created publisher: World Affairs')
            )

        for name, desc, website in [
            ('Pitch Report', 'Sports news and match coverage',
             'https://pitchreport.com'),
            ('Market Pulse', 'Business, finance and market news',
             'https://marketpulse.com'),
            ('The Daily Brief', 'Headlines and news digests',
             'https://thedailybrief.com'),
            ('ByteWire', 'Consumer tech and gadgets',
             'https://bytewire.com'),
            ('Policy Brief', 'Politics and policy analysis',
             'https://policybrief.com'),
            ('Lifestyle Plus', 'Health, wellness and culture',
             'https://lifestyleplus.com'),
        ]:
            pub, created = Publisher.objects.get_or_create(
                name=name,
                defaults={'description': desc, 'website': website}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created publisher: {name}')
                )

        # Create categories
        tech_category, created = Category.objects.get_or_create(
            name='Technology',
            defaults={'description': 'Technology news and updates'}
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS('Created category: Technology')
            )

        world_category, created = Category.objects.get_or_create(
            name='World News',
            defaults={'description': 'Global news and events'}
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS('Created category: World News')
            )

        for name, desc in [
            ('Sport', 'Sports news and updates'),
            ('Politics', 'Political news and analysis'),
            ('Business', 'Business and finance news'),
            ('Lifestyle', 'Lifestyle and culture'),
        ]:
            Category.objects.get_or_create(
                name=name,
                defaults={'description': desc}
            )

        # Create users
        journalist1, created = User.objects.get_or_create(
            username='Aphiwe_tech',
            defaults={
                'email': 'aphiwe@example.com',
                'first_name': 'Aphiwe',
                'last_name': 'Mthembu',
                'role': 'journalist'
            }
        )
        if created:
            journalist1.set_password('testpass123')
            journalist1.save()
            self.stdout.write(
                self.style.SUCCESS('Created journalist: Aphiwe_tech')
            )

        journalist2, created = User.objects.get_or_create(
            username='Kwanele_world',
            defaults={
                'email': 'kwanele@example.com',
                'first_name': 'Kwanele',
                'last_name': 'Ndlovu',
                'role': 'journalist'
            }
        )
        if created:
            journalist2.set_password('testpass123')
            journalist2.save()
            self.stdout.write(
                self.style.SUCCESS('Created journalist: Kwanele_world')
            )

        editor1, created = User.objects.get_or_create(
            username='editor_tech',
            defaults={
                'email': 'editor@technews.com',
                'first_name': 'Mike',
                'last_name': 'Editor',
                'role': 'editor'
            }
        )
        if created:
            editor1.set_password('testpass123')
            editor1.save()
            self.stdout.write(
                self.style.SUCCESS('Created editor: editor_tech')
            )

        reader1, created = User.objects.get_or_create(
            username='reader1',
            defaults={
                'email': 'reader1@example.com',
                'first_name': 'Alice',
                'last_name': 'Reader',
                'role': 'reader'
            }
        )
        if created:
            reader1.set_password('testpass123')
            reader1.save()
            self.stdout.write(
                self.style.SUCCESS('Created reader: reader1')
            )

        publisher_user, created = User.objects.get_or_create(
            username='publisher_tech',
            defaults={
                'email': 'publisher@technewsdaily.com',
                'first_name': 'Sarah',
                'last_name': 'Publisher',
                'role': 'publisher'
            }
        )
        if created:
            publisher_user.set_password('testpass123')
            publisher_user.save()
            self.stdout.write(
                self.style.SUCCESS('Created publisher user: publisher_tech')
            )
        if publisher1.owner != publisher_user:
            publisher1.owner = publisher_user
            publisher1.save()

        # Add journalists to publishers
        publisher1.journalists.add(journalist1)
        publisher2.journalists.add(journalist2)
        publisher1.editors.add(editor1)

        # Create sample articles
        article1, created = Article.objects.get_or_create(
            title='AI Healthcare Assistant: Diagnosis, Medication Reminders, '
                  'and Health Chatbot',
            defaults={
                'content': (
                    'A comprehensive AI healthcare assistant has been '
                    'developed that revolutionizes patient care through '
                    'three key features: intelligent diagnosis assistance, '
                    'smart medication reminders, and an AI-powered health '
                    'chatbot. This innovative system uses advanced machine '
                    'learning algorithms to analyze symptoms, provide '
                    'preliminary health assessments, and help patients '
                    'manage their medications effectively. The AI chatbot '
                    'component offers 24/7 health guidance, answering '
                    'common medical questions and providing personalized '
                    'health recommendations based on individual patient '
                    'profiles and medical history.'
                ),
                'summary': (
                    'Comprehensive AI healthcare assistant featuring '
                    'diagnosis assistance, medication reminders, and '
                    'intelligent health chatbot for 24/7 patient support.'
                ),
                'author': journalist1,
                'publisher': publisher1,
                'category': tech_category,
                'status': 'published',
                'is_approved': True
            }
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    'Created article: AI Healthcare Assistant...'
                )
            )

        article2, created = Article.objects.get_or_create(
            title='Global Climate Summit Reaches Historic Agreement',
            defaults={
                'content': 'World leaders have reached a historic agreement '
                           'on climate change at the latest global summit. '
                           'The agreement includes ambitious targets for '
                           'reducing carbon emissions and transitioning to '
                           'renewable energy sources.',
                'summary': 'Historic climate agreement reached with ambitious '
                           'emission reduction targets.',
                'author': journalist2,
                'publisher': publisher2,
                'category': world_category,
                'status': 'published',
                'is_approved': True
            }
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS('Created article: Global Climate Summit...')
            )

        # Create sample newsletter
        newsletter1, created = Newsletter.objects.get_or_create(
            title='Weekly Tech Roundup',
            defaults={
                'content': (
                    'This week in technology: AI breakthroughs, '
                    'new smartphone releases, and cybersecurity updates.'
                ),
                'author': journalist1,
                'publisher': publisher1
            }
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS('Created newsletter: Weekly Tech Roundup')
            )

        self.stdout.write(
            self.style.SUCCESS('Sample data creation completed successfully!')
        )

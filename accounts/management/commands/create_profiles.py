"""
Management command to create profiles for users that don't have one.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Profile

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates Profile objects for all users that don\'t have one'

    def handle(self, *args, **options):
        users_without_profile = User.objects.filter(profile__isnull=True)
        count = users_without_profile.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('All users already have profiles'))
            return
        
        for user in users_without_profile:
            Profile.objects.create(user=user)
            self.stdout.write(
                self.style.SUCCESS(f'Created profile for user: {user.username}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {count} profile(s)')
        )

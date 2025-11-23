from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile, Role

class Command(BaseCommand):
    help = "Seed default users with roles"

    def handle(self, *args, **kwargs):
        users_data = [
            {
                "username": "admin_user",
                "email": "admin@example.com",
                "password": "password123",
                "role": Role.ADMIN,
            },
            {
                "username": "staff_user",
                "email": "staff@example.com",
                "password": "password123",
                "role": Role.STAFF,
            },
            {
                "username": "approver1_user",
                "email": "approver1@example.com",
                "password": "password123",
                "role": Role.APPROVER_L1,
            },
            {
                "username": "approver2_user",
                "email": "approver2@example.com",
                "password": "password123",
                "role": Role.APPROVER_L2,
            },
            {
                "username": "finance_user",
                "email": "finance@example.com",
                "password": "password123",
                "role": Role.FINANCE,
            },
        ]

        for data in users_data:
            user, created = User.objects.get_or_create(
                username=data["username"],
                defaults={"email": data["email"]}
            )

            if created:
                user.set_password(data["password"])
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created user: {user.username}"))
            else:
                self.stdout.write(self.style.WARNING(f"User {user.username} already exists"))

            # Ensure profile exists
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.role = data["role"]
            profile.save()

        self.stdout.write(self.style.SUCCESS("User seeding completed."))

import factory
from django.contrib.auth import get_user_model

from apps.accounts.models import DoctorProfile, RegistrationStatus, Role

User = get_user_model()


class AdminUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"admin{n}")
    email = factory.Sequence(lambda n: f"admin{n}@example.com")
    role = Role.ADMIN
    is_active = True
    is_staff = True

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        self.set_password(extracted or "AdminPass123!")
        if create:
            self.save()


class DoctorUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"doctor{n}")
    email = factory.Sequence(lambda n: f"doctor{n}@example.com")
    role = Role.DOCTOR
    is_active = True

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        self.set_password(extracted or "DoctorPass123!")
        if create:
            self.save()


class DoctorProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DoctorProfile

    user = factory.SubFactory(DoctorUserFactory)
    license_number = factory.Sequence(lambda n: f"LIC-{n:05d}")
    specialization = "Neurology"
    phone_number = "+1-555-0100"
    registration_status = RegistrationStatus.APPROVED

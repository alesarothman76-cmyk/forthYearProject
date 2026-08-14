from django.db import models

from apps.accounts.models import DoctorProfile
from apps.common.models import SoftDeleteModel


class Gender(models.TextChoices):
    MALE = "MALE", "Male"
    FEMALE = "FEMALE", "Female"


class Patient(SoftDeleteModel):
    # Unique globally - including against archived rows (see Section 5.1 /
    # Section 11 item 6: flagged as a possible future refinement, not
    # changed for now).
    national_id = models.CharField(max_length=64, unique=True, db_index=True)
    full_name = models.CharField(max_length=255, db_index=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=6, choices=Gender.choices)
    medical_history = models.TextField(blank=True)
    email = models.EmailField(blank=True)

    # Doctor accounts are only ever soft-deleted, so PROTECT should never
    # actually trigger in practice - it's a safety net.
    created_by_doctor = models.ForeignKey(DoctorProfile, on_delete=models.PROTECT, related_name="patients")

    class Meta:
        indexes = [
            models.Index(fields=["full_name"]),
            models.Index(fields=["national_id"]),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.national_id})"

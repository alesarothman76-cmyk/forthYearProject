from apps.patients.models import Patient


def create_patient(*, doctor, **fields):
    """Stamps created_by_doctor from the `doctor` argument, never from arbitrary kwargs."""
    fields.pop("created_by_doctor", None)
    return Patient.objects.create(created_by_doctor=doctor, **fields)


def update_patient(*, patient, **fields):
    """
    Explicitly pops created_by_doctor and national_id before applying - so
    even if a caller passes them, they're silently ignored (not errored).
    """
    fields.pop("created_by_doctor", None)
    fields.pop("national_id", None)

    for key, value in fields.items():
        setattr(patient, key, value)
    patient.save()
    return patient


def archive_patient(*, patient):
    """Soft-delete via SoftDeleteModel."""
    patient.delete()
    return patient

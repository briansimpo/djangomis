from django.db import models
from djangospice.db.models import BaseModel

from apps.party.enums import BiometricModality, BiometricSubType
from .parties import Person


class BiometricSample(BaseModel):
    person = models.ForeignKey(Person, on_delete=models.CASCADE,  related_name='biometric_samples')
    
    # Classification
    modality = models.CharField(max_length=50, choices=BiometricModality.choices)
    subtype = models.CharField(max_length=50, choices=BiometricSubType.choices, default=BiometricSubType.DEFAULT)

    # Stores the mathematical template/array/blob used by matching algorithms
    template_blob = models.BinaryField(blank=True, null=True, help_text="The raw byte array, vector, or ISO standard template data.")
    
    # Stores the human-verifiable file (photo, signature image, audio recording)
    media_file = models.FileField(upload_to='biometrics/%Y/%m/%d/', blank=True, null=True, help_text="The physical image, photo, or audio file path stored securely.")
    
    # For complex structural data (like signature stroke velocity vectors or device logs)
    extended_metadata = models.JSONField(default=dict, blank=True, help_text="Vendor-specific metadata, device information, or pen-stroke telemetry.")

    # Compliance & Audit Trail
    is_active = models.BooleanField(default=True, help_text="Deactivate instead of deleting to preserve compliance audit trails.")
    hardware_vendor = models.CharField(max_length=255, blank=True, null=True)
    hardware_serial = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Biometric Sample"
        verbose_name_plural = "Biometric Samples"
        constraints = [models.UniqueConstraint(fields=["person", "modality", "subtype"], name="uniq_biometric_sample")]

    def __str__(self):
        return f"{self.person} - {self.modality} ({self.subtype})"
    
    
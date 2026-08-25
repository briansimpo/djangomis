from django.db import models
from django.utils.translation import gettext_lazy as _


class PartyType(models.TextChoices):
    PERSON = "PERSON", _("Person")
    ORGANIZATION = "ORGANIZATION", _("Organization")
    GROUP = "GROUP", _("Group")


class BiometricModality(models.TextChoices):
	FACE = 'FACE', _('Facial Recognition')
	FINGERPRINT = 'FINGERPRINT', _('Fingerprint Scan')
	IRIS = 'IRIS', _('Iris Scan')
	VOICE = 'VOICE', _('Voiceprint')
	SIGNATURE = 'SIGNATURE', _('Digital Signature')
 

class BiometricSubType(models.TextChoices):
	# Fingers
	RIGHT_INDEX = 'RIGHT_INDEX', _('Right Index Finger')
	RIGHT_THUMB = 'RIGHT_THUMB', _('Right Thumb')
	LEFT_INDEX = 'LEFT_INDEX', _('Left Index Finger')
	LEFT_THUMB = 'LEFT_THUMB', _('Left Thumb')
	# Eyes
	LEFT_IRIS = 'LEFT_IRIS', _('Left Iris')
	RIGHT_IRIS = 'RIGHT_IRIS', _('Right Iris')
	# Face/Other
	FRONT_VIEW = 'FRONT_VIEW', _('Front Facial Profile')
	ANGLED_VIEW = 'ANGLED_VIEW', _('Angled Facial Profile')
	PRIMARY_SIG = 'PRIMARY_SIG', _('Primary Handwritten Signature')
	DEFAULT = 'DEFAULT', _('Standard/Default Sample')


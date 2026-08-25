from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from apps.workforce.models import Workstream, WorkstreamType


class WorkstreamMixin(models.Model):
    """
    Abstract mixin that automatically provisions, syncs, and archives a 
    workforce Workstream hub based on the lifecycle of the inheriting model.
    """
    workstream = models.OneToOneField(
        Workstream,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s",
        verbose_name=_("Governing Workstream Hub")
    )

    class Meta:
        abstract = True

    def get_workstream_name(self) -> str:
        """Defines the name of the Workstream. Defaults to the string representation."""
        return f"HUB: {str(self)}"

    def get_workstream_type_name(self) -> str:
        """Defines the category of the Workstream. Defaults to the model's verbose name."""
        return f"{self._meta.verbose_name.title()} Hub"

    def is_workstream_active(self) -> bool:
        """Defines whether the Workstream should accept workers. Defaults to True."""
        return True

    @transaction.atomic
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        
        # 1. Evaluate current state from hooks
        expected_name = self.get_workstream_name()
        expected_active = self.is_workstream_active()

        # 2. Provisioning: If brand new and no hub exists, build one.
        if is_new and not getattr(self, 'workstream_id', None):
            ws_type, _ = WorkstreamType.objects.get_or_create(
                name=self.get_workstream_type_name()
            )
            self.workstream = Workstream.objects.create(
                name=expected_name,
                workstream_type=ws_type,
                is_active=expected_active,
                metadata={"auto_provisioned_by": self._meta.model_name}
            )

        # 3. Save the entity
        super().save(*args, **kwargs)

        # 4. Syncing: If an existing entity changes, sync the hub.
        if not is_new and self.workstream:
            fields_to_update = []
            
            if self.workstream.name != expected_name:
                self.workstream.name = expected_name
                fields_to_update.append('name')
                
            if self.workstream.is_active != expected_active:
                self.workstream.is_active = expected_active
                fields_to_update.append('is_active')

            if fields_to_update:
                self.workstream.save(update_fields=fields_to_update)

    @transaction.atomic
    def delete(self, *args, **kwargs):
        """
        Soft-closes the Workstream to preserve HR/Deployment history 
        if the operational entity is hard-deleted.
        """
        if getattr(self, 'workstream', None) and self.workstream.is_active:
            self.workstream.is_active = False
            self.workstream.metadata["archived_reason"] = f"Governing {self._meta.verbose_name} was deleted."
            self.workstream.save(update_fields=['is_active', 'metadata'])
            
        super().delete(*args, **kwargs)
        

class WorkforceScopeMixin:
    """
    Mixin for Class-Based Views to automatically scope 
    data to the user's workforce hierarchy and Org Unit descendants.
    """
    def get_queryset(self):
        # 1. Get the base queryset from the view
        queryset = super().get_queryset()
        
        # 2. Check if the model has our custom WorkforceManager
        if not hasattr(queryset, 'authorized'):
            raise AttributeError(
                f"The model {queryset.model.__name__} does not use WorkforceManager. "
                "Ensure it is assigned to 'objects' in the model definition."
            )
        
        # 3. Apply the authorization scope using the request's workforce context
        return queryset.authorized(self.request)
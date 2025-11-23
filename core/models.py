from django.db import models
from django.utils import timezone

class AgreementType(models.Model):
    """Types of agreements available"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True)  # emoji or icon class
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return self.name


class Agreement(models.Model):
    """Main agreement model"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('reflection', 'In Reflection'),
        ('review', 'Under Review'),
        ('signed', 'Signed'),
        ('completed', 'Completed'),
    ]
    
    # Basic info
    agreement_type = models.ForeignKey(AgreementType, on_delete=models.CASCADE)
    participants = models.TextField(help_text="Names of participants")
    
    # Content
    conversation_history = models.JSONField(default=list, blank=True)
    agreement_text = models.TextField(blank=True)
    edited_text = models.TextField(blank=True, help_text="User edited version")
    
    # Metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    session_key = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    signed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Exhibition data
    is_archived = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.agreement_type.name} - {self.participants[:50]}"
    
    def get_final_text(self):
        """Returns edited text if available, otherwise original"""
        return self.edited_text if self.edited_text else self.agreement_text


class Photo(models.Model):
    """Photo of signing moment"""
    agreement = models.OneToOneField(Agreement, on_delete=models.CASCADE, related_name='photo')
    image = models.ImageField(upload_to='signing_photos/%Y/%m/')
    uploaded_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Photo for {self.agreement.id}"
from django import forms
from .models import Article
from django.core.exceptions import ValidationError
from django.utils.timezone import now

class ArticleFormPage1(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'subtitle', 'content', 'email']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 10:
            raise ValidationError("Title must be at least 10 characters long.")
        return title

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email or '@' not in email:
            raise ValidationError("Enter a valid email address.")
        return email


class ArticleFormPage2(forms.ModelForm):
    agree_to_terms = forms.BooleanField(required=True, label="I agree to the terms and conditions")

    class Meta:
        model = Article
        fields = ['image', 'tags', 'category', 'publish_date']

    def clean_publish_date(self):
        publish_date = self.cleaned_data.get('publish_date')
        if publish_date and publish_date <= now().date():
            raise ValidationError("Publish date must be a future date.")
        return publish_date

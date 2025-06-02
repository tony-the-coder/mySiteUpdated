# portfolio_app/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import (
    ContactInquiry,
    PortfolioProject, PortfolioImage, PortfolioCategory,
    BlogPost, BlogCategory
    # ActivityLog # Optional
)
# Import the new widget for CKEditor 5
from django_ckeditor_5.widgets import CKEditor5Widget
from django.db.models import Max

# --- Contact Form ---
class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactInquiry
        fields = ['name', 'email', 'phone_number', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': ' ',
                                           'class': 'peer block w-full appearance-none border-0 border-b-2 border-gray-300 bg-transparent py-2.5 px-0 text-sm text-gray-900 focus:border-accent focus:outline-none focus:ring-0'}),
            'email': forms.EmailInput(attrs={'placeholder': ' ',
                                             'class': 'peer block w-full appearance-none border-0 border-b-2 border-gray-300 bg-transparent py-2.5 px-0 text-sm text-gray-900 focus:border-accent focus:outline-none focus:ring-0'}),
            'phone_number': forms.TextInput(attrs={'placeholder': ' ',
                                                   'class': 'peer block w-full appearance-none border-0 border-b-2 border-gray-300 bg-transparent py-2.5 px-0 text-sm text-gray-900 focus:border-accent focus:outline-none focus:ring-0'}),
            'subject': forms.TextInput(attrs={'placeholder': ' ',
                                              'class': 'peer block w-full appearance-none border-0 border-b-2 border-gray-300 bg-transparent py-2.5 px-0 text-sm text-gray-900 focus:border-accent focus:outline-none focus:ring-0'}),
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': ' ',
                                             'class': 'peer block w-full appearance-none border-0 border-b-2 border-gray-300 bg-transparent py-2.5 px-0 text-sm text-gray-900 focus:border-accent focus:outline-none focus:ring-0'}),
        }

# --- Staff Form for Managing Coding Projects (PortfolioProject model) ---
class StaffPortfolioProjectForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=PortfolioCategory.objects.filter(is_active=True).order_by('name'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select one or more relevant categories/tech stacks."
    )
    # Use CKEditor5Widget for the 'details' field
    details = forms.CharField(
        widget=CKEditor5Widget(config_name='default'), # Use 'default' or another config from settings.py
        required=False,
        help_text="Detailed description: project goals, challenges, solutions, your role."
    )
    technologies_used = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Comma-separated, e.g., Python, Django, React, Vite'}),
        required=False,
        help_text="Comma-separated list of key technologies."
    )

    class Meta:
        model = PortfolioProject
        fields = [
            'title', 'categories', 'short_description', 'details',
            'technologies_used', 'github_url', 'live_demo_url',
            'featured_image', 'status', 'year_completed',
            'order', 'is_active',
        ]
        # No need to define widget for 'details' here if already done above for the field
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input block w-full mt-1 rounded-md shadow-sm border-gray-300 focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 text-gray-700'}),
            'short_description': forms.Textarea(attrs={'rows': 3,
                                                       'class': 'form-textarea block w-full mt-1 rounded-md shadow-sm border-gray-300 focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 text-gray-700'}),
            'github_url': forms.URLInput(attrs={
                'class': 'form-input block w-full mt-1 rounded-md shadow-sm border-gray-300 focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 text-gray-700',
                'placeholder': 'https://github.com/yourusername/yourproject'}),
            'live_demo_url': forms.URLInput(attrs={
                'class': 'form-input block w-full mt-1 rounded-md shadow-sm border-gray-300 focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 text-gray-700',
                'placeholder': 'https://yourprojectdemo.com'}),
            'featured_image': forms.ClearableFileInput(attrs={'class': 'form-input block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'}),
            'status': forms.Select(attrs={
                'class': 'form-select block w-full mt-1 rounded-md shadow-sm border-gray-300 focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 text-gray-700'}),
            'year_completed': forms.NumberInput(attrs={
                'class': 'form-input block w-full mt-1 rounded-md shadow-sm border-gray-300 focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 text-gray-700'}),
            'order': forms.NumberInput(attrs={
                'class': 'form-input block w-full mt-1 rounded-md shadow-sm border-gray-300 focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 text-gray-700'}),
            'is_active': forms.CheckboxInput(
                attrs={'class': 'form-checkbox h-5 w-5 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'order' in self.fields and not self.instance.pk:
            try:
                max_order = PortfolioProject.objects.aggregate(Max('order'))['order__max']
                self.fields['order'].initial = (max_order or 0) + 1
            except Exception:
                 self.fields['order'].initial = 1
        self.fields['details'].required = False
        self.fields['short_description'].required = False
        self.fields['featured_image'].required = False
        self.fields['year_completed'].required = False
        self.fields['technologies_used'].required = False # Make sure this is also set if applicable

# You might also want a form for BlogPost to use CKEditor 5
class BlogPostForm(forms.ModelForm): # Example name, use in admin.py if needed
    content = forms.CharField(
        widget=CKEditor5Widget(config_name='default'), # Use your config name
        required=False
    )
    excerpt = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    class Meta:
        model = BlogPost
        fields = ['title', 'category', 'status', 'content', 'excerpt', 'featured_image', 'author', 'published_date', 'is_active']
        # Add widgets for other fields if needed for styling
        widgets = {
             'title': forms.TextInput(attrs={'class': 'form-input block w-full mt-1 rounded-md shadow-sm border-gray-300 focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 text-gray-700'}),
             'category': forms.Select(attrs={'class': 'form-select block w-full mt-1 rounded-md shadow-sm border-gray-300 focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 text-gray-700'}),
             'status': forms.Select(attrs={'class': 'form-select block w-full mt-1 rounded-md shadow-sm border-gray-300 focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 text-gray-700'}),
             'featured_image': forms.ClearableFileInput(attrs={'class': 'form-input block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'}),
             'author': forms.Select(attrs={'class': 'form-select block w-full mt-1 rounded-md shadow-sm border-gray-300 focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 text-gray-700'}),
             'published_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-input block w-full mt-1 rounded-md shadow-sm border-gray-300 focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 text-gray-700'}),
             'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500'}),
        }


# --- Form for Managing Portfolio Images (in staff portal formset) ---
class PortfolioImageManagementForm(forms.ModelForm):
    class Meta:
        model = PortfolioImage
        fields = ['caption', 'order']
        widgets = {
            'caption': forms.TextInput(attrs={
                'class': 'form-input w-full text-sm py-1 px-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-gray-700',
                'placeholder': 'Image caption (optional)'}),
            'order': forms.NumberInput(attrs={
                'class': 'form-input w-24 text-sm py-1 px-2 text-center border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-gray-700',
                'placeholder': 'Order'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['caption'].required = False
        if 'order' in self.fields and self.fields['order'].initial is None and not (self.instance and self.instance.pk):
            self.fields['order'].initial = 0


# --- Staff User Profile Edit Form ---
class StaffUserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-input block w-full mt-1 rounded-md shadow-sm border-gray-300 focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 text-gray-700'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input block w-full mt-1 rounded-md shadow-sm border-gray-300 focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 text-gray-700'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input block w-full mt-1 rounded-md shadow-sm border-gray-300 focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 text-gray-700'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
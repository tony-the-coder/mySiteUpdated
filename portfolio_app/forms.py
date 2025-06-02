# portfolio_app/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import (
    ContactInquiry,
    PortfolioProject, PortfolioImage, PortfolioCategory,
    BlogPost, BlogCategory # Assuming Blog models are kept
    # ActivityLog # Optional, uncomment if you keep this model
)
from ckeditor.widgets import CKEditorWidget
from django.db.models import Max

# --- Contact Form (For public site, to be potentially handled by React later) ---
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
    # Use CheckboxSelectMultiple for better UX with ManyToManyField
    categories = forms.ModelMultipleChoiceField(
        queryset=PortfolioCategory.objects.filter(is_active=True).order_by('name'),
        widget=forms.CheckboxSelectMultiple,
        required=False, # Or True, depending on if every project must have a category
        help_text="Select one or more relevant categories/tech stacks."
    )
    details = forms.CharField(widget=CKEditorWidget(config_name='default'), required=False,
                              help_text="Detailed description: project goals, challenges, solutions, your role.")
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
            'featured_image', 'status', 'year_completed', # year_completed is optional
            'order', 'is_active',
        ]
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
        # Set initial order for new projects
        if 'order' in self.fields and not self.instance.pk:
            try:
                max_order = PortfolioProject.objects.aggregate(Max('order'))['order__max']
                self.fields['order'].initial = (max_order or 0) + 1
            except Exception: # Handles case where table might not exist yet or other DB issues
                 self.fields['order'].initial = 1
        # Ensure 'details' is not required if blank=True in model, same for others
        self.fields['details'].required = False
        self.fields['short_description'].required = False
        self.fields['featured_image'].required = False
        self.fields['year_completed'].required = False


# --- Form for Managing Portfolio Images (in staff portal formset) ---
class PortfolioImageManagementForm(forms.ModelForm):
    class Meta:
        model = PortfolioImage
        fields = ['caption', 'order'] # Image file itself is uploaded in StaffPortfolioProjectForm or managed in admin for existing
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
        model = User # Target Django's built-in User model
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
        self.fields['email'].required = True # Make email required


# --- Forms for models you are removing (Commented out) ---
# If you decide you don't need Customer, Project (internal), Expense, CostItem, ActivityLog
# for your portfolio, you can remove these forms and their model imports.

# class ExpenseForm(forms.ModelForm):
#     # ... (original ExpenseForm code from your file) ...
#     pass

# class ActivityLogForm(forms.ModelForm):
#     # ... (original ActivityLogForm code from your file) ...
#     pass

# You would also remove imports for: Expense, Project, CustomerDocument, CostItem, ActivityLog
# if these models are fully removed from your models.py.
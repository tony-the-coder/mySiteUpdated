# portfolio_app/forms.py
from django import forms
from django.contrib.auth.models import User # Import Django's User model
from .models import (
    ContactInquiry, Expense, Project, CustomerDocument, CostItem, ActivityLog,
    PortfolioProject, PortfolioImage, PortfolioCategory
)
from ckeditor.widgets import CKEditorWidget
from django.db.models import Max


# --- Existing Contact Form ---
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


# --- Existing Expense Form ---
class ExpenseForm(forms.ModelForm):
    receipt_upload = forms.FileField(required=False, label="Upload New Receipt/Document",
                                     help_text="Upload a new file for this expense. This will create a new Customer Document record and link it.")

    class Meta:
        model = Expense
        fields = ['project', 'vendor', 'category', 'expense_date', 'amount', 'draw_number', 'description',
                  'invoice_number', 'is_active']
        # Basic styling for select and date input, you can expand this
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select block w-full mt-1 rounded-md shadow-sm border-gray-300 focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 text-gray-700'}),
            'vendor': forms.Select(attrs={'class': 'form-select block w-full mt-1 rounded-md shadow-sm border-gray-300 focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 text-gray-700'}),
            'category': forms.Select(attrs={'class': 'form-select block w-full mt-1 rounded-md shadow-sm border-gray-300 focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 text-gray-700'}),
            'expense_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input block w-full mt-1 rounded-md shadow-sm border-gray-300 focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 text-gray-700'}),
            'amount': forms.NumberInput(attrs={'class': 'form-input block w-full mt-1 rounded-md shadow-sm border-gray-300 focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 text-gray-700'}),
            'draw_number': forms.Select(attrs={'class': 'form-select block w-full mt-1 rounded-md shadow-sm border-gray-300 focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 text-gray-700'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-textarea block w-full mt-1 rounded-md shadow-sm border-gray-300 focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 text-gray-700'}),
            'invoice_number': forms.TextInput(attrs={'class': 'form-input block w-full mt-1 rounded-md shadow-sm border-gray-300 focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 text-gray-700'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500'}),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project'].queryset = Project.objects.filter(is_active=True).order_by('project_name')


# --- Existing ActivityLog Form ---
class ActivityLogForm(forms.ModelForm):
    class Meta:
        model = ActivityLog
        fields = ['note_type', 'note']
        widgets = {
            'note_type': forms.Select(attrs={
                'class': 'form-select mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-gray-900'}),
            'note': forms.Textarea(attrs={'rows': 3,
                                          'class': 'form-textarea mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-gray-900',
                                          'placeholder': 'Enter note details here...'}),
        }
        labels = {'note_type': 'Type of Note', 'note': 'Note Content', }


# --- StaffPortfolioProjectForm (For the new two-step bulk upload workflow) ---
class StaffPortfolioProjectForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=PortfolioCategory.objects.filter(is_active=True).order_by('name'), # Ensure only active categories
        widget=forms.Select(attrs={
            'class': 'form-select block w-full mt-1 rounded-md shadow-sm border-gray-300 focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 text-gray-700'}),
        required=True
    )
    details = forms.CharField(widget=CKEditorWidget(config_name='default'), required=False)

    class Meta:
        model = PortfolioProject
        fields = [
            'title', 'category', 'short_description', 'details', 'is_active',
            'location', 'year_completed', 'square_footage', 'status', 'order',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input block w-full mt-1 rounded-md shadow-sm border-gray-300 focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 text-gray-700'}),
            'short_description': forms.Textarea(attrs={'rows': 3,
                                                       'class': 'form-textarea block w-full mt-1 rounded-md shadow-sm border-gray-300 focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 text-gray-700'}),
            'is_active': forms.CheckboxInput(
                attrs={'class': 'form-checkbox h-5 w-5 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500'}),
            'location': forms.TextInput(attrs={
                'class': 'form-input block w-full mt-1 rounded-md shadow-sm border-gray-300 focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 text-gray-700'}),
            'year_completed': forms.NumberInput(attrs={
                'class': 'form-input block w-full mt-1 rounded-md shadow-sm border-gray-300 focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 text-gray-700'}),
            'square_footage': forms.NumberInput(attrs={
                'class': 'form-input block w-full mt-1 rounded-md shadow-sm border-gray-300 focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 text-gray-700'}),
            'status': forms.Select(attrs={
                'class': 'form-select block w-full mt-1 rounded-md shadow-sm border-gray-300 focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 text-gray-700'}),
            'order': forms.NumberInput(attrs={
                'class': 'form-input block w-full mt-1 rounded-md shadow-sm border-gray-300 focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 text-gray-700'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'order' in self.fields and not self.instance.pk: # Only set initial for new projects
            try:
                max_order = PortfolioProject.objects.aggregate(Max('order'))['order__max']
                self.fields['order'].initial = (max_order or 0) + 1
            except: # Handles case where table might not exist yet (e.g. first migration)
                 self.fields['order'].initial = 1


# --- PortfolioImageManagementForm (For the staff portal image management formset) ---
class PortfolioImageManagementForm(forms.ModelForm):
    class Meta:
        model = PortfolioImage
        fields = ['caption', 'order'] # Image field itself is not managed here, only its attributes
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


# --- NEW: Staff User Profile Edit Form ---
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
# portfolio_app/admin.py
from django.contrib import admin
from django import forms
from django.utils.html import mark_safe
from django.utils import timezone # Required for make_published action
from django.urls import reverse # For portfolio_project_link

from .models import (
    PortfolioCategory,
    PortfolioProject,
    PortfolioImage,
    BlogCategory,
    BlogPost,
    ContactInquiry,
    # ActivityLog # Optional: Uncomment to keep and register ActivityLog
)
# Import the new widget for CKEditor 5
from django_ckeditor_5.widgets import CKEditor5Widget

# --- Inlines ---
class PortfolioImageInline(admin.TabularInline):
    model = PortfolioImage
    extra = 1
    fields = ('image_preview', 'image', 'caption', 'order')
    readonly_fields = ('image_preview',)
    ordering = ('order',)
    verbose_name = "Coding Project Image"
    verbose_name_plural = "Coding Project Images"

    def image_preview(self, obj):
        return obj.image_preview() # Calls the method from models.py
    image_preview.short_description = 'Preview'

    class Media:
        js = ('js/admin_image_preview.js',) # Ensure this file is in your static/js/ directory


# --- Custom Forms for Admin ---
class PortfolioProjectAdminForm(forms.ModelForm):
    # Use CKEditor5Widget for the 'details' field
    details = forms.CharField(
        widget=CKEditor5Widget(config_name='default'), # UPDATED HERE
        required=False # Set required=False if blank=True in model
    )
    # If you want CKEditor for short_description too, you could configure a 'small' config in settings.py
    # short_description = forms.CharField(widget=CKEditor5Widget(config_name='small'), required=False)

    class Meta:
        model = PortfolioProject
        fields = '__all__'
        widgets = {
            'categories': forms.CheckboxSelectMultiple,
            'technologies_used': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Comma-separated, e.g., Python, Django, React'}),
        }

class BlogPostAdminForm(forms.ModelForm):
    # Use CKEditor5Widget for the 'content' field
    content = forms.CharField(
        widget=CKEditor5Widget(config_name='default'), # UPDATED HERE
        required=False
    )
    excerpt = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    class Meta:
        model = BlogPost
        fields = '__all__'

# --- ModelAdmins ---

@admin.register(PortfolioCategory)
class PortfolioCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'description')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    list_filter = ('is_active',)

@admin.register(PortfolioProject)
class PortfolioProjectAdmin(admin.ModelAdmin):
    form = PortfolioProjectAdminForm # Uses the updated form with CKEditor5Widget
    list_display = ('title', 'display_categories', 'is_active', 'order', 'github_url', 'live_demo_url', 'created_at')
    list_filter = ('categories', 'is_active', 'status')
    search_fields = ('title', 'short_description', 'details', 'technologies_used')
    list_editable = ('is_active', 'order')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [PortfolioImageInline]
    filter_horizontal = ('categories',)

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'categories', 'is_active', 'order', 'status', 'year_completed')
        }),
        ('Project URLs & Tech Stack', {
            'fields': ('github_url', 'live_demo_url', 'technologies_used')
        }),
        ('Visuals & Descriptions', {
            'fields': ('featured_image', 'short_description', 'details')
        }),
    )

    def display_categories(self, obj):
        return ", ".join([cat.name for cat in obj.categories.all()])
    display_categories.short_description = "Categories"


@admin.register(PortfolioImage)
class PortfolioImageAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'portfolio_project_link', 'caption', 'order', 'uploaded_at')
    list_filter = ('portfolio_project__title',)
    search_fields = ('caption', 'portfolio_project__title')
    list_editable = ('caption', 'order')
    list_per_page = 20
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        return obj.image_preview()
    image_preview.short_description = 'Image Preview'

    def portfolio_project_link(self, obj):
        if obj.portfolio_project:
            link = reverse("admin:portfolio_app_portfolioproject_change", args=[obj.portfolio_project.id])
            return mark_safe(f'<a href="{link}">{obj.portfolio_project.title}</a>')
        return None
    portfolio_project_link.short_description = 'Portfolio Project'
    portfolio_project_link.admin_order_field = 'portfolio_project'


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'description')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    list_filter = ('is_active',)

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    form = BlogPostAdminForm # Uses the updated form with CKEditor5Widget
    list_display = ('title', 'category', 'status', 'published_date', 'author_name', 'is_active')
    list_filter = ('status', 'category', 'is_active', 'author')
    search_fields = ('title', 'content', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_date'
    actions = ['make_published', 'make_draft']
    autocomplete_fields = ['author', 'category']

    def author_name(self, obj):
        if obj.author:
            return obj.author.get_full_name() or obj.author.username
        return None
    author_name.short_description = 'Author'
    author_name.admin_order_field = 'author'

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)

    def make_published(self, request, queryset):
        queryset.update(status=BlogPost.PUBLISHED, published_date=timezone.now())
    make_published.short_description = "Mark selected posts as Published"

    def make_draft(self, request, queryset):
        queryset.update(status=BlogPost.DRAFT)
    make_draft.short_description = "Mark selected posts as Draft"


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'status', 'submitted_at')
    list_filter = ('status', 'submitted_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name','email','phone_number','subject','message','submitted_at', 'updated_at')
    fields = ('name', 'email', 'phone_number', 'subject', 'message', 'status', 'internal_notes', 'submitted_at', 'updated_at')

# ... (Optional ActivityLogAdmin and comments about removed models remain the same) ...
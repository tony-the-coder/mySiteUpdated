# portfolio_app/admin.py
from django.contrib import admin
from django import forms
from django.utils.html import mark_safe
from django.utils import timezone # Required for make_published action

from .models import (
    PortfolioCategory,
    PortfolioProject,
    PortfolioImage,
    BlogCategory,
    BlogPost,
    ContactInquiry,
    # ActivityLog # Optional: Uncomment to keep and register ActivityLog
)
from ckeditor.widgets import CKEditorWidget

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

    # To enable the JS preview for newly added inline images before saving
    class Media:
        js = ('js/admin_image_preview.js',) # Ensure this file is in your static/js/ directory


# --- Custom Forms for Admin ---
class PortfolioProjectAdminForm(forms.ModelForm):
    details = forms.CharField(widget=CKEditorWidget(), required=False)
    # If you want to use CKEditor for short_description too, uncomment next line
    # short_description = forms.CharField(widget=CKEditorWidget(config_name='small'), required=False)


    class Meta:
        model = PortfolioProject
        fields = '__all__'
        widgets = {
            'categories': forms.CheckboxSelectMultiple, # Better UI for ManyToManyField
            'technologies_used': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Comma-separated, e.g., Python, Django, React'}),
        }

class BlogPostAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget(), required=False)
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
    form = PortfolioProjectAdminForm
    list_display = ('title', 'display_categories', 'is_active', 'order', 'github_url', 'live_demo_url', 'created_at')
    list_filter = ('categories', 'is_active', 'status') # Filter by categories (ManyToMany)
    search_fields = ('title', 'short_description', 'details', 'technologies_used')
    list_editable = ('is_active', 'order')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [PortfolioImageInline]
    filter_horizontal = ('categories',) # Better UI for ManyToMany relationship with PortfolioCategory

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
    form = BlogPostAdminForm
    list_display = ('title', 'category', 'status', 'published_date', 'author_name', 'is_active')
    list_filter = ('status', 'category', 'is_active', 'author')
    search_fields = ('title', 'content', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_date'
    actions = ['make_published', 'make_draft']
    autocomplete_fields = ['author', 'category'] # Makes selecting author and category easier

    def author_name(self, obj):
        if obj.author:
            return obj.author.get_full_name() or obj.author.username
        return None
    author_name.short_description = 'Author'
    author_name.admin_order_field = 'author'


    def save_model(self, request, obj, form, change):
        if not obj.author_id: # If author is not set (e.g. new post)
            obj.author = request.user # Default to current user
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
    # Make most fields read-only in the change view, only status and internal_notes editable
    readonly_fields = ('name', 'email', 'phone_number', 'subject', 'message', 'submitted_at', 'updated_at')
    fields = ('name', 'email', 'phone_number', 'subject', 'message', 'status', 'internal_notes', 'submitted_at', 'updated_at')


# Optional: If you decide to keep and repurpose ActivityLog for your portfolio
# from .models import ActivityLog
# @admin.register(ActivityLog)
# class ActivityLogAdmin(admin.ModelAdmin):
#     list_display = ('timestamp', 'author_display', 'note_type', 'note_snippet', 'related_object_link')
#     list_filter = ('note_type', 'timestamp', 'author')
#     search_fields = ('note', 'author__username') # Add other fields if needed
#     readonly_fields = ('timestamp', 'author')
#     list_per_page = 25
#
#     def note_snippet(self, obj):
#         return obj.note[:75] + ('...' if len(obj.note) > 75 else '')
#     note_snippet.short_description = 'Note'
#
#     def author_display(self, obj):
#         return obj.author.get_full_name() or obj.author.username if obj.author else 'N/A'
#     author_display.short_description = 'Author'
#
#     def related_object_link(self, obj):
#         # This part would need to be adapted if ActivityLog links to PortfolioProject instead of old Project/Customer
#         # For now, this is a placeholder as ActivityLog model might need to be refactored too
#         # if obj.project: # Assuming 'project' could be a PortfolioProject
#         #     link = reverse("admin:portfolio_app_portfolioproject_change", args=[obj.project.id])
#         #     return mark_safe(f'<a href="{link}">{obj.project}</a>')
#         # elif obj.customer: # If you keep a customer-like model
#         #     link = reverse("admin:portfolio_app_customer_change", args=[obj.customer.id])
#         #     return mark_safe(f'<a href="{link}">{obj.customer}</a>')
#         return "N/A"
#     related_object_link.short_description = 'Related To'

# --- Models from the original Lehman site that are now removed from models.py ---
# (and thus should NOT be registered here for 'portfolio_app')
# - Customer
# - Project (the internal construction project model)
# - ProjectImage (for the internal Project model)
# - Vendor
# - ExpenseCategory
# - CostItem
# - Expense
# - CustomerDocument
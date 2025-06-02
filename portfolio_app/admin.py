# portfolio_app/admin.py
from django.contrib import admin
from django import forms
from django.utils.html import mark_safe # For image preview method in model
from .models import (
    Customer, Project, Vendor, ExpenseCategory, CostItem, Expense,
    CustomerDocument, ProjectImage, PortfolioProject, PortfolioImage,
    BlogCategory, BlogPost, ContactInquiry, ActivityLog, PortfolioCategory # Ensure all needed models imported
)
# Import CKEditor widget
from ckeditor.widgets import CKEditorWidget

# --- Inlines ---
class PortfolioImageInline(admin.TabularInline): # Or admin.StackedInline for different layout
    model = PortfolioImage
    extra = 1 # Show 1 empty slot by default for adding new images
    fields = ('image_preview', 'image', 'caption', 'order') # Display preview first
    readonly_fields = ('image_preview',) # Make the preview field read-only in the form
    ordering = ('order',) # Order images by the 'order' field
    verbose_name = "Gallery Image"
    verbose_name_plural = "Gallery Images"

    # This method calls the image_preview method defined ON THE MODEL
    # It tells the admin how to display the read-only field
    def image_preview(self, obj):
        # obj here is an instance of PortfolioImage
        return obj.image_preview() # Calls the method from models.py
    image_preview.short_description = 'Image Preview' # Column header

    # --- ADD THIS MEDIA CLASS ---
    # This tells the admin to load our custom JavaScript on pages where this inline is used
    class Media:
        # Path is relative to your STATIC_URL (e.g., /static/js/admin_image_preview.js)
        js = ('js/admin_image_preview.js',)
    # --- END MEDIA CLASS ---


# --- Custom Forms for Admin ---
class PortfolioProjectAdminForm(forms.ModelForm):
    # Use CKEditor Rich Text Editor widget for the 'details' field
    # Make sure the field name 'details' matches your PortfolioProject model
    details = forms.CharField(widget=CKEditorWidget())
    class Meta:
        model = PortfolioProject
        fields = '__all__' # Include all fields from the model in this form

# --- ModelAdmins ---
# Register each model with the admin site, customizing display as needed

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'email', 'telephone_number', 'is_active')
    search_fields = ('last_name', 'first_name', 'email')
    list_filter = ('is_active',)

@admin.register(Project) # This is the INTERNAL Project model
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'customer', 'status', 'start_date', 'estimated_completion_date', 'is_active')
    list_filter = ('status', 'is_active', 'customer')
    search_fields = ('project_name', 'customer__first_name', 'customer__last_name')
    prepopulated_fields = {'slug': ('project_name',)}
    # You could potentially add ProjectImageInline here if needed for internal projects

@admin.register(PortfolioProject) # This is the PUBLIC Portfolio model
class PortfolioProjectAdmin(admin.ModelAdmin):
    form = PortfolioProjectAdminForm # Use the form with CKEditor for the 'details' field
    list_display = ('title', 'category', 'is_active', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('title', 'short_description', 'details')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [PortfolioImageInline] # Manage gallery images directly here

@admin.register(PortfolioCategory)
class PortfolioCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(PortfolioImage)
class PortfolioImageAdmin(admin.ModelAdmin):
    # This admin is for managing *all* gallery images directly if needed
    # It also benefits from the preview
    list_display = ('image_preview', 'portfolio_project', 'caption', 'order', 'uploaded_at')
    list_filter = ('portfolio_project',)
    search_fields = ('caption', 'portfolio_project__title')
    list_editable = ('caption', 'order') # Allow quick edits in the list view
    list_per_page = 20
    readonly_fields = ('image_preview',) # Show preview here too

    # Uses the method defined in the PortfolioImage model
    def image_preview(self, obj):
        return obj.image_preview()
    image_preview.short_description = 'Image Preview'


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'email', 'phone_number', 'is_active')
    search_fields = ('name', 'contact_person', 'email')
    list_filter = ('is_active',)

@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)

@admin.register(CostItem)
class CostItemAdmin(admin.ModelAdmin):
    list_display = ('project', 'category', 'description', 'budgeted_amount', 'is_active')
    list_filter = ('project', 'category', 'is_active')
    search_fields = ('description', 'project__project_name', 'category__name')
    list_per_page = 25

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('project', 'vendor', 'category', 'amount', 'expense_date', 'draw_number', 'is_active')
    list_filter = ('project', 'vendor', 'category', 'expense_date', 'draw_number', 'is_active')
    search_fields = ('description', 'vendor__name', 'project__project_name', 'category__name', 'invoice_number')
    list_per_page = 25

@admin.register(CustomerDocument)
class CustomerDocumentAdmin(admin.ModelAdmin):
    list_display = ('customer', 'project', 'document_type', 'description', 'get_filename', 'uploaded_at', 'is_active')
    list_filter = ('document_type', 'customer', 'project', 'is_active')
    search_fields = ('description', 'original_filename', 'customer__first_name', 'customer__last_name', 'project__project_name')
    readonly_fields = ('original_filename', 'uploaded_at', 'get_filename')
    list_per_page = 25

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'published_date', 'author', 'is_active')
    list_filter = ('status', 'category', 'is_active', 'author')
    search_fields = ('title', 'content', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_date'
    # Consider adding CKEditor here later for the 'content' field
    # formfield_overrides = { models.TextField: {'widget': CKEditorWidget} }

@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'status', 'submitted_at')
    list_filter = ('status', 'submitted_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('submitted_at', 'updated_at')

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'author_display', 'note_type', 'customer', 'project', 'note_snippet')
    list_filter = ('note_type', 'timestamp', 'author', 'customer', 'project')
    search_fields = ('note', 'customer__first_name', 'customer__last_name', 'project__project_name', 'author__username')
    readonly_fields = ('timestamp','author', 'customer', 'project') # Make these read-only on the change form
    list_per_page = 25

    # Helper methods for display
    def note_snippet(self, obj):
        return obj.note[:50] + ('...' if len(obj.note) > 50 else '')
    note_snippet.short_description = 'Note (Snippet)'

    def author_display(self, obj):
        # Display full name or username, handle possibility of no author
        return obj.author.get_full_name() or obj.author.username if obj.author else 'N/A'
    author_display.short_description = 'Author'

# Register ProjectImage only if needed for direct admin access - optional
# admin.site.register(ProjectImage)
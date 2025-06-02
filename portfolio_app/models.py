# portfolio_apps/models.py
import os
from django.db import models
from django.db.models import Sum
from django.utils import timezone
from django.conf import settings
from django.utils.text import slugify
from django.utils.html import mark_safe
from django.urls import reverse


# --- Helper Functions ---

def get_document_upload_path(instance, filename):
    """ Determine upload path for CustomerDocument """
    customer_part = f"customer_{instance.customer.id}" if instance.customer else "customer_misc"
    project_part = f"project_{instance.project.id}" if instance.project else "project_general"
    safe_filename = os.path.basename(filename)
    return f'uploads/customer_docs/{customer_part}/{project_part}/{safe_filename}'


def get_portfolio_image_upload_path(instance, filename):
    """ Creates a path like: portfolio_gallery/project_slug/filename.ext """
    # Ensure instance.portfolio_project exists and has a slug
    project_slug = "unassigned"
    if hasattr(instance, 'portfolio_project') and instance.portfolio_project and hasattr(instance.portfolio_project,
                                                                                         'slug') and instance.portfolio_project.slug:
        project_slug = instance.portfolio_project.slug
    elif hasattr(instance, 'project') and instance.project and hasattr(instance.project,
                                                                       'slug') and instance.project.slug:  # Fallback if used with internal Project
        project_slug = instance.project.slug

    safe_filename = os.path.basename(filename)
    return f'portfolio_gallery/{project_slug}/{safe_filename}'


# --- Model Definitions ---

class Customer(models.Model):
    # ... (your Customer model fields - keep as is) ...
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, unique=True)
    telephone_number = models.CharField(max_length=25, blank=True)
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    secondary_first_name = models.CharField(max_length=100, blank=True)
    secondary_last_name = models.CharField(max_length=100, blank=True)
    secondary_email = models.EmailField(max_length=254, blank=True)
    secondary_telephone_number = models.CharField(max_length=25, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
        ordering = ['last_name', 'first_name']


class PortfolioCategory(models.Model):
    # ... (your PortfolioCategory model fields - keep as is) ...
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            original_slug = self.slug
            counter = 1
            while PortfolioCategory.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class PortfolioCategory(models.Model):
        # ... other fields ...
        def get_absolute_url(self):
            return reverse('portfolio_app:portfolio_projects_by_category', kwargs={'category_slug': self.slug})

    def get_representative_image_url(self):
        first_project_with_image = self.portfolio_projects.filter(
            is_active=True,
            featured_image__isnull=False
        ).exclude(featured_image__exact='').order_by('order', '-created_at').first()  # Added order here too

        if first_project_with_image and first_project_with_image.featured_image:
            return first_project_with_image.featured_image.url
        return None

    class Meta:
        verbose_name = "Portfolio Category"
        verbose_name_plural = "Portfolio Categories"
        ordering = ['name']


class Project(models.Model):  # Internal Project Tracking
    # ... (your Project model fields - keep as is) ...
    STATUS_CHOICES = [
        ('PLAN', 'Planning'), ('ACTIVE', 'Active'), ('HOLD', 'On Hold'), ('COMP', 'Completed'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='projects')
    portfolio_category = models.ForeignKey(PortfolioCategory, on_delete=models.SET_NULL, null=True, blank=True,
                                           related_name='internal_projects',
                                           verbose_name="Portfolio Category (Optional Internal)")
    project_name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=210, unique=True, blank=True,
                            help_text="URL-friendly name. Auto-generated if blank.")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PLAN', db_index=True)
    short_description = models.CharField(max_length=255, blank=True, help_text="Internal brief description.")
    full_description = models.TextField(blank=True, help_text="Internal detailed description.")
    build_address_line1 = models.CharField(max_length=255, blank=True)
    build_address_line2 = models.CharField(max_length=255, blank=True)
    build_city = models.CharField(max_length=100, blank=True)
    build_state = models.CharField(max_length=50, blank=True)
    build_zip_code = models.CharField(max_length=20, blank=True)
    total_budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    estimated_completion_date = models.DateField(null=True, blank=True)
    date_completed = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Project (Internal)"
        verbose_name_plural = "Projects (Internal)"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.project_name)
            original_slug = self.slug;
            counter = 1
            while Project.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{original_slug}-{counter}";
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.project_name

    def calculate_actual_cost(self):
        total = self.expenses.filter(is_active=True).aggregate(total=Sum('amount'))['total']
        return total if total is not None else Decimal('0.00')

    @property
    def actual_cost(self):
        return self.calculate_actual_cost()

    @property
    def budget_variance(self):
        if self.total_budget is None: return None
        budget = self.total_budget if isinstance(self.total_budget, Decimal) else Decimal(str(self.total_budget))
        return budget - self.actual_cost


class ProjectImage(models.Model):  # Images ONLY for INTERNAL Project view
    # ... (your ProjectImage model fields - keep as is) ...
    project = models.ForeignKey(Project, related_name='internal_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='project_images_internal/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'uploaded_at'];
        verbose_name = "Internal Project Image";
        verbose_name_plural = "Internal Project Images"

    def __str__(self): return f"Internal image for {self.project.project_name}"


class Vendor(models.Model):
    # ... (your Vendor model fields - keep as is) ...
    name = models.CharField(max_length=200, unique=True);
    contact_person = models.CharField(max_length=150, blank=True)
    email = models.EmailField(max_length=254, blank=True);
    phone_number = models.CharField(max_length=25, blank=True)
    address_line1 = models.CharField(max_length=255, blank=True);
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True);
    state = models.CharField(max_length=50, blank=True);
    zip_code = models.CharField(max_length=20, blank=True)
    account_number = models.CharField(max_length=50, blank=True);
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False);
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self): return self.name

    class Meta: verbose_name_plural = "Vendors"; ordering = ['name']


class ExpenseCategory(models.Model):
    # ... (your ExpenseCategory model fields - keep as is) ...
    name = models.CharField(max_length=150, unique=True);
    description = models.TextField(blank=True);
    is_active = models.BooleanField(default=True, db_index=True)

    def __str__(self): return self.name

    class Meta: verbose_name = "Expense Category"; verbose_name_plural = "Expense Categories"; ordering = ['name']


class CustomerDocument(models.Model):
    # ... (your CustomerDocument model fields - keep as is) ...
    DOCUMENT_TYPE_CHOICES = [('RECEIPT', 'Receipt'), ('CONTRACT', 'Contract'), ('WARRANTY', 'Warranty'),
                             ('PLAN', 'Plan/Blueprint'), ('PHOTO', 'Photo'), ('OTHER', 'Other')]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True,
                                related_name='customer_documents')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True,
                                 related_name='customer_documents')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='uploaded_documents')
    document_type = models.CharField(max_length=10, choices=DOCUMENT_TYPE_CHOICES, default='OTHER')
    description = models.CharField(max_length=255, blank=True, default='');
    original_filename = models.CharField(max_length=255, editable=False, blank=True)
    file = models.FileField(upload_to=get_document_upload_path, null=True, blank=True);
    uploaded_at = models.DateTimeField(default=timezone.now, editable=False)
    is_active = models.BooleanField(default=True, db_index=True)

    def save(self, *args, **kwargs):
        if not self.pk and self.file and not self.original_filename: self.original_filename = os.path.basename(
            self.file.name)
        if self.project and not self.customer: self.customer = self.project.customer
        super().save(*args, **kwargs)

    def get_filename(self):
        return os.path.basename(self.file.name) if self.file else self.original_filename or ""

    def __str__(self):
        display_name = self.description or self.get_filename() or "[No Identifier]";
        context_parts = []
        if self.project: context_parts.append(f"for project {self.project.project_name}")
        if self.customer and not self.project: context_parts.append(f"for customer {self.customer}")
        if not context_parts: context_parts.append("General")
        return f"{self.get_document_type_display()} {' '.join(context_parts)} ({display_name})"

    class Meta:
        verbose_name = "Customer Document"; verbose_name_plural = "Customer Documents"; ordering = ['-uploaded_at']


class Expense(models.Model):
    # ... (your Expense model fields - keep as is) ...
    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name='expenses')
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name='expenses')
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT, related_name='expenses',
                                 verbose_name="Expense Category")
    receipt_document = models.ForeignKey(CustomerDocument, on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='expenses', help_text="Link to an uploaded document/receipt")
    expense_date = models.DateField(default=timezone.now, db_index=True);
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True);
    invoice_number = models.CharField(max_length=100, blank=True)
    draw_number = models.PositiveIntegerField(choices=[(1, 'Draw 1'), (2, 'Draw 2'), (3, 'Draw 3')], null=True,
                                              blank=True, db_index=True,
                                              help_text="Which draw period does this expense belong to?")
    is_active = models.BooleanField(default=True, db_index=True);
    created_at = models.DateTimeField(auto_now_add=True);
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self): return f"Expense: ${self.amount} for {self.project.project_name} on {self.expense_date}"

    class Meta: verbose_name_plural = "Expenses"; ordering = ['-expense_date', '-created_at']


class CostItem(models.Model):  # Represents Budget lines
    # ... (your CostItem model fields - keep as is) ...
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='cost_items')
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT, related_name='cost_items',
                                 verbose_name="Expense Category")
    description = models.CharField(max_length=255,
                                   help_text="Specific item description (e.g., 'labor for framing', 'Permit Fee') - From QBO Estimate")
    budgeted_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00);
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True);
    created_at = models.DateTimeField(default=timezone.now, editable=False);
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(
            self): return f"Budget for {self.description} ({self.category.name}) in {self.project.project_name}: ${self.budgeted_amount}"

    class Meta:
        verbose_name = "Cost Item (Budget Line)";
        verbose_name_plural = "Cost Items (Budget Lines)"
        constraints = [models.UniqueConstraint(fields=['project', 'category', 'description'],
                                               name='unique_project_category_item_budget')]
        ordering = ['project', 'category__name', 'description']


class BlogCategory(models.Model):
    # ... (your BlogCategory model fields - keep as is) ...
    name = models.CharField(max_length=100, unique=True);
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True);
    is_active = models.BooleanField(default=True, db_index=True)

    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.name); original_slug = self.slug; counter = 1
        while BlogCategory.objects.filter(slug=self.slug).exclude(
            id=self.id).exists(): self.slug = f"{original_slug}-{counter}"; counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Blog Category"; verbose_name_plural = "Blog Categories"; ordering = ['name']


class BlogPost(models.Model):
    # ... (your BlogPost model fields - keep as is) ...
    STATUS_CHOICES = [('DRAFT', 'Draft'), ('PUBLISHED', 'Published')]
    title = models.CharField(max_length=255);
    slug = models.SlugField(max_length=270, unique=True, blank=True)
    content = models.TextField();
    excerpt = models.TextField(blank=True)
    featured_image = models.ImageField(upload_to='blog_featured_images/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT', db_index=True)
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='blog_posts')
    published_date = models.DateTimeField(null=True, blank=True, db_index=True);
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True);
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.title); original_slug = self.slug; counter = 1
        while BlogPost.objects.filter(slug=self.slug).exclude(
            id=self.id).exists(): self.slug = f"{original_slug}-{counter}"; counter += 1
        if self.status == 'PUBLISHED' and self.published_date is None: self.published_date = timezone.now()
        super().save(*args, **kwargs)

    def is_live(self):
        return self.status == 'PUBLISHED' and self.published_date is not None and self.published_date <= timezone.now() and self.is_active

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Blog Post"; verbose_name_plural = "Blog Posts"; ordering = ['-published_date', '-created_at']


class ContactInquiry(models.Model):
    # ... (your ContactInquiry model fields - keep as is) ...
    STATUS_CHOICES = [('NEW', 'New'), ('CONTACTED', 'Contacted'), ('CLOSED', 'Closed'), ('ARCHIVED', 'Archived')]
    name = models.CharField(max_length=200);
    email = models.EmailField(max_length=254)
    phone_number = models.CharField(max_length=25, blank=True);
    subject = models.CharField(max_length=255, blank=True)
    message = models.TextField();
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='NEW', db_index=True)
    internal_notes = models.TextField(blank=True);
    submitted_at = models.DateTimeField(auto_now_add=True);
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self): return f"Inquiry from {self.name} ({self.email}) - {self.submitted_at.strftime('%Y-%m-%d')}"

    class Meta: verbose_name = "Contact Inquiry"; verbose_name_plural = "Contact Inquiries"; ordering = [
        '-submitted_at']


class PortfolioProject(models.Model):  # Public Portfolio Item
    category = models.ForeignKey(
        PortfolioCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='portfolio_projects'
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=270, unique=True, blank=True)
    featured_image = models.ImageField(upload_to='portfolio_featured_images/', null=True, blank=True,
                                       help_text="Main image for the portfolio grid and hero.")
    short_description = models.TextField(blank=True,
                                         help_text="A brief description displayed on portfolio list pages.")
    details = models.TextField(help_text="Detailed information about the project, shown on the project's detail page.")

    # --- NEW FIELDS TO BE ADDED for more detailed portfolio information ---
    location = models.CharField(max_length=255, blank=True, help_text="e.g., City, State or Neighborhood")
    year_completed = models.PositiveIntegerField(null=True, blank=True, help_text="Year the project was completed.")
    square_footage = models.PositiveIntegerField(null=True, blank=True, help_text="Approximate square footage.")

    PROJECT_STATUS_CHOICES = [  # Status specific to portfolio display, e.g. for 'Coming Soon'
        ('COMPLETED', 'Completed'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMING_SOON', 'Coming Soon'),
        ('DESIGN_PHASE', 'Design Phase'),
    ]
    status = models.CharField(
        max_length=20,
        choices=PROJECT_STATUS_CHOICES,
        default='COMPLETED',
        blank=True,
        help_text="Current status of this portfolio project (for display)."
    )

    order = models.PositiveIntegerField(default=0,
                                        help_text="Order for display on portfolio list pages (lower numbers show first).")
    # End of NEW FIELDS ---

    is_active = models.BooleanField(default=True, db_index=True,
                                    help_text="Controls if this project is visible on the public site.")  # Renamed from is_public for consistency
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            counter = 1
            while PortfolioProject.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('portfolio_app:portfolio_detail', kwargs={'slug': self.slug})

    def get_first_image_url(self):
        if self.featured_image:
            return self.featured_image.url
        first_gallery_image = self.images.order_by('order', 'uploaded_at').first()
        if first_gallery_image and first_gallery_image.image:
            return first_gallery_image.image.url
        return None  # Or a placeholder image URL

    class Meta:
        verbose_name = "Portfolio Project"
        verbose_name_plural = "Portfolio Projects"
        ordering = ['order', '-created_at']  # Updated ordering to include 'order'


class PortfolioImage(models.Model):  # Gallery images FOR PortfolioProject
    portfolio_project = models.ForeignKey(
        PortfolioProject,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to=get_portfolio_image_upload_path)
    caption = models.CharField(max_length=255, blank=True, help_text="Optional caption (e.g., room name).")
    order = models.PositiveIntegerField(default=0,
                                        help_text="Order of image in the gallery (lower numbers show first).")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def image_preview(self):
        if self.image:
            return mark_safe(f'<img src="{self.image.url}" width="150" height="auto" style="object-fit: cover;" />')
        return "(No image)"

    image_preview.short_description = 'Preview'

    def __str__(self):
        return f"Image for {self.portfolio_project.title} (Order: {self.order})"

    class Meta:
        verbose_name = "Portfolio Gallery Image"
        verbose_name_plural = "Portfolio Gallery Images"
        ordering = ['portfolio_project', 'order',
                    'uploaded_at']  # Added portfolio_project for better grouping if needed


class ActivityLog(models.Model):
    # ... (your ActivityLog model fields - keep as is) ...
    NOTE_TYPE_CHOICES = [('NOTE', 'General Note'), ('CALL', 'Phone Call'), ('EMAIL', 'Email'), ('MEETING', 'Meeting'),
                         ('SITE', 'Site Visit'), ('UPDATE', 'Project Update')]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True,
                                 related_name='activity_logs')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='activity_logs')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='authored_activity_logs')
    timestamp = models.DateTimeField(default=timezone.now, editable=False);
    note_type = models.CharField(max_length=10, choices=NOTE_TYPE_CHOICES, default='NOTE')
    note = models.TextField()

    class Meta: ordering = [
        '-timestamp']; verbose_name = "Activity Log / Note"; verbose_name_plural = "Activity Logs / Notes"

    def __str__(self):
        target = f"for {self.customer}" if self.customer else f"for {self.project}" if self.project else "General"
        author_name = self.author.get_full_name() or self.author.username if self.author else "System"
        return f"{self.get_note_type_display()} {target} by {author_name} on {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
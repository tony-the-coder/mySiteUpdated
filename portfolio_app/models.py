# portfolio_app/models.py
import os
from django.db import models
from django.utils import timezone
from django.conf import settings # For BlogPost author
from django.utils.text import slugify
from django.utils.html import mark_safe
from django.urls import reverse

# --- Helper Functions ---

def get_portfolio_image_upload_path(instance, filename):
    """ Creates a path like: portfolio_gallery/project_slug/filename.ext """
    project_slug = "unassigned"
    if hasattr(instance, 'portfolio_project') and instance.portfolio_project and \
       hasattr(instance.portfolio_project, 'slug') and instance.portfolio_project.slug:
        project_slug = instance.portfolio_project.slug
    safe_filename = os.path.basename(filename)
    return f'portfolio_gallery/{project_slug}/{safe_filename}'

# --- Models for TonyTheCoder.com ---

class PortfolioCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="e.g., Python/Django, React, AI/ML, Full-Stack")
    slug = models.SlugField(max_length=110, unique=True, blank=True)
    description = models.TextField(blank=True, null=True, help_text="Optional: A brief description of this category/tech stack.")
    is_active = models.BooleanField(default=True, db_index=True)

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

    def get_absolute_url(self):
        # This URL might be used by Django admin or sitemaps.
        # If React handles all category filtering client-side, it might not be used on the public site.
        return reverse('portfolio_app:portfolio_projects_by_category', kwargs={'category_slug': self.slug})

    class Meta:
        verbose_name = "Portfolio Project Category"
        verbose_name_plural = "Portfolio Project Categories"
        ordering = ['name']


class PortfolioProject(models.Model):  # For Your Coding Projects
    categories = models.ManyToManyField(
        PortfolioCategory,
        blank=True,
        related_name='portfolio_projects', # Default related_name, good
        help_text="Select one or more categories/tech stacks for this project (e.g., Python, React, AI)."
    )
    title = models.CharField(max_length=255, help_text="Name of your coding project.")
    slug = models.SlugField(max_length=270, unique=True, blank=True)
    featured_image = models.ImageField(
        upload_to='portfolio_featured_images/',
        null=True, blank=True,
        help_text="A screenshot or representative image for the project card."
    )
    short_description = models.TextField(
        blank=True,
        help_text="A brief 1-2 sentence summary for list views or cards (used for meta descriptions too)."
    )
    details = models.TextField( # For CKEditor in admin/forms
        help_text="Detailed description: project goals, challenges, solutions, your role, learnings."
    )
    technologies_used = models.CharField(
        max_length=500, blank=True,
        help_text="Comma-separated list of key technologies (e.g., Python, Django, React, TensorFlow, Vite)."
    )
    github_url = models.URLField(max_length=255, blank=True, null=True, help_text="Link to the GitHub repository.")
    live_demo_url = models.URLField(max_length=255, blank=True, null=True, help_text="Link to the live deployed project.")

    order = models.PositiveIntegerField(
        default=0,
        help_text="Order for display (lower numbers show first)."
    )

    STATUS_CHOICES = [
        ('COMPLETED', 'Completed'),
        ('IN_PROGRESS', 'In Progress'),
        ('CONCEPT', 'Concept/Learning'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='COMPLETED',
        blank=True,
        help_text="Current status of this coding project."
    )
    year_completed = models.PositiveIntegerField( # Kept this as it can be relevant for coding projects
        null=True, blank=True, help_text="Year the project was primarily developed or completed."
    )

    is_active = models.BooleanField(
        default=True, db_index=True,
        help_text="Controls if this project is visible on your public portfolio."
    )
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
        # This might be used for sitemaps or if you decide to have a fallback Django detail view.
        # If React handles all routing client-side for project details, this could simply be:
        # return self.live_demo_url or self.github_url or f"/portfolio/#{self.slug}"
        # For now, let's assume a potential (even if unused) Django detail view for the 'portfolio_app'
        # This will need a corresponding URL pattern named 'portfolio_project_detail_django'.
        # If your React app takes over the /portfolio/ route, this won't be hit directly by users.
        try:
            return reverse('portfolio_app:portfolio_project_detail_django', kwargs={'slug': self.slug})
        except Exception: # Avoid errors if the URL is not defined
            return "#"


    def get_first_image_url(self): # For API and templates
        if self.featured_image and hasattr(self.featured_image, 'url'):
            return self.featured_image.url
        # Ensure 'images' related_name is correct and refers to PortfolioImage model
        first_gallery_image = self.images.filter(image__isnull=False).exclude(image__exact='').order_by('order', 'uploaded_at').first()
        if first_gallery_image and first_gallery_image.image and hasattr(first_gallery_image.image, 'url'):
            return first_gallery_image.image.url
        return None # Or return static('portfolio_app/images/default_project.png')

    class Meta:
        verbose_name = "Coding Project"
        verbose_name_plural = "Coding Projects"
        ordering = ['order', '-created_at']


class PortfolioImage(models.Model):
    portfolio_project = models.ForeignKey(
        PortfolioProject,
        on_delete=models.CASCADE,
        related_name='images' # This matches get_first_image_url above
    )
    image = models.ImageField(upload_to=get_portfolio_image_upload_path)
    caption = models.CharField(max_length=255, blank=True, help_text="Optional caption (e.g., specific feature screenshot).")
    order = models.PositiveIntegerField(default=0, help_text="Order of image in the gallery (lower numbers show first).")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def image_preview(self):
        if self.image and hasattr(self.image, 'url'):
            return mark_safe(f'<img src="{self.image.url}" width="150" height="auto" style="max-height: 100px; object-fit: contain;" />')
        return "(No image)"
    image_preview.short_description = 'Preview'

    def __str__(self):
        return f"Image for {self.portfolio_project.title} (Order: {self.order})"

    class Meta:
        verbose_name = "Coding Project Image"
        verbose_name_plural = "Coding Project Images"
        ordering = ['portfolio_project', 'order', 'uploaded_at']


class BlogCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, help_text="A short description for the category page (SEO).")
    is_active = models.BooleanField(default=True, db_index=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            original_slug = self.slug
            counter = 1
            while BlogCategory.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('portfolio_app:blog_category_list', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = "Blog Category"
        verbose_name_plural = "Blog Categories"
        ordering = ['name']


class BlogPost(models.Model):
    STATUS_CHOICES = [('DRAFT', 'Draft'), ('PUBLISHED', 'Published')]
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=270, unique=True, blank=True)
    content = models.TextField(help_text="Main content of the blog post. Use Markdown or enable CKEditor.")
    excerpt = models.TextField(blank=True, help_text="A short summary for list views and meta descriptions (SEO).")
    featured_image = models.ImageField(upload_to='blog_featured_images/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT', db_index=True)
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True, # Allow admin to create posts without assigning author if needed
        related_name='blog_posts'
    )
    published_date = models.DateTimeField(null=True, blank=True, db_index=True, help_text="Set date to make post live (if status='Published'). Auto-set if published and date is blank.")
    is_active = models.BooleanField(default=True, db_index=True, help_text="Controls overall visibility. Set status to 'Draft' to unpublish.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            counter = 1
            while BlogPost.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        if self.status == 'PUBLISHED' and self.published_date is None:
            self.published_date = timezone.now()
        super().save(*args, **kwargs)

    def is_live(self):
        return self.status == 'PUBLISHED' and self.published_date is not None and self.published_date <= timezone.now() and self.is_active

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('portfolio_app:blog_post_detail', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
        ordering = ['-published_date', '-created_at']


class ContactInquiry(models.Model):
    STATUS_CHOICES = [('NEW', 'New'), ('READ', 'Read'), ('RESPONDED', 'Responded'), ('ARCHIVED', 'Archived')]
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=254)
    phone_number = models.CharField(max_length=25, blank=True)
    subject = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='NEW', db_index=True)
    internal_notes = models.TextField(blank=True, help_text="Internal notes about this inquiry.")
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Inquiry from {self.name} ({self.email}) - {self.submitted_at.strftime('%Y-%m-%d')}"

    class Meta:
        verbose_name = "Contact Inquiry"
        verbose_name_plural = "Contact Inquiries"
        ordering = ['-submitted_at']

# Note: Models like Customer, Project (internal construction project), Vendor, Expense, etc.,
# from the original Lehman site have been removed as they are not typically needed
# for a personal developer portfolio. If you intend to manage freelance clients
# and their projects through this site, you might re-introduce simplified versions later.
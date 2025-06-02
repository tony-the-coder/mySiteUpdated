# portfolio_app/views.py

# --- Standard Library Imports ---
import os
import logging
from collections import defaultdict
from decimal import Decimal

# --- Django Imports ---
from django.contrib import admin, messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Q, Count, Max
from django.db.models.functions import TruncMonth
from django.forms import inlineformset_factory, modelformset_factory  # Keep for staff forms
from django.http import HttpResponse, HttpResponseForbidden, Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView
from django.utils.text import Truncator
from django.utils.html import strip_tags
from django.core.files.base import ContentFile
from django.contrib.auth import update_session_auth_hash
from django.conf import settings

# --- Third Party Imports ---
try:
    from PIL import Image as PillowImage
except ImportError:
    PillowImage = None
    logging.warning("Pillow library not installed. Some image functionalities might be limited.")

# --- App Imports ---
from .forms import (
    ContactForm,  # Keep ContactForm if used by Django before React takes over
    # ExpenseForm, # Likely remove if internal Project model is removed
    StaffPortfolioProjectForm,  # This will need to be updated for new PortfolioProject fields
    PortfolioImageManagementForm,
    StaffUserChangeForm,
)
from .models import (
    # ActivityLog, # Optional: Keep if you want to log your own activities
    BlogCategory, BlogPost, ContactInquiry, PortfolioCategory,
    PortfolioImage, PortfolioProject,
    # Models to likely remove/re-evaluate for portfolio:
    # CostItem, Customer, CustomerDocument, Expense, ExpenseCategory,
    # Project, InternalProjectImage, Vendor
)

logger = logging.getLogger(__name__)


# --- Helper Functions ---
def is_office_staff(user):  # For your portfolio, this might just become `user.is_staff`
    if not user.is_authenticated:
        return False
    return user.is_active and (user.is_staff or user.groups.filter(name='OfficeStaff').exists())


# --- Public Site Views ---
def home(request):
    published_status = getattr(BlogPost, 'PUBLISHED', 'PUBLISHED')
    try:
        latest_blog_posts = BlogPost.objects.filter(
            status=published_status,
            published_date__lte=timezone.now(),
            is_active=True
        ).select_related('category', 'author').order_by('-published_date')[:3]
    except Exception as e:
        logger.error(f"Error fetching latest blog posts for home page: {e}")
        latest_blog_posts = []

    # Fetch your coding projects for the homepage
    try:
        latest_portfolio_projects = PortfolioProject.objects.filter(is_active=True).order_by('order', '-created_at')[:3]
    except Exception as e:
        logger.error(f"Error fetching latest portfolio projects for home page: {e}")
        latest_portfolio_projects = []

    context = {
        'latest_blog_posts': latest_blog_posts,
        'latest_portfolio_projects': latest_portfolio_projects,
        'page_title': 'Tony the Coder - Full-Stack Developer & AI Enthusiast',
        'meta_description': "Welcome to the portfolio of Tony the Coder. Discover projects in Python, Django, React, AI, and more.",
        'is_staff_portal': False,
    }
    return render(request, 'portfolio_app/home.html', context)


def about_us(request):  # Will be "About Me"
    context = {
        'page_title': 'About Tony the Coder',
        'meta_description': "Learn more about Tony the Coder, a developer passionate about building innovative solutions and exploring new technologies.",
        'breadcrumbs': [
            {'name': 'Home', 'url': reverse('portfolio_app:home')},
            {'name': 'About Me', 'is_active': True},
        ],
        'is_staff_portal': False,
    }
    return render(request, 'portfolio_app/about_us.html', context)


def contact_us(request):
    # This view will initially serve the page for the React contact form.
    # The actual form submission will be handled by an API view.
    form = ContactForm()  # You might still pass an empty form for non-JS fallback or initial structure
    context = {
        'form': form,  # If React handles it all, this might become unnecessary
        'page_title': 'Contact Tony the Coder',
        'meta_description': "Get in touch with Tony the Coder to discuss projects, collaborations, or just to say hi!",
        'breadcrumbs': [
            {'name': 'Home', 'url': reverse('portfolio_app:home')},
            {'name': 'Contact', 'is_active': True},
        ],
        'is_staff_portal': False,
    }
    return render(request, 'portfolio_app/contact_us.html', context)


# API endpoint for React contact form (Example)
def api_contact_submit(request):
    if request.method == 'POST':
        # For React, you'd typically parse JSON data
        # import json
        # try:
        #     data = json.loads(request.body)
        #     form = ContactForm(data) # Assuming ContactForm can handle a dictionary
        # except json.JSONDecodeError:
        #     return JsonResponse({'status': 'error', 'errors': {'form': ['Invalid JSON.']}}, status=400)

        # For now, let's assume standard form data if testing without JS first
        form = ContactForm(request.POST)

        if form.is_valid():
            form.save()
            # In a real API, you wouldn't use Django messages directly like this for React
            return JsonResponse(
                {'status': 'success', 'message': 'Thank you for your message! We will be in touch soon.'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


def blog_list(request):
    published_status = getattr(BlogPost, 'PUBLISHED', 'PUBLISHED')
    posts = BlogPost.objects.filter(
        status=published_status,
        published_date__lte=timezone.now(),
        is_active=True
    ).select_related('category', 'author').order_by('-published_date')
    categories = BlogCategory.objects.filter(is_active=True).annotate(
        num_posts=Count('posts', filter=Q(
            posts__status=published_status,
            posts__published_date__lte=timezone.now(),
            posts__is_active=True
        ))
    ).filter(num_posts__gt=0).order_by('name')
    context = {
        'blog_posts': posts,
        'categories_for_sidebar': categories,
        'page_title': 'Tony\'s Tech Blog - Coding & AI Insights',
        'meta_description': "Explore articles on web development, Python, Django, React, AI, and other technology topics by Tony the Coder.",
        'breadcrumbs': [
            {'name': 'Home', 'url': reverse('portfolio_app:home')},
            {'name': 'Blog', 'is_active': True},
        ],
        'is_staff_portal': False,
    }
    return render(request, 'portfolio_app/blog_list.html', context)


def blog_post_detail(request, slug):
    published_status = getattr(BlogPost, 'PUBLISHED', 'PUBLISHED')
    post_instance = get_object_or_404(
        BlogPost.objects.select_related('category', 'author'),
        slug=slug, status=published_status, published_date__lte=timezone.now(), is_active=True
    )
    related_posts = BlogPost.objects.none()
    if post_instance:
        base_query = BlogPost.objects.filter(
            status=published_status, published_date__lte=timezone.now(), is_active=True
        ).exclude(pk=post_instance.pk).select_related('category')
        if post_instance.category:
            related_posts = base_query.filter(category=post_instance.category).order_by('-published_date')[:3]
        if not related_posts.exists():
            related_posts = base_query.order_by('-published_date')[:3]

    breadcrumbs = [
        {'name': 'Home', 'url': reverse('portfolio_app:home')},
        {'name': 'Blog', 'url': reverse('portfolio_app:blog_list')},
    ]
    if post_instance and post_instance.category:
        breadcrumbs.append({'name': post_instance.category.name,
                            'url': reverse('portfolio_app:blog_category_list',
                                           kwargs={'slug': post_instance.category.slug})})
    breadcrumbs.append({'name': Truncator(post_instance.title).chars(40, truncate="..."), 'is_active': True})
    context = {
        'post': post_instance, 'related_posts': related_posts,
        'page_title': post_instance.title,
        'meta_description': (
                    post_instance.excerpt or Truncator(strip_tags(post_instance.content)).words(25, truncate="...")),
        'breadcrumbs': breadcrumbs,
        'is_staff_portal': False,
    }
    return render(request, 'portfolio_app/blog_post_detail.html', context)


def blog_category_list(request, slug):
    category = get_object_or_404(BlogCategory, slug=slug, is_active=True)
    published_status = getattr(BlogPost, 'PUBLISHED', 'PUBLISHED')
    posts = BlogPost.objects.filter(
        category=category, status=published_status, published_date__lte=timezone.now(), is_active=True
    ).select_related('author', 'category').order_by('-published_date')
    all_categories = BlogCategory.objects.filter(is_active=True).annotate(
        num_posts=Count('posts', filter=Q(posts__status=published_status, posts__published_date__lte=timezone.now(),
                                          posts__is_active=True))
    ).filter(num_posts__gt=0).order_by('name')
    breadcrumbs = [
        {'name': 'Home', 'url': reverse('portfolio_app:home')},
        {'name': 'Blog', 'url': reverse('portfolio_app:blog_list')},
        {'name': category.name, 'is_active': True},
    ]
    context = {
        'category': category, 'blog_posts': posts, 'categories_for_sidebar': all_categories,
        'page_title': f'{category.name} Posts - Tony\'s Tech Blog',
        'meta_description': category.description or f"Explore blog posts by Tony the Coder in the '{category.name}' category.",
        'breadcrumbs': breadcrumbs,
        'is_staff_portal': False,
    }
    return render(request, 'portfolio_app/blog_category_list.html', context)


# --- New React Portfolio Views ---

def portfolio_showcase_react(request):
    context = {
        'page_title': 'My Coding Portfolio - Tony the Coder',
        'meta_description': "A showcase of web development, Python, Django, React, and AI projects by Tony the Coder.",
        'breadcrumbs': [
            {'name': 'Home', 'url': reverse('portfolio_app:home')},
            {'name': 'Portfolio', 'is_active': True},
        ],
        'is_staff_portal': False,
    }
    return render(request, 'portfolio_app/portfolio_showcase_react.html', context)


def api_portfolio_projects(request):
    projects = PortfolioProject.objects.filter(is_active=True).order_by('order', '-created_at').prefetch_related(
        'categories')
    data = []
    for p in projects:
        project_data = {
            'id': p.pk,
            'title': p.title,
            'slug': p.slug,
            'short_description': p.short_description,
            'details': p.details,
            'imageUrl': None,
            'categories': [{'name': cat.name, 'slug': cat.slug} for cat in p.categories.all()],
            'technologies_used': p.technologies_used,
            'github_url': p.github_url,
            'live_demo_url': p.live_demo_url,
            'year_completed': p.year_completed,
            'status': p.get_status_display()  # To get the display name of status
        }
        first_image_url_path = p.get_first_image_url()
        if first_image_url_path:
            project_data['imageUrl'] = request.build_absolute_uri(first_image_url_path)
        # else:
        # project_data['imageUrl'] = request.build_absolute_uri(settings.STATIC_URL + 'images/default_project_thumb.png') # Example default
        data.append(project_data)
    return JsonResponse({'projects': data})


def api_portfolio_categories(request):  # New API view for categories
    published_status = getattr(BlogPost, 'PUBLISHED', 'PUBLISHED')  # Used in BlogPost category count
    categories = PortfolioCategory.objects.filter(is_active=True).annotate(
        num_active_projects=Count('portfolio_projects', filter=Q(portfolio_projects__is_active=True))
    ).filter(num_active_projects__gt=0).order_by('name')
    data = [{'name': cat.name, 'slug': cat.slug, 'description': cat.description} for cat in categories]
    return JsonResponse({'categories': data})


# --- Staff Portal Views (Updated for TonyTheCoder.com) ---

@login_required
@user_passes_test(is_office_staff)
def staff_dashboard(request):
    active_portfolio_projects_count = PortfolioProject.objects.filter(is_active=True).count()
    draft_blog_posts_count = BlogPost.objects.filter(status='DRAFT', is_active=True).count()
    new_inquiry_count = ContactInquiry.objects.filter(status='NEW').count()
    context = {
        'page_title': 'Tony the Coder - Admin Dashboard',
        'active_portfolio_projects_count': active_portfolio_projects_count,
        'draft_blog_posts_count': draft_blog_posts_count,
        'new_inquiry_count': new_inquiry_count,
        'breadcrumbs': [{'name': 'Admin Dashboard', 'is_active': True}],
        'is_staff_portal': True,
    }
    return render(request, 'portfolio_app/staff/dashboard.html', context)


@login_required
@user_passes_test(is_office_staff)
def staff_user_profile(request):
    user_object = request.user
    context = {
        'page_title': 'My Profile',
        'user_profile': user_object,
        'is_staff_portal': True,
        'breadcrumbs': [
            {'name': 'Admin Dashboard', 'url': reverse('portfolio_app:staff_dashboard')},
            {'name': 'My Profile', 'is_active': True}
        ]
    }
    return render(request, 'portfolio_app/staff/staff_user_profile.html', context)


@login_required
@user_passes_test(is_office_staff)
def staff_user_profile_edit(request):
    if request.method == 'POST':
        form = StaffUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect(reverse('portfolio_app:staff_user_profile'))
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StaffUserChangeForm(instance=request.user)
    context = {
        'page_title': 'Edit My Profile',
        'form': form,
        'is_staff_portal': True,
        'breadcrumbs': [
            {'name': 'Admin Dashboard', 'url': reverse('portfolio_app:staff_dashboard')},
            {'name': 'My Profile', 'url': reverse('portfolio_app:staff_user_profile')},
            {'name': 'Edit', 'is_active': True}
        ]
    }
    return render(request, 'portfolio_app/staff/staff_user_profile_edit.html', context)


# Staff Portfolio Project Management (for coding projects)
@login_required
@user_passes_test(is_office_staff)
def staff_portfolio_list(request):
    portfolio_items = PortfolioProject.objects.select_related('categories').order_by('order', '-created_at')
    context = {
        'page_title': 'Manage Coding Projects',
        'portfolio_items': portfolio_items,
        'breadcrumbs': [{'name': 'Admin Dashboard', 'url': reverse('portfolio_app:staff_dashboard')},
                        {'name': 'Manage Coding Projects', 'is_active': True}],
        'is_staff_portal': True,
    }
    return render(request, 'portfolio_app/staff/portfolio_list_staff.html', context)


@login_required
@user_passes_test(is_office_staff)
def staff_portfolio_add(request):
    if request.method == 'POST':
        form = StaffPortfolioProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project_instance = form.save()
            new_gallery_images = request.FILES.getlist('new_images')
            images_uploaded_count = 0
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            for uploaded_file in new_gallery_images:
                ext = os.path.splitext(uploaded_file.name)[1].lower()
                if ext not in allowed_extensions:
                    messages.error(request, f"Invalid file type: {uploaded_file.name}. Only image files allowed.")
                    continue
                if PillowImage:
                    try:
                        img = PillowImage.open(uploaded_file)
                        img.verify()  # Check if it's a valid image
                        uploaded_file.seek(0)  # Reset file pointer after verify
                    except Exception as e:
                        logger.error(f"Pillow could not verify gallery image {uploaded_file.name}: {e}")
                        messages.error(request, f"File {uploaded_file.name} could not be verified as a valid image.")
                        continue
                PortfolioImage.objects.create(portfolio_project=project_instance, image=uploaded_file, caption='',
                                              order=0)
                images_uploaded_count += 1
            messages.success(request, f'Coding Project "{project_instance.title}" created successfully.')
            if images_uploaded_count > 0:
                messages.info(request, f'{images_uploaded_count} new gallery image(s) uploaded.')
            return redirect(reverse('portfolio_app:staff_manage_portfolio_images', kwargs={'pk': project_instance.pk}))
        else:
            messages.error(request, "Error: Please correct the project details below.")
    else:
        form = StaffPortfolioProjectForm()
        if 'order' in form.fields:  # Check if order field exists
            max_order = PortfolioProject.objects.aggregate(Max('order'))['order__max']
            form.fields['order'].initial = (max_order or 0) + 1
    context = {
        'form': form, 'project': None,
        'form_title': 'Add New Coding Project', 'page_title': 'Add Coding Project',
        'breadcrumbs': [
            {'name': 'Admin Dashboard', 'url': reverse('portfolio_app:staff_dashboard')},
            {'name': 'Manage Coding Projects', 'url': reverse('portfolio_app:staff_portfolio_list')},
            {'name': 'Add Project', 'is_active': True}
        ],
        'is_staff_portal': True,
    }
    return render(request, 'portfolio_app/staff/portfolio_project_form.html', context)


@login_required
@user_passes_test(is_office_staff)
def staff_portfolio_edit(request, pk):
    project_instance = get_object_or_404(PortfolioProject, pk=pk)
    if request.method == 'POST':
        form = StaffPortfolioProjectForm(request.POST, request.FILES, instance=project_instance)
        if form.is_valid():
            updated_project = form.save()
            new_gallery_images = request.FILES.getlist('new_images')
            images_uploaded_count = 0
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            for uploaded_file in new_gallery_images:
                ext = os.path.splitext(uploaded_file.name)[1].lower()
                if ext not in allowed_extensions:
                    messages.error(request, f"Invalid file type: {uploaded_file.name}. Only image files allowed.")
                    continue
                if PillowImage:
                    try:
                        img = PillowImage.open(uploaded_file)
                        img.verify()
                        uploaded_file.seek(0)
                    except Exception as e:
                        logger.error(f"Pillow could not verify gallery image {uploaded_file.name}: {e}")
                        messages.error(request, f"File {uploaded_file.name} could not be verified as a valid image.")
                        continue
                PortfolioImage.objects.create(portfolio_project=updated_project, image=uploaded_file, caption='',
                                              order=0)
                images_uploaded_count += 1
            messages.success(request, f'Coding Project "{updated_project.title}" updated successfully.')
            if images_uploaded_count > 0:
                messages.info(request, f'{images_uploaded_count} new gallery image(s) uploaded.')
            return redirect(reverse('portfolio_app:staff_manage_portfolio_images', kwargs={'pk': updated_project.pk}))
        else:
            messages.error(request, "Error: Please correct the project details below.")
    else:
        form = StaffPortfolioProjectForm(instance=project_instance)
    context = {
        'form': form, 'project': project_instance,
        'form_title': f'Edit Coding Project: {project_instance.title}',
        'page_title': f'Edit Project: {Truncator(project_instance.title).chars(40)}',
        'breadcrumbs': [
            {'name': 'Admin Dashboard', 'url': reverse('portfolio_app:staff_dashboard')},
            {'name': 'Manage Coding Projects', 'url': reverse('portfolio_app:staff_portfolio_list')},
            {'name': f'Edit: {Truncator(project_instance.title).chars(30, truncate="...")}', 'is_active': True}
        ],
        'is_staff_portal': True,
    }
    return render(request, 'portfolio_app/staff/portfolio_project_form.html', context)


@login_required
@user_passes_test(is_office_staff)
def staff_manage_portfolio_images(request, pk):
    project = get_object_or_404(PortfolioProject, pk=pk)
    PortfolioImageFormSet = modelformset_factory(
        PortfolioImage,
        form=PortfolioImageManagementForm,
        extra=0,  # No empty forms for adding new, new images are added via staff_portfolio_add/edit
        can_delete=True,
    )
    queryset = PortfolioImage.objects.filter(portfolio_project=project).order_by('order', 'id')

    if request.method == 'POST':
        formset = PortfolioImageFormSet(request.POST, request.FILES, queryset=queryset)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for obj in formset.deleted_objects:
                if obj.image and hasattr(obj.image, 'path') and os.path.isfile(obj.image.path):
                    try:
                        os.remove(obj.image.path)
                    except OSError as e:
                        logger.error(f"Error deleting image file {obj.image.path}: {e}")
                obj.delete()
            for instance in instances:
                instance.portfolio_project = project
                instance.save()

            featured_image_id_str = request.POST.get('set_featured_image_id')
            if featured_image_id_str:
                try:
                    featured_image_id = int(featured_image_id_str)
                    selected_gallery_image = PortfolioImage.objects.get(id=featured_image_id, portfolio_project=project)
                    if selected_gallery_image.image:
                        if not project.featured_image or project.featured_image.name != selected_gallery_image.image.name:
                            if project.featured_image and project.featured_image.name:
                                old_image_path = project.featured_image.path
                                if os.path.isfile(old_image_path):
                                    try:
                                        project.featured_image.delete(save=False)
                                    except Exception as e_del:
                                        logger.warning(
                                            f"Could not delete old featured image file {old_image_path}: {e_del}")

                            img_file_content = ContentFile(selected_gallery_image.image.read())
                            file_name = os.path.basename(selected_gallery_image.image.name)
                            project.featured_image.save(file_name, img_file_content,
                                                        save=False)  # Don't save project yet
                            messages.success(request,
                                             f"Image '{selected_gallery_image.caption or file_name}' set as the featured image.")
                        else:
                            messages.info(request, "Selected image is already the featured image.")
                    project.save()  # Save the project here to persist featured_image changes
                except (ValueError, PortfolioImage.DoesNotExist):
                    messages.error(request, "Invalid selection or image not found for featured image.")
                except Exception as e:
                    logger.error(
                        f"Error setting featured image for project {project.pk} from image {featured_image_id_str}: {e}")
                    messages.error(request, f"An error occurred while setting the featured image: {e}")

            if formset.has_changed() or formset.deleted_objects:
                messages.success(request, 'Gallery image details updated successfully!')
            elif not featured_image_id_str:  # Only show if no other message was more relevant
                messages.info(request, 'No changes detected in gallery images.')

            return redirect(reverse('portfolio_app:staff_manage_portfolio_images', kwargs={'pk': project.pk}))
        else:
            messages.error(request, "Please correct errors in the image forms below.")
    else:
        formset = PortfolioImageFormSet(queryset=queryset)
    context = {
        'project': project,
        'formset': formset,
        'form_title': f'Manage Images for: {project.title}',
        'page_title': f'Manage Images: {project.title}',
        'current_featured_image_name': os.path.basename(
            project.featured_image.name) if project.featured_image else None,
        'breadcrumbs': [
            {'name': 'Admin Dashboard', 'url': reverse('portfolio_app:staff_dashboard')},
            {'name': 'Manage Coding Projects', 'url': reverse('portfolio_app:staff_portfolio_list')},
            {'name': f'Edit Project: {Truncator(project.title).chars(30, truncate="...")}',
             'url': reverse('portfolio_app:staff_portfolio_edit', kwargs={'pk': project.pk})},
            {'name': 'Manage Images', 'is_active': True},
        ],
        'is_staff_portal': True,
    }
    return render(request, 'portfolio_app/staff/manage_portfolio_images.html', context)


@login_required
@user_passes_test(is_office_staff)
def portfolio_project_detail_staff(request, pk):
    project = get_object_or_404(PortfolioProject.objects.select_related('categories'), pk=pk)
    context = {
        'project': project,
        'page_title': f'Admin View: {project.title}',
        'breadcrumbs': [
            {'name': 'Admin Dashboard', 'url': reverse('portfolio_app:staff_dashboard')},
            {'name': 'Manage Coding Projects', 'url': reverse('portfolio_app:staff_portfolio_list')},
            {'name': Truncator(project.title).chars(30, truncate="..."), 'is_active': True}
        ],
        'is_staff_portal': True,
    }
    return render(request, 'portfolio_app/staff/portfolio_project_detail_staff.html', context)


@login_required
@user_passes_test(is_office_staff)
def staff_portfolio_delete(request, pk):
    project_instance = get_object_or_404(PortfolioProject, pk=pk)
    project_title = project_instance.title
    if request.method == 'POST':
        project_instance.delete()
        messages.success(request, f'Coding Project "{project_title}" and its images deleted.')
        return redirect(reverse('portfolio_app:staff_portfolio_list'))
    context = {
        'project': project_instance,
        'page_title': f'Confirm Delete: {project_title}',
        'breadcrumbs': [
            {'name': 'Admin Dashboard', 'url': reverse('portfolio_app:staff_dashboard')},
            {'name': 'Manage Coding Projects', 'url': reverse('portfolio_app:staff_portfolio_list')},
            {'name': f'Delete: {Truncator(project_title).chars(30, truncate="...")}', 'is_active': True}
        ],
        'is_staff_portal': True,
    }
    return render(request, 'portfolio_app/staff/portfolio_project_confirm_delete.html', context)

# --- (Potentially Remove/Simplify) Staff views for Customer, internal Project, Expense, Budget ---
# These views below were for the construction business logic.
# Review if you need similar functionality for managing freelance clients/projects.
# For a pure showcase portfolio, they might be unnecessary.
# I've updated namespaces and titles but their internal logic may need heavy adaptation.

# Example for one, apply similar thought to others if keeping them:
# @login_required
# @user_passes_test(is_office_staff)
# def staff_client_list(request): # Renamed from staff_customer_list
#     clients = Customer.objects.filter(is_active=True).order_by('last_name', 'first_name') # Assuming you keep Customer model for clients
#     context = {
#         'page_title': 'Manage Clients',
#         'clients': clients,
#         'breadcrumbs': [{'name': 'Admin Dashboard', 'url': reverse('portfolio_app:staff_dashboard')},
#                         {'name': 'Clients', 'is_active': True}],
#         'is_staff_portal': True,
#     }
#     return render(request, 'portfolio_app/staff/client_list.html', context) # New template name

# Ensure other views like staff_project_list (for internal projects), staff_project_detail,
# add_expense_to_project, edit_expense, delete_expense, etc., are updated or removed.
# For any you keep, update 'LehmanCustomConstruction:' to 'portfolio_app:' in reverse() calls
# and ensure templates are moved to 'portfolio_app/staff/' and paths in render() are updated.


# --- Admin Redirect Views (Update namespace if you keep underlying models) ---
# @staff_member_required
# def admin_customer_dashboard_view(request, customer_id):
#     customer = get_object_or_404(Customer, pk=customer_id) # If Customer model is kept
#     admin_url = reverse('admin:portfolio_app_customer_change', args=[customer.id])
#     return redirect(admin_url)

# @staff_member_required
# def admin_project_expenses_view(request, project_id): # Refers to old 'Project' model
#     project = get_object_or_404(Project, pk=project_id) # If 'Project' model for internal work is kept
#     admin_url = reverse('admin:portfolio_app_project_change', args=[project.id])
#     return redirect(admin_url)

# @staff_member_required
# def project_expenses_view(request, project_id): # Refers to old 'Project' model
#     # This view needs significant review if the 'Project' model functionality is changed or removed.
#     project_instance = get_object_or_404(Project, pk=project_id)
#     # ... (rest of the logic)
#     context = {
#         # ...
#         'breadcrumbs': [
#             {'name': 'Admin Dashboard', 'url': reverse('portfolio_app:staff_dashboard')},
#             # {'name': 'Client Projects', 'url': reverse('portfolio_app:staff_internal_project_list')}, # Example
#             # {'name': Truncator(project_instance.project_name).chars(30, truncate="..."),
#             #  'url': reverse('portfolio_app:staff_internal_project_detail', args=[project_instance.id])}, # Example
#             {'name': 'View Expenses', 'is_active': True}
#         ],
#         # ...
#     }
#     return render(request, 'portfolio_app/staff/internal_project_expenses.html', context) # Example new template
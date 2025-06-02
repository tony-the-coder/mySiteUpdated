# LehmanCustomConstruction/views.py

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
from django.forms import inlineformset_factory, modelformset_factory
from django.http import HttpResponse, HttpResponseForbidden, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView
from django.utils.text import Truncator
from django.utils.html import strip_tags
from django.core.files.base import ContentFile
from django.contrib.auth import update_session_auth_hash # For password change success

# --- Third Party Imports ---
try:
    from PIL import Image as PillowImage
except ImportError:
    PillowImage = None
    logging.warning("Pillow library not installed. Some image functionalities might be limited.")

# --- App Imports ---
from .forms import (
    ActivityLogForm, ContactForm, ExpenseForm,
    StaffPortfolioProjectForm,
    PortfolioImageManagementForm,
    StaffUserChangeForm, # Added new form
)
from .models import (
    ActivityLog, BlogCategory, BlogPost, ContactInquiry, CostItem, Customer,
    CustomerDocument, Expense, ExpenseCategory, PortfolioCategory,
    PortfolioImage, PortfolioProject, Project, ProjectImage as InternalProjectImage, Vendor
)

logger = logging.getLogger(__name__)


# --- Helper Functions ---
def is_office_staff(user):
    if not user.is_authenticated:
        return False
    return user.is_active and (user.is_staff or user.groups.filter(name='OfficeStaff').exists())


# --- Public Site Views ---
def home(request):
    sample_testimonials = [
        {'quote': "Exceptional craftsmanship and attention to detail. We love our new home!",
         'author_name': "The Millers"},
        {'quote': "From start to finish, the process was seamless and professional.", 'author_name': "J. Anderson"},
    ]
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
    context = {
        'testimonials': sample_testimonials,
        'latest_blog_posts': latest_blog_posts,
        'page_title': 'Custom Home Builder - Excellence & Craftsmanship',
        'meta_description': "Lehman Custom Construction builds high-quality, luxury custom homes with a focus on craftsmanship, integrity, and client satisfaction. Discover your dream home.",
        'is_staff_portal': False,
    }
    return render(request, 'LehmanCustomConstruction/home.html', context)


def about_us(request):
    about_content_placeholder = """<p>Lehman Custom Construction is dedicated to building high-quality, luxury custom homes with a focus on craftsmanship, integrity, and client satisfaction. Founded on years of experience in the construction industry, we partner with you to bring your unique vision to life, ensuring every detail reflects your dream and our commitment to excellence.</p>"""
    context = {
        'page_title': 'About Lehman Custom Construction',
        'about_content': about_content_placeholder,
        'meta_description': "Learn about Lehman Custom Construction, our dedication to luxury custom homes, craftsmanship, and client satisfaction.",
        'breadcrumbs': [
            {'name': 'Home', 'url': reverse('LehmanCustomConstruction:home')},
            {'name': 'About Us', 'is_active': True},
        ],
        'is_staff_portal': False,
    }
    return render(request, 'LehmanCustomConstruction/about_us.html', context)


def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for your message! We will be in touch soon.')
            return redirect('LehmanCustomConstruction:contact_us')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()
    context = {
        'form': form,
        'page_title': 'Contact Lehman Custom Construction',
        'meta_description': "Get in touch with Lehman Custom Construction to discuss your custom home project. We look forward to hearing from you.",
        'breadcrumbs': [
            {'name': 'Home', 'url': reverse('LehmanCustomConstruction:home')},
            {'name': 'Contact Us', 'is_active': True},
        ],
        'is_staff_portal': False,
    }
    return render(request, 'LehmanCustomConstruction/contact_us.html', context)


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
        'page_title': 'Design & Build Insights',
        'meta_description': "Explore the latest in custom home trends, expert advice, and project spotlights from Lehman Custom Construction.",
        'breadcrumbs': [
            {'name': 'Home', 'url': reverse('LehmanCustomConstruction:home')},
            {'name': 'Blog', 'is_active': True},
        ],
        'is_staff_portal': False,
    }
    return render(request, 'LehmanCustomConstruction/blog_list.html', context)


def blog_post_detail(request, slug):
    published_status = getattr(BlogPost, 'PUBLISHED', 'PUBLISHED')
    post_instance = get_object_or_404(
        BlogPost.objects.select_related('category', 'author'),
        slug=slug, status=published_status, published_date__lte=timezone.now(), is_active=True
    )
    related_posts = BlogPost.objects.none()
    if post_instance:
        if post_instance.category:
            related_posts = BlogPost.objects.filter(
                category=post_instance.category, status=published_status, published_date__lte=timezone.now(),
                is_active=True
            ).exclude(pk=post_instance.pk).select_related('category').order_by('-published_date')[:3]
        else:
            related_posts = BlogPost.objects.filter(
                status=published_status, published_date__lte=timezone.now(), is_active=True
            ).exclude(pk=post_instance.pk).select_related('category').order_by('-published_date')[:3]
    breadcrumbs = [
        {'name': 'Home', 'url': reverse('LehmanCustomConstruction:home')},
        {'name': 'Blog', 'url': reverse('LehmanCustomConstruction:blog_list')},
    ]
    if post_instance and post_instance.category:
        breadcrumbs.append({'name': post_instance.category.name,
                            'url': reverse('LehmanCustomConstruction:blog_category_list',
                                           kwargs={'slug': post_instance.category.slug})})
    if post_instance:
        breadcrumbs.append({'name': Truncator(post_instance.title).chars(40, truncate="..."), 'is_active': True})
    else:
        breadcrumbs.append({'name': "Post Not Found", 'is_active': True})
    context = {
        'post': post_instance, 'related_posts': related_posts,
        'page_title': post_instance.title if post_instance else "Blog Post",
        'meta_description': (post_instance.excerpt or Truncator(strip_tags(post_instance.content)).words(25,
                                                                                                         truncate="...")) if post_instance else "Read our latest blog post.",
        'breadcrumbs': breadcrumbs,
        'is_staff_portal': False,
    }
    return render(request, 'LehmanCustomConstruction/blog_post_detail.html', context)


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
        {'name': 'Home', 'url': reverse('LehmanCustomConstruction:home')},
        {'name': 'Blog', 'url': reverse('LehmanCustomConstruction:blog_list')},
        {'name': category.name, 'is_active': True},
    ]
    context = {
        'category': category, 'blog_posts': posts, 'categories_for_sidebar': all_categories,
        'page_title': f'{category.name} - Blog Insights',
        'meta_description': category.description or f"Explore blog posts related to '{category.name}'.",
        'breadcrumbs': breadcrumbs,
        'is_staff_portal': False,
    }
    return render(request, 'LehmanCustomConstruction/blog_category_list.html', context)


def portfolio_list_view(request):
    portfolio_items = PortfolioProject.objects.filter(is_active=True).select_related('category').order_by('order',
                                                                                                          '-created_at')
    portfolio_categories = PortfolioCategory.objects.filter(is_active=True).annotate(
        num_projects=Count('portfolio_projects', filter=Q(portfolio_projects__is_active=True))
    ).filter(num_projects__gt=0).order_by('name')
    context = {
        'portfolio_items': portfolio_items, 'portfolio_categories': portfolio_categories,
        'page_title': 'Our Custom Home Portfolio',
        'meta_description': "View the portfolio of luxury custom homes by Lehman Custom Construction.",
        'breadcrumbs': [{'name': 'Home', 'url': reverse('LehmanCustomConstruction:home')},
                        {'name': 'Portfolio', 'is_active': True}],
        'is_staff_portal': False,
    }
    return render(request, 'LehmanCustomConstruction/portfolio_list.html', context)


def portfolio_detail_view(request, slug):
    project = get_object_or_404(PortfolioProject.objects.select_related('category'), slug=slug, is_active=True)
    breadcrumbs = [
        {'name': 'Home', 'url': reverse('LehmanCustomConstruction:home')},
        {'name': 'Portfolio', 'url': reverse('LehmanCustomConstruction:portfolio_list')},
    ]
    if project.category:
        breadcrumbs.append({'name': project.category.name,
                            'url': reverse('LehmanCustomConstruction:portfolio_projects_by_category',
                                           kwargs={'category_slug': project.category.slug})})
    breadcrumbs.append({'name': Truncator(project.title).chars(40, truncate="..."), 'is_active': True})
    context = {
        'project': project, 'page_title': f"{project.title} - Portfolio",
        'meta_description': project.short_description or f"View details of '{project.title}'.",
        'breadcrumbs': breadcrumbs,
        'is_staff_portal': False,
    }
    return render(request, 'LehmanCustomConstruction/portfolio_detail.html', context)


class PortfolioCategoryListView(ListView):
    model = PortfolioCategory
    template_name = 'LehmanCustomConstruction/portfolio_category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return PortfolioCategory.objects.filter(is_active=True).annotate(
            num_active_projects=Count('portfolio_projects', filter=Q(portfolio_projects__is_active=True))
        ).filter(num_active_projects__gt=0).order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Portfolio Styles & Categories"
        context['meta_description'] = "Browse projects by style."
        context['breadcrumbs'] = [{'name': 'Home', 'url': reverse('LehmanCustomConstruction:home')},
                                  {'name': 'Portfolio', 'url': reverse('LehmanCustomConstruction:portfolio_list')},
                                  {'name': 'Styles', 'is_active': True}]
        context['is_staff_portal'] = False
        return context


class PortfolioProjectsByCategoryView(ListView):
    model = PortfolioProject
    template_name = 'LehmanCustomConstruction/portfolio_projects_by_category.html'
    context_object_name = 'projects'
    paginate_by = 9

    def get_queryset(self):
        self.category = get_object_or_404(PortfolioCategory, slug=self.kwargs['category_slug'], is_active=True)
        return PortfolioProject.objects.filter(category=self.category, is_active=True).select_related(
            'category').order_by('order', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['all_categories_for_sidebar'] = PortfolioCategory.objects.filter(is_active=True).annotate(
            num_active_projects=Count('portfolio_projects', filter=Q(portfolio_projects__is_active=True))
        ).filter(num_active_projects__gt=0).order_by('name')
        context['page_title'] = f"{self.category.name} Projects"
        context['meta_description'] = self.category.description or f"Explore projects in {self.category.name}."
        context['breadcrumbs'] = [{'name': 'Home', 'url': reverse('LehmanCustomConstruction:home')},
                                  {'name': 'Portfolio', 'url': reverse('LehmanCustomConstruction:portfolio_list')},
                                  {'name': 'Styles',
                                   'url': reverse('LehmanCustomConstruction:portfolio_category_list')},
                                  {'name': self.category.name, 'is_active': True}]
        context['is_staff_portal'] = False
        return context


# --- Staff Portal Views ---
@login_required
@user_passes_test(is_office_staff)
def staff_dashboard(request):
    active_customer_count = Customer.objects.filter(is_active=True).count()
    active_project_count = Project.objects.filter(is_active=True).exclude(status='COMP').count()
    new_inquiry_count = ContactInquiry.objects.filter(status='NEW').count()
    context = {
        'page_title': 'Staff Dashboard',
        'active_customer_count': active_customer_count,
        'active_project_count': active_project_count,
        'new_inquiry_count': new_inquiry_count,
        'breadcrumbs': [{'name': 'Staff Portal', 'is_active': True}],
        'is_staff_portal': True,
    }
    return render(request, 'LehmanCustomConstruction/staff/dashboard.html', context)


@login_required
@user_passes_test(is_office_staff)
def staff_customer_list(request):
    customers = Customer.objects.filter(is_active=True).order_by('last_name', 'first_name')
    context = {
        'page_title': 'Manage Customers',
        'customers': customers,
        'breadcrumbs': [{'name': 'Staff Portal', 'url': reverse('LehmanCustomConstruction:staff_dashboard')},
                        {'name': 'Customers', 'is_active': True}],
        'is_staff_portal': True,
    }
    return render(request, 'LehmanCustomConstruction/staff/customer_list.html', context)


@login_required
@user_passes_test(is_office_staff)
def staff_customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    log_form = ActivityLogForm()
    if request.method == 'POST' and 'submit_log_note' in request.POST:
        log_form = ActivityLogForm(request.POST)
        if log_form.is_valid():
            new_note = log_form.save(commit=False)
            new_note.author = request.user
            new_note.customer = customer
            new_note.save()
            messages.success(request, 'Note added.')
            return redirect(reverse('LehmanCustomConstruction:staff_customer_detail', args=[customer_id]))
        else:
            messages.error(request, 'Correct errors in note form.')
    projects = Project.objects.filter(customer=customer).prefetch_related('cost_items__category',
                                                                          'expenses__category').order_by('-start_date',
                                                                                                         '-created_at')
    projects_data = []
    grand_total_budget = Decimal('0.00')
    grand_total_actual = Decimal('0.00')
    for item in projects:
        actual = item.expenses.filter(is_active=True).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        budget = item.total_budget or Decimal('0.00')
        grand_total_budget += budget
        grand_total_actual += actual
        projects_data.append({'project': item, 'actual_cost': actual, 'budget': budget, 'variance': budget - actual,
                              'cost_items': item.cost_items.filter(is_active=True).select_related('category')})
    docs = CustomerDocument.objects.filter(Q(customer=customer) | Q(project__customer=customer),
                                           is_active=True).distinct().order_by('-uploaded_at').select_related('project')
    docs_by_type = defaultdict(list)
    for d_item in docs: docs_by_type[d_item.get_document_type_display()].append(d_item)
    context = {
        'customer': customer, 'projects_data': projects_data, 'grand_total_budget': grand_total_budget,
        'grand_total_actual': grand_total_actual, 'grand_total_variance': grand_total_budget - grand_total_actual,
        'page_title': f'Customer: {customer}', 'documents_by_type': dict(docs_by_type),
        'document_type_choices': CustomerDocument.DOCUMENT_TYPE_CHOICES,
        'activity_logs': ActivityLog.objects.filter(customer=customer).select_related('author').order_by('-timestamp'),
        'log_form': log_form,
        'breadcrumbs': [{'name': 'Staff Portal', 'url': reverse('LehmanCustomConstruction:staff_dashboard')},
                        {'name': 'Customers', 'url': reverse('LehmanCustomConstruction:staff_customer_list')},
                        {'name': Truncator(str(customer)).chars(30, truncate="..."), 'is_active': True}],
        'is_staff_portal': True,
    }
    return render(request, 'LehmanCustomConstruction/staff/customer_detail.html', context)


@login_required
@user_passes_test(is_office_staff)
def staff_project_list(request):
    projects = Project.objects.filter(is_active=True).select_related('customer').order_by('-created_at')
    context = {
        'page_title': 'Manage Internal Projects',
        'projects': projects,
        'breadcrumbs': [{'name': 'Staff Portal', 'url': reverse('LehmanCustomConstruction:staff_dashboard')},
                        {'name': 'Internal Projects', 'is_active': True}],
        'is_staff_portal': True,
    }
    return render(request, 'LehmanCustomConstruction/staff/project_list.html', context)


@login_required
@user_passes_test(is_office_staff)
def staff_project_detail(request, project_id):
    project = get_object_or_404(Project.objects.select_related('customer'), pk=project_id)
    log_form = ActivityLogForm()
    if request.method == 'POST' and 'submit_log_note' in request.POST:
        log_form = ActivityLogForm(request.POST)
        if log_form.is_valid():
            note = log_form.save(commit=False)
            note.author = request.user
            note.project = project
            if project.customer: note.customer = project.customer
            note.save()
            messages.success(request, 'Note added to project.')
            return redirect(reverse('LehmanCustomConstruction:staff_project_detail', args=[project_id]))
        else:
            messages.error(request, 'Correct errors in note form.')
    cost_items = project.cost_items.filter(is_active=True).select_related('category')
    actual_cost = project.expenses.filter(is_active=True).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_budget = project.total_budget or Decimal('0.00')
    project_docs = CustomerDocument.objects.filter(project=project, is_active=True).order_by('-uploaded_at')
    docs_by_type = defaultdict(list)
    for d_item in project_docs: docs_by_type[d_item.get_document_type_display()].append(d_item)
    context = {
        'project': project, 'customer': project.customer, 'cost_items': cost_items,
        'actual_cost': actual_cost, 'budget': total_budget, 'variance': total_budget - actual_cost,
        'page_title': f'Internal Project: {project.project_name}', 'documents_by_type': dict(docs_by_type),
        'document_type_choices': CustomerDocument.DOCUMENT_TYPE_CHOICES,
        'activity_logs': ActivityLog.objects.filter(project=project).select_related('author').order_by('-timestamp'),
        'log_form': log_form,
        'breadcrumbs': [{'name': 'Staff Portal', 'url': reverse('LehmanCustomConstruction:staff_dashboard')},
                        {'name': 'Internal Projects', 'url': reverse('LehmanCustomConstruction:staff_project_list')},
                        {'name': Truncator(project.project_name).chars(30, truncate="..."), 'is_active': True}],
        'is_staff_portal': True,
    }
    return render(request, 'LehmanCustomConstruction/staff/project_detail.html', context)


@login_required
@user_passes_test(is_office_staff)
def staff_portfolio_list(request):
    portfolio_items = PortfolioProject.objects.select_related('category').order_by('order', '-created_at')
    context = {
        'page_title': 'Manage Portfolio Projects',
        'portfolio_items': portfolio_items,
        'breadcrumbs': [{'name': 'Staff Portal', 'url': reverse('LehmanCustomConstruction:staff_dashboard')},
                        {'name': 'Manage Portfolio', 'is_active': True}],
        'is_staff_portal': True,
    }
    return render(request, 'LehmanCustomConstruction/staff/portfolio_list_staff.html', context)


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
                        img.verify()
                        uploaded_file.seek(0)
                    except Exception as e:
                        logger.error(f"Pillow could not verify gallery image {uploaded_file.name}: {e}")
                        messages.error(request, f"File {uploaded_file.name} could not be verified as a valid image.")
                        continue
                PortfolioImage.objects.create(portfolio_project=project_instance, image=uploaded_file, caption='', order=0)
                images_uploaded_count += 1
            messages.success(request, f'Portfolio Project "{project_instance.title}" created successfully.')
            if images_uploaded_count > 0:
                messages.info(request, f'{images_uploaded_count} new gallery image(s) uploaded.')
            return redirect(reverse('LehmanCustomConstruction:staff_manage_portfolio_images', kwargs={'pk': project_instance.pk}))
        else:
            messages.error(request, "Error: Please correct the project details below.")
    else:
        form = StaffPortfolioProjectForm()
        if 'order' in form.fields and hasattr(PortfolioProject(), 'order'):
            max_order = PortfolioProject.objects.aggregate(Max('order'))['order__max']
            form.fields['order'].initial = (max_order or 0) + 1
    context = {
        'form': form, 'project': None,
        'form_title': 'Add New Portfolio Project', 'page_title': 'Add Portfolio Project',
        'breadcrumbs': [
            {'name': 'Staff Portal', 'url': reverse('LehmanCustomConstruction:staff_dashboard')},
            {'name': 'Manage Portfolio', 'url': reverse('LehmanCustomConstruction:staff_portfolio_list')},
            {'name': 'Add Project', 'is_active': True}
        ],
        'is_staff_portal': True,
    }
    return render(request, 'LehmanCustomConstruction/staff/portfolio_project_form.html', context)


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
                PortfolioImage.objects.create(portfolio_project=updated_project, image=uploaded_file, caption='', order=0)
                images_uploaded_count += 1
            messages.success(request, f'Portfolio Project "{updated_project.title}" updated successfully.')
            if images_uploaded_count > 0:
                messages.info(request, f'{images_uploaded_count} new gallery image(s) uploaded.')
            return redirect(reverse('LehmanCustomConstruction:staff_manage_portfolio_images', kwargs={'pk': updated_project.pk}))
        else:
            messages.error(request, "Error: Please correct the project details below.")
    else:
        form = StaffPortfolioProjectForm(instance=project_instance)
    context = {
        'form': form, 'project': project_instance,
        'form_title': f'Edit Portfolio Project: {project_instance.title}',
        'page_title': f'Edit Portfolio: {Truncator(project_instance.title).chars(40)}',
        'breadcrumbs': [
            {'name': 'Staff Portal', 'url': reverse('LehmanCustomConstruction:staff_dashboard')},
            {'name': 'Manage Portfolio', 'url': reverse('LehmanCustomConstruction:staff_portfolio_list')},
            {'name': f'Edit: {Truncator(project_instance.title).chars(30, truncate="...")}', 'is_active': True}
        ],
        'is_staff_portal': True,
    }
    return render(request, 'LehmanCustomConstruction/staff/portfolio_project_form.html', context)


@login_required
@user_passes_test(is_office_staff)
def staff_manage_portfolio_images(request, pk):
    project = get_object_or_404(PortfolioProject, pk=pk)
    PortfolioImageFormSet = modelformset_factory(
        PortfolioImage,
        form=PortfolioImageManagementForm,
        extra=0,
        can_delete=True,
    )
    queryset = PortfolioImage.objects.filter(portfolio_project=project).order_by('order', 'id')
    if request.method == 'POST':
        formset = PortfolioImageFormSet(request.POST, request.FILES, queryset=queryset)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for obj in formset.deleted_objects:
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
                            if project.featured_image:
                                try:
                                    project.featured_image.delete(save=False)
                                except Exception as e_del:
                                    logger.warning(f"Could not delete old featured image {project.featured_image.name}: {e_del}")
                            file_name = os.path.basename(selected_gallery_image.image.name)
                            project.featured_image.save(file_name, ContentFile(selected_gallery_image.image.read()), save=True)
                            messages.success(request, f"Image '{selected_gallery_image.caption or file_name}' set as the featured image.")
                        else:
                            messages.info(request, "Selected image is already the featured image.")
                except (ValueError, PortfolioImage.DoesNotExist):
                    messages.error(request, "Invalid selection or image not found for featured image.")
                except Exception as e:
                    logger.error(f"Error setting featured image for project {project.pk} from image {featured_image_id_str}: {e}")
                    messages.error(request, f"An error occurred while setting the featured image: {e}")
            messages.success(request, 'Gallery image details updated successfully!')
            return redirect(reverse('LehmanCustomConstruction:staff_manage_portfolio_images', kwargs={'pk': project.pk}))
        else:
            messages.error(request, "Please correct errors in the image forms below.")
    else:
        formset = PortfolioImageFormSet(queryset=queryset)
    context = {
        'project': project,
        'formset': formset,
        'form_title': f'Manage Images for: {project.title}',
        'page_title': f'Manage Images: {project.title}',
        'current_featured_image_name': os.path.basename(project.featured_image.name) if project.featured_image else None,
        'breadcrumbs': [
            {'name': 'Staff Portal', 'url': reverse('LehmanCustomConstruction:staff_dashboard')},
            {'name': 'Manage Portfolio', 'url': reverse('LehmanCustomConstruction:staff_portfolio_list')},
            {'name': f'Edit Project: {Truncator(project.title).chars(30, truncate="...")}',
             'url': reverse('LehmanCustomConstruction:staff_portfolio_edit', kwargs={'pk': project.pk})},
            {'name': 'Manage Images', 'is_active': True},
        ],
        'is_staff_portal': True,
    }
    return render(request, 'LehmanCustomConstruction/staff/manage_portfolio_images.html', context)


@login_required
@user_passes_test(is_office_staff)
def portfolio_project_detail_staff(request, pk):
    project = get_object_or_404(PortfolioProject.objects.select_related('category'), pk=pk)
    context = {
        'project': project,
        'page_title': f'Staff View: {project.title}',
        'breadcrumbs': [
            {'name': 'Staff Portal', 'url': reverse('LehmanCustomConstruction:staff_dashboard')},
            {'name': 'Manage Portfolio', 'url': reverse('LehmanCustomConstruction:staff_portfolio_list')},
            {'name': Truncator(project.title).chars(30, truncate="..."), 'is_active': True}
        ],
        'is_staff_portal': True,
    }
    return render(request, 'LehmanCustomConstruction/staff/portfolio_project_detail_staff.html', context)


@login_required
@user_passes_test(is_office_staff)
def staff_portfolio_delete(request, pk):
    project_instance = get_object_or_404(PortfolioProject, pk=pk)
    project_title = project_instance.title
    if request.method == 'POST':
        project_instance.delete()
        messages.success(request, f'Portfolio Project "{project_title}" and its images deleted.')
        return redirect(reverse('LehmanCustomConstruction:staff_portfolio_list'))
    context = {
        'project': project_instance,
        'page_title': f'Confirm Delete: {project_title}',
        'breadcrumbs': [
            {'name': 'Staff Portal', 'url': reverse('LehmanCustomConstruction:staff_dashboard')},
            {'name': 'Manage Portfolio', 'url': reverse('LehmanCustomConstruction:staff_portfolio_list')},
            {'name': f'Delete: {Truncator(project_title).chars(30, truncate="...")}', 'is_active': True}
        ],
        'is_staff_portal': True,
    }
    return render(request, 'LehmanCustomConstruction/staff/portfolio_project_confirm_delete.html', context)


@staff_member_required
def project_expenses_view(request, project_id):
    project_instance = get_object_or_404(Project, pk=project_id)
    expenses = Expense.objects.filter(project=project_instance, is_active=True).order_by(
        '-expense_date').select_related('vendor', 'category')
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    context = {
        'project': project_instance, 'expenses': expenses, 'total_expenses': total_expenses,
        'page_title': f'Expenses for Project: {project_instance.project_name}',
        'breadcrumbs': [{'name': 'Staff Portal', 'url': reverse('LehmanCustomConstruction:staff_dashboard')},
                        {'name': 'Internal Projects', 'url': reverse('LehmanCustomConstruction:staff_project_list')},
                        {'name': Truncator(project_instance.project_name).chars(30, truncate="..."),
                         'url': reverse('LehmanCustomConstruction:staff_project_detail', args=[project_instance.id])},
                        {'name': 'View Expenses', 'is_active': True}],
        'is_staff_portal': True,
    }
    return render(request, 'admin/LehmanCustomConstruction/project/project_expenses.html', context)


@staff_member_required
def admin_customer_dashboard_view(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    admin_url = reverse('admin:LehmanCustomConstruction_customer_change', args=[customer.id])
    return redirect(admin_url)


@staff_member_required
def admin_project_expenses_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    admin_url = reverse('admin:LehmanCustomConstruction_project_change', args=[project.id])
    return redirect(admin_url)


@login_required
@user_passes_test(is_office_staff)
def add_document_to_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    messages.info(request, f"Placeholder for adding document to project {project.project_name} ({project_id})")
    return redirect(reverse('LehmanCustomConstruction:staff_project_detail', args=[project_id]))


@login_required
@user_passes_test(is_office_staff)
def delete_document(request, document_id):
    document = get_object_or_404(CustomerDocument, pk=document_id)
    redirect_url_name = 'LehmanCustomConstruction:staff_dashboard'
    redirect_kwargs = {}
    if document.project:
        redirect_url_name = 'LehmanCustomConstruction:staff_project_detail'
        redirect_kwargs = {'project_id': document.project.id}
    elif document.customer:
        redirect_url_name = 'LehmanCustomConstruction:staff_customer_detail'
        redirect_kwargs = {'customer_id': document.customer.id}
    doc_name = document.get_filename()
    try:
        document.delete()
        messages.success(request, f"Document '{doc_name}' deleted.")
    except Exception as e:
        logger.error(f"Error deleting document '{doc_name}': {e}")
        messages.error(request, f"Error deleting document '{doc_name}'.")
    return redirect(reverse(redirect_url_name, kwargs=redirect_kwargs) if redirect_kwargs else reverse(redirect_url_name))


@login_required
@user_passes_test(is_office_staff)
def add_expense_to_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.project = project
            uploaded_receipt = form.cleaned_data.get('receipt_upload')
            if uploaded_receipt:
                CustomerDocument.objects.create(
                    project=project,
                    customer=project.customer,
                    file=uploaded_receipt,
                    document_type='RECEIPT',
                    description=f"Receipt for expense on {expense.expense_date or timezone.now().date()}"
                )
            expense.save()
            messages.success(request, "Expense added.")
            return redirect(reverse('LehmanCustomConstruction:staff_project_detail', args=[project_id]))
        else:
            messages.error(request, "Error adding expense.")
    else:
        form = ExpenseForm(initial={'project': project})
    context = {
        'form': form, 'project': project,
        'page_title': f'Add Expense to {project.project_name}',
        'breadcrumbs': [{'name': 'Staff Portal', 'url': reverse('LehmanCustomConstruction:staff_dashboard')},
                        {'name': 'Internal Projects', 'url': reverse('LehmanCustomConstruction:staff_project_list')},
                        {'name': Truncator(project.project_name).chars(30, truncate="..."),
                         'url': reverse('LehmanCustomConstruction:staff_project_detail', args=[project_id])},
                        {'name': 'Add Expense', 'is_active': True}],
        'is_staff_portal': True,
    }
    return render(request, 'LehmanCustomConstruction/staff/expense_form.html', context)


@login_required
@user_passes_test(is_office_staff)
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, pk=expense_id)
    project_id = expense.project.id
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, "Expense updated.")
            return redirect(reverse('LehmanCustomConstruction:staff_project_detail', args=[project_id]))
        else:
            messages.error(request, "Error updating expense.")
    else:
        form = ExpenseForm(instance=expense)
    context = {
        'form': form, 'expense': expense, 'project': expense.project,
        'page_title': f'Edit Expense for {expense.project.project_name}',
        'breadcrumbs': [{'name': 'Staff Portal', 'url': reverse('LehmanCustomConstruction:staff_dashboard')},
                        {'name': 'Internal Projects', 'url': reverse('LehmanCustomConstruction:staff_project_list')},
                        {'name': Truncator(expense.project.project_name).chars(30, truncate="..."),
                         'url': reverse('LehmanCustomConstruction:staff_project_detail', args=[project_id])},
                        {'name': 'Edit Expense', 'is_active': True}],
        'is_staff_portal': True,
    }
    return render(request, 'LehmanCustomConstruction/staff/expense_form.html', context)


@login_required
@user_passes_test(is_office_staff)
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, pk=expense_id)
    project_id = expense.project.id
    if request.method == 'POST':
        desc = expense.description or f"Expense ID {expense.id}"
        expense.delete()
        messages.success(request, f"Expense '{desc}' deleted.")
        return redirect(reverse('LehmanCustomConstruction:staff_project_detail', args=[project_id]))
    context = {
        'expense': expense, 'project': expense.project,
        'page_title': f'Confirm Delete Expense for {expense.project.project_name}',
        'breadcrumbs': [{'name': 'Staff Portal', 'url': reverse('LehmanCustomConstruction:staff_dashboard')},
                        {'name': 'Internal Projects', 'url': reverse('LehmanCustomConstruction:staff_project_list')},
                        {'name': Truncator(expense.project.project_name).chars(30, truncate="..."),
                         'url': reverse('LehmanCustomConstruction:staff_project_detail', args=[project_id])},
                        {'name': 'Delete Expense', 'is_active': True}],
        'is_staff_portal': True,
    }
    return render(request, 'LehmanCustomConstruction/staff/expense_confirm_delete.html', context)


@login_required
@user_passes_test(is_office_staff)
def add_budget_line_item(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    messages.info(request, f"Placeholder for adding budget item to project {project.project_name}")
    return redirect(reverse('LehmanCustomConstruction:staff_project_detail', args=[project_id]))


@login_required
@user_passes_test(is_office_staff)
def edit_budget_line_item(request, item_id):
    item = get_object_or_404(CostItem, pk=item_id)
    project_id = item.project.id
    messages.info(request, f"Placeholder for editing budget item {item.description}")
    return redirect(reverse('LehmanCustomConstruction:staff_project_detail', args=[project_id]))


@login_required
@user_passes_test(is_office_staff)
def delete_budget_line_item(request, item_id):
    item = get_object_or_404(CostItem, pk=item_id)
    project_id = item.project.id
    if request.method == 'POST':
        desc = item.description
        item.delete()
        messages.success(request, f"Budget item '{desc}' deleted.")
        return redirect(reverse('LehmanCustomConstruction:staff_project_detail', args=[project_id]))
    context = {
        'item': item, 'project': item.project,
        'page_title': f'Confirm Delete Budget Item for {item.project.project_name}',
        'breadcrumbs': [{'name': 'Staff Portal', 'url': reverse('LehmanCustomConstruction:staff_dashboard')},
                        {'name': 'Internal Projects', 'url': reverse('LehmanCustomConstruction:staff_project_list')},
                        {'name': Truncator(item.project.project_name).chars(30, truncate="..."),
                         'url': reverse('LehmanCustomConstruction:staff_project_detail', args=[project_id])},
                        {'name': 'Delete Budget Item', 'is_active': True}],
        'is_staff_portal': True,
    }
    return render(request, 'LehmanCustomConstruction/staff/costitem_confirm_delete.html', context)

# --- Staff User Profile Views ---
@login_required
@user_passes_test(is_office_staff)
def staff_user_profile(request):
    user_object = request.user
    context = {
        'page_title': 'My Profile',
        'user_profile': user_object,
        'is_staff_portal': True,
        'breadcrumbs': [
            {'name': 'Staff Portal', 'url': reverse('LehmanCustomConstruction:staff_dashboard')},
            {'name': 'My Profile', 'is_active': True}
        ]
    }
    return render(request, 'LehmanCustomConstruction/staff/staff_user_profile.html', context)

@login_required
@user_passes_test(is_office_staff)
def staff_user_profile_edit(request):
    if request.method == 'POST':
        form = StaffUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect(reverse('LehmanCustomConstruction:staff_user_profile'))
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StaffUserChangeForm(instance=request.user)

    context = {
        'page_title': 'Edit My Profile',
        'form': form,
        'is_staff_portal': True,
        'breadcrumbs': [
            {'name': 'Staff Portal', 'url': reverse('LehmanCustomConstruction:staff_dashboard')},
            {'name': 'My Profile', 'url': reverse('LehmanCustomConstruction:staff_user_profile')},
            {'name': 'Edit', 'is_active': True}
        ]
    }
    return render(request, 'LehmanCustomConstruction/staff/staff_user_profile_edit.html', context)
# portfolio_app/urls.py
from django.urls import path
from . import views

app_name = 'portfolio_app'  # This is crucial for namespacing

urlpatterns = [
    # --- Public Site URLs ---
    path('', views.home, name='home'),
    path('about/', views.about_us, name='about_us'),  # For your "About Me" page
    path('contact/', views.contact_us, name='contact_us'),  # Page to host your React contact form

    path('blog/', views.blog_list, name='blog_list'),
    path('blog/category/<slug:slug>/', views.blog_category_list, name='blog_category_list'),
    path('blog/<slug:slug>/', views.blog_post_detail, name='blog_post_detail'),

    # --- URL for your React-based Portfolio Showcase ---
    path('portfolio/', views.portfolio_showcase_react, name='portfolio_showcase_react'),

    # --- API URLs for React ---
    path('api/portfolio-projects/', views.api_portfolio_projects, name='api_portfolio_projects'),
    path('api/portfolio-categories/', views.api_portfolio_categories, name='api_portfolio_categories'),
    path('api/contact-submit/', views.api_contact_submit, name='api_contact_submit'),  # For React contact form

    # --- Staff Portal URLs ---
    path('staff/', views.staff_dashboard, name='staff_dashboard'),  # For your admin/content management
    path('staff/profile/', views.staff_user_profile, name='staff_user_profile'),
    path('staff/profile/edit/', views.staff_user_profile_edit, name='staff_user_profile_edit'),

    # Staff Portfolio Project Management (for your Coding Projects)
    path('staff/coding-projects/', views.staff_portfolio_list, name='staff_portfolio_list'),
    path('staff/coding-projects/add/', views.staff_portfolio_add, name='staff_portfolio_add'),
    path('staff/coding-projects/<int:pk>/edit/', views.staff_portfolio_edit, name='staff_portfolio_edit'),
    path('staff/coding-projects/<int:pk>/detail/', views.portfolio_project_detail_staff,
         name='portfolio_project_detail_staff'),
    path('staff/coding-projects/<int:pk>/delete/', views.staff_portfolio_delete, name='staff_portfolio_delete'),
    path('staff/coding-projects/<int:pk>/manage-images/', views.staff_manage_portfolio_images,
         name='staff_manage_portfolio_images'),
    path('react-minimal-test/', views.react_test_minimal_view, name='react_test_minimal'),

    # --- Commented out URLs for features you might not need for a personal portfolio ---
    # --- Review and remove these if you've removed the corresponding models and views ---

    # # Staff Customer Management (If you manage freelance clients this way)
    # path('staff/clients/', views.staff_client_list, name='staff_client_list'),
    # path('staff/clients/<int:customer_id>/', views.staff_client_detail, name='staff_client_detail'),

    # # Staff Internal Project Management (If you manage larger freelance projects with financials this way)
    # path('staff/client-projects/', views.staff_internal_project_list, name='staff_internal_project_list'),
    # path('staff/client-projects/<int:project_id>/', views.staff_internal_project_detail, name='staff_internal_project_detail'),
    #
    # # Staff Action URLs (Mostly tied to the old 'Project' model)
    # path('staff/client-projects/<int:project_id>/add_document/', views.add_document_to_project, name='add_document_to_project'),
    # path('staff/documents/<int:document_id>/delete/', views.delete_document, name='delete_document'),
    # path('staff/client-projects/<int:project_id>/add_expense/', views.add_expense_to_project, name='add_expense_to_project'),
    # path('staff/expenses/<int:expense_id>/edit/', views.edit_expense, name='edit_expense'),
    # path('staff/expenses/<int:expense_id>/delete/', views.delete_expense, name='delete_expense'),
    # path('staff/client-projects/<int:project_id>/add_budget_item/', views.add_budget_line_item, name='add_budget_line_item'),
    # path('staff/budget_item/<int:item_id>/edit/', views.edit_budget_line_item, name='edit_budget_line_item'),
    # path('staff/budget_item/<int:item_id>/delete/', views.delete_budget_line_item, name='delete_budget_line_item'),

    # --- Admin-Related URLs (Redirects to Django Admin - only keep if models exist) ---
    # path('admin-dashboard/customer/<int:customer_id>/', views.admin_customer_dashboard_view, name='admin_customer_dashboard'),
    # path('admin-dashboard/project-expenses/<int:project_id>/', views.admin_project_expenses_view, name='admin_project_expenses_redirect'),
    # path('admin-custom/project/<int:project_id>/expenses/', views.project_expenses_view, name='project_expenses_view_custom_admin'),
]
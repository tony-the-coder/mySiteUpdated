# portfolio_app/urls.py
from django.urls import path
from . import views

app_name = 'portfolio_app'

urlpatterns = [
    # --- Public Site URLs ---
    path('', views.home, name='home'),
    path('about/', views.about_us, name='about_us'),
    path('contact/', views.contact_us, name='contact_us'),

    path('blog/', views.blog_list, name='blog_list'),
    path('blog/category/<slug:slug>/', views.blog_category_list, name='blog_category_list'),
    path('blog/<slug:slug>/', views.blog_post_detail, name='blog_post_detail'),

    path('portfolio/styles/', views.PortfolioCategoryListView.as_view(), name='portfolio_category_list'),
    path('portfolio/styles/<slug:category_slug>/', views.PortfolioProjectsByCategoryView.as_view(), name='portfolio_projects_by_category'),
    path('portfolio/', views.portfolio_list_view, name='portfolio_list'),
    path('portfolio/<slug:slug>/', views.portfolio_detail_view, name='portfolio_detail'),

    # --- Staff Portal URLs ---
    path('staff/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/profile/', views.staff_user_profile, name='staff_user_profile'),
    path('staff/profile/edit/', views.staff_user_profile_edit, name='staff_user_profile_edit'), # <-- NEW URL FOR EDITING

    # Staff Customer Management
    path('staff/customers/', views.staff_customer_list, name='staff_customer_list'),
    path('staff/customers/<int:customer_id>/', views.staff_customer_detail, name='staff_customer_detail'),

    # Staff Internal Project Management (models.Project)
    path('staff/projects/', views.staff_project_list, name='staff_project_list'),
    path('staff/projects/<int:project_id>/', views.staff_project_detail, name='staff_project_detail'),

    # Staff Portfolio Project Management (models.PortfolioProject)
    path('staff/portfolio/', views.staff_portfolio_list, name='staff_portfolio_list'),
    path('staff/portfolio/add/', views.staff_portfolio_add, name='staff_portfolio_add'),
    path('staff/portfolio/<int:pk>/edit/', views.staff_portfolio_edit, name='staff_portfolio_edit'),
    path('staff/portfolio/<int:pk>/detail/', views.portfolio_project_detail_staff, name='portfolio_project_detail_staff'),
    path('staff/portfolio/<int:pk>/delete/', views.staff_portfolio_delete, name='staff_portfolio_delete'),
    path('staff/portfolio/<int:pk>/manage-images/', views.staff_manage_portfolio_images, name='staff_manage_portfolio_images'),

    # Staff Action URLs (for internal Project model)
    path('staff/projects/<int:project_id>/add_document/', views.add_document_to_project, name='add_document_to_project'),
    path('staff/documents/<int:document_id>/delete/', views.delete_document, name='delete_document'),
    path('staff/projects/<int:project_id>/add_expense/', views.add_expense_to_project, name='add_expense_to_project'),
    path('staff/expenses/<int:expense_id>/edit/', views.edit_expense, name='edit_expense'),
    path('staff/expenses/<int:expense_id>/delete/', views.delete_expense, name='delete_expense'),
    path('staff/projects/<int:project_id>/add_budget_item/', views.add_budget_line_item, name='add_budget_line_item'),
    path('staff/budget_item/<int:item_id>/edit/', views.edit_budget_line_item, name='edit_budget_line_item'),
    path('staff/budget_item/<int:item_id>/delete/', views.delete_budget_line_item, name='delete_budget_line_item'),

    # --- Admin-Related URLs (Redirects to Django Admin) ---
    path('admin-dashboard/customer/<int:customer_id>/', views.admin_customer_dashboard_view, name='admin_customer_dashboard'),
    path('admin-dashboard/project-expenses/<int:project_id>/', views.admin_project_expenses_view, name='admin_project_expenses_redirect'),

    # --- Custom Admin View (Example, as per your file) ---
    path('admin-custom/project/<int:project_id>/expenses/', views.project_expenses_view, name='project_expenses_view_custom_admin'),
]
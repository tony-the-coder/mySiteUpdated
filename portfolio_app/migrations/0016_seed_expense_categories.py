# LehmanCustomConstruction/migrations/00XX_seed_expense_categories.py
# (Replace 00XX with the actual number generated)

from django.db import migrations

# List of category names from your spreadsheet
# Note: Removed trailing colons and slightly adjusted names for clarity
EXPENSE_CATEGORIES = [
    "Permits/ Misc",
    "Grading",
    "Portable toilets",
    "Termite treatment",
    "Trash removal",
    "Septic tank",
    "Foundation",
    "Framing",
    "Windows/ Doors",
    "Roofing/ gutters",
    "Exterior Finish",
    "Electrical Rough/ Trim",
    "Plumbing rough/ Trim",
    "HVAC mechanical",
    "Insulation",
    "Sheetrock",
    "Interior Trim/ Stairs",
    "Paint Interior and exterior",
    "Cabinets",
    "Hardwood Flooring/ Carpet",
    "Ceramic Tile",
    "Door hardware",
    "Garage doors",
    "Concrete",
    "Landscaping",
    "Lights (interior and exterior)",
    "Plumbing fixtures",
    "Shelving/ Towel bars, mirrors shower",
    "Counter tops",
    # Add any other base categories here
]

def create_initial_categories(apps, schema_editor):
    """Creates the initial ExpenseCategory instances."""
    # We get the model from the versioned app registry;
    # avoids importing directly which can cause issues.
    ExpenseCategory = apps.get_model('LehmanCustomConstruction', 'ExpenseCategory')
    db_alias = schema_editor.connection.alias

    category_instances = [
        ExpenseCategory(name=name) for name in EXPENSE_CATEGORIES
    ]

    # Use bulk_create for efficiency, ignoring conflicts if they somehow already exist
    ExpenseCategory.objects.using(db_alias).bulk_create(category_instances, ignore_conflicts=True)

    # Or use update_or_create if you prefer to ensure they exist or update description later
    # for category_name in EXPENSE_CATEGORIES:
    #     ExpenseCategory.objects.using(db_alias).update_or_create(
    #         name=category_name,
    #         defaults={'description': ''} # Optional: set a default description
    #     )


def remove_initial_categories(apps, schema_editor):
    """Removes the categories if the migration is reversed (optional but good practice)."""
    ExpenseCategory = apps.get_model('LehmanCustomConstruction', 'ExpenseCategory')
    db_alias = schema_editor.connection.alias
    ExpenseCategory.objects.using(db_alias).filter(name__in=EXPENSE_CATEGORIES).delete()


class Migration(migrations.Migration):

    # === IMPORTANT: CHECK DEPENDENCIES ===
    # This migration needs to run *after* the migration that created the
    # ExpenseCategory model. Look in your migrations folder - find the name
    # of the file that created ExpenseCategory (e.g., 0004_expensecategory.py)
    # and put its prefix here. Adjust '0004' if needed.
    # Also add dependency for the CostItem rename if applicable.
    dependencies = [
        # Replace '0004_expensecategory' with the actual name of your migration file
        ('LehmanCustomConstruction', '0004_expensecategory'),
        # Add the migration that renamed BudgetLineItem if it exists, e.g.:
        # ('LehmanCustomConstruction', '0016_rename_budget_to_costitem'), #<-- ADJUST NAME/NUMBER
    ]
    # =====================================

    operations = [
        # Run the Python function to create categories
        migrations.RunPython(create_initial_categories, reverse_code=remove_initial_categories),
    ]

from azure import functions as func
from functions.timesheets.syncronize_timesheets import bp as timesheets_bp
from functions.customers.syncronize_customers import bp as customers_bp
from functions.employees.syncronize_employees import bp as employees_bp
from functions.projects.syncronize_projects import bp as projects_bp


# Create the function app.
app = func.FunctionApp()

# Register all the functions here for the app.
app.register_blueprint(timesheets_bp)
app.register_blueprint(customers_bp)
app.register_blueprint(employees_bp)
app.register_blueprint(projects_bp)
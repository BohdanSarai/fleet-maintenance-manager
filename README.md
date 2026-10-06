# Fleet Maintenance Manager

Fleet Maintenance Manager is a Django web application designed for managing a company's vehicle fleet and keeping track of vehicle maintenance.

The system allows a company to store its vehicles, monitor their current mileage, create maintenance plans, and keep a history of completed service work. Maintenance plans can be based on mileage, time intervals, or both. The dashboard shows upcoming maintenance and helps identify vehicles that require service.

The application also includes tire management. Tire sets can be registered separately and installed on vehicles. The system keeps the installation and replacement history and calculates the mileage of each tire set based on the distance traveled by the vehicle while the tires were installed.

Service records contain information about completed maintenance, including the vehicle, maintenance plan, date, mileage, cost, notes, and the employee who created the record.

The application has a custom user model with two access levels. The owner can manage company employees, while regular employees can work with the fleet and maintenance data.

Vehicle, maintenance plan, and service history pages support search. Lists with larger amounts of data use pagination.

## Live Demo

The deployed application is available at:

https://fleet-maintenance-manager.onrender.com

> The application is hosted on a free Render instance, so the first request after a period of inactivity may take up to a minute.

### Demo Accounts

**Owner**

- Username: `demo.owner`
- Password: `FleetDemo2026!`

The owner has access to employee management in addition to the fleet and maintenance functionality.

**Employee**

- Username: `demo.employee`
- Password: `FleetDemo2026!`

The employee can work with fleet and maintenance data but does not have access to employee management.

## Main Features

- Vehicle management and mileage tracking
- Maintenance plans based on mileage and/or time
- Upcoming maintenance reminders
- Service history with costs and notes
- Tire set management and mileage calculation
- Tire installation and replacement history
- Employee management
- Owner and employee access levels
- Authentication
- Search and pagination

## Technologies

The project is built with Python and Django. Django ORM is used to work with the database.

SQLite is used during local development, while the deployed application uses PostgreSQL.

The user interface is built with Bootstrap 5. Django forms are rendered using django-crispy-forms and crispy-bootstrap5.

Gunicorn is used as the production WSGI server, and WhiteNoise is used for serving static files.

The application is deployed on Render.

Code style is checked with Flake8 and additional Flake8 plugins.

## Database Structure

The project contains six main models:

- CompanyUser
- Vehicle
- MaintenancePlan
- ServiceRecord
- TireSet
- TireInstallation

The database diagram shows the relationships between these models.

![Database structure](docs/database-diagram.png)

The editable draw.io version of the diagram is available at `docs/database-diagram.drawio`.

## Running the Project

Clone the repository:

```bash
git clone https://github.com/BohdanSarai/fleet-maintenance-manager.git
```

Go to the project directory:

```bash
cd fleet-maintenance-manager
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment and install the dependencies:

```bash
pip install -r requirements.txt
```

Apply database migrations:

```bash
python manage.py migrate
```

Run the development server:

```bash
python manage.py runserver
```

## Tests and Code Quality

Run the project tests with:

```bash
python manage.py test
```

Check the code with Flake8:

```bash
flake8
```

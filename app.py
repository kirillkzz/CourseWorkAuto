from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from app.database import db
from app.models import RouteSheet, Driver, Vehicle, Route, User
from app.services.cache_service import CacheService
from datetime import date
import math

app = Flask(
    __name__,
    template_folder='app/templates',
    static_folder='app/static'
)
app.secret_key = 'super_secret_key_for_coursework'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Будь ласка, увійдіть у систему для доступу."
login_manager.login_message_category = "warning"

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

db.initialize()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.get_by_username(username)

        if user and user.check_password(password):
            login_user(user)
            flash(f'Вітаємо, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Невірний логін або пароль.', 'danger')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.get_by_username(username):
            flash('Користувач з таким логіном вже існує!', 'danger')
        else:
            User.create(username, password)
            flash('Реєстрація успішна! Тепер ви можете увійти.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Ви вийшли з системи.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    try:
        stats = {
            'drivers_count': Driver.count(),
            'vehicles_count': Vehicle.count(),
            'routes_count': Route.count(),
            'sheets_count': RouteSheet.count(),
            'total_fuel': RouteSheet.get_total_fuel()
        }
        recent_actions = CacheService.get_recent_actions()
        return render_template('dashboard.html', stats=stats, recent_actions=recent_actions)
    except Exception as e:
        return render_template('base.html', content=f"<div class='alert alert-danger'>Помилка Dashboard: {e}</div>")

@app.route('/reports')
@login_required
def reports():
    try:
        sort_by = request.args.get('sort', 'sheet_date')
        sort_order = request.args.get('order', 'desc')
        vehicle_filter = request.args.get('vehicle')
        route_filter = request.args.get('route')

        page = request.args.get('page', 1, type=int)
        per_page = 5
        offset = (page - 1) * per_page
        next_order = 'asc' if sort_order == 'desc' else 'desc'

        use_cache = (page == 1 and
                     sort_by == 'sheet_date' and
                     sort_order == 'desc' and
                     not vehicle_filter and
                     not route_filter)

        if use_cache:
            cached_data = CacheService.get_report()
            if cached_data:
                total_rows = len(cached_data)
                reports = cached_data[offset: offset + per_page]
                source = "Redis"
            else:
                all_raw_data, total_rows = RouteSheet.get_full_report(
                    sort_by, sort_order, vehicle_filter, route_filter, limit=None, offset=0
                )
                all_reports = [dict(row) for row in all_raw_data]
                CacheService.save_report(all_reports, ttl=30)
                reports = all_reports[offset: offset + per_page]
                source = "PostgreSQL"
        else:
            raw_reports, total_rows = RouteSheet.get_full_report(
                sort_by, sort_order, vehicle_filter, route_filter, limit=per_page, offset=offset
            )
            reports = [dict(row) for row in raw_reports]
            source = "PostgreSQL"

        total_pages = math.ceil(total_rows / per_page)
        vehicles = Vehicle.get_all_with_drivers()
        routes = Route.get_all()

        return render_template('index.html',
                               reports=reports,
                               source=source,
                               vehicles=vehicles,
                               routes=routes,
                               current_sort=sort_by,
                               current_order=sort_order,
                               next_order=next_order,
                               current_vehicle=vehicle_filter,
                               current_route=route_filter,
                               page=page,
                               total_pages=total_pages)
    except Exception as e:
        return f"<div class='alert alert-danger'>Помилка reports: {e}</div>"

@app.route('/drivers')
@login_required
def drivers_list():
    search_query = request.args.get('q')
    if search_query:
        drivers = Driver.search(search_query)
    else:
        drivers = Driver.get_all()
    return render_template('drivers.html', drivers=drivers)

@app.route('/vehicles')
@login_required
def vehicles_list():
    vehicles = Vehicle.get_all_with_drivers()
    return render_template('vehicles.html', vehicles=vehicles)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_sheet(id):
    sheet = RouteSheet.get_by_id(id)
    if not sheet:
        flash('Запис не знайдено!', 'danger')
        return redirect(url_for('reports'))

    if request.method == 'POST':
        try:
            sheet_date = request.form['sheet_date']
            vehicle_id = int(request.form['vehicle_id'])
            route_number = request.form['route_number']
            fuel = float(request.form['fuel'])

            if fuel < 0 or fuel > 500:
                flash(f'Помилка: Витрата {fuel} л нереалістична.', 'danger')
                return redirect(url_for('edit_sheet', id=id))

            if RouteSheet.is_vehicle_busy(vehicle_id, sheet_date, exclude_sheet_id=id):
                flash('Помилка: Авто зайняте в цей день!', 'danger')
                return redirect(url_for('edit_sheet', id=id))

            RouteSheet.update(id, sheet_date, vehicle_id, route_number, fuel)
            CacheService.clear_report_cache()
            CacheService.log_action(f"{current_user.username}: Редагування рейсу #{id}")
            flash('Запис оновлено!', 'success')
            return redirect(url_for('reports'))

        except Exception as e:
            flash(f'Помилка: {e}', 'danger')

    vehicles = Vehicle.get_all_with_drivers()
    routes = Route.get_all()

    sheet_dict = dict(sheet)
    if hasattr(sheet['sheet_date'], 'strftime'):
        sheet_dict['sheet_date'] = sheet['sheet_date'].strftime('%Y-%m-%d')
    else:
        sheet_dict['sheet_date'] = str(sheet['sheet_date'])

    return render_template('edit_sheet.html', sheet=sheet_dict, vehicles=vehicles, routes=routes)


@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_sheet(id):
    try:
        RouteSheet.delete(id)
        CacheService.clear_report_cache()
        CacheService.log_action(f"{current_user.username}: Видалення рейсу #{id}")
        flash('Запис видалено!', 'warning')
    except Exception as e:
        flash(f'Помилка: {e}', 'danger')
    return redirect(url_for('reports'))


@app.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        try:
            sheet_date = request.form['sheet_date']
            vehicle_id = int(request.form['vehicle_id'])
            route_number = request.form['route_number']
            fuel = float(request.form['fuel'])

            if fuel > 500:
                flash('Помилка: Занадто велика витрата (>500)!', 'danger')
                return redirect(url_for('create'))

            if RouteSheet.is_vehicle_busy(vehicle_id, sheet_date):
                flash('Помилка: Авто зайняте!', 'danger')
                return redirect(url_for('create'))

            RouteSheet.create(sheet_date, vehicle_id, route_number, fuel)
            CacheService.clear_report_cache()
            CacheService.log_action(f"{current_user.username}: Створено новий рейс")

            flash('Запис додано!', 'success')
            return redirect(url_for('reports'))

        except Exception as e:
            flash(f'Помилка: {e}', 'danger')

    try:
        vehicles = Vehicle.get_all_with_drivers()
        routes = Route.get_all()
        today = date.today().strftime('%Y-%m-%d')
        return render_template('create_sheet.html', vehicles=vehicles, routes=routes, today=today)
    except Exception as e:
        return f"Помилка: {e}"


@app.route('/drivers/add', methods=['GET', 'POST'])
@login_required
def add_driver():
    if request.method == 'POST':
        try:
            Driver.create(request.form['full_name'], request.form['phone'], request.form['address'])
            flash('Водія додано!', 'success')
            return redirect(url_for('drivers_list'))
        except Exception as e:
            flash(f'Помилка: {e}', 'danger')
    return render_template('add_driver.html')


@app.route('/vehicles/add', methods=['GET', 'POST'])
@login_required
def add_vehicle():
    if request.method == 'POST':
        try:
            Vehicle.create(request.form['license_plate'], request.form['model'], request.form['driver_id'])
            flash('Авто додано!', 'success')
            return redirect(url_for('vehicles_list'))
        except Exception as e:
            flash(f'Помилка: {e}', 'danger')
    drivers = Driver.get_all()
    return render_template('add_vehicle.html', drivers=drivers)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
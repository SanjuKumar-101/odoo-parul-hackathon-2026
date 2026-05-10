from flask import Blueprint, render_template, request, jsonify
from app import mysql

search_bp = Blueprint('search', __name__)

@search_bp.route('/search/cities')
def search_cities():
    query = request.args.get('q', '').strip()
    region = request.args.get('region', '').strip()
    cur = mysql.connection.cursor()
    # Always return all cities — filtering is done client-side
    cur.execute("SELECT * FROM cities ORDER BY popularity DESC")
    cities = cur.fetchall()
    cur.execute("SELECT DISTINCT region FROM cities WHERE region IS NOT NULL ORDER BY region ASC")
    regions = [r['region'] for r in cur.fetchall()]
    cur.close()
    return render_template('search/cities.html', cities=cities, regions=regions,
                           query=query, selected_region=region)

@search_bp.route('/api/cities')
def api_cities():
    """JSON endpoint for live city search dropdown"""
    q = request.args.get('q', '').strip()
    if len(q) < 1:
        return jsonify([])
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, name, country, region FROM cities
        WHERE name LIKE %s ORDER BY popularity DESC LIMIT 8
    """, (f'%{q}%',))
    cities = cur.fetchall()
    cur.close()
    return jsonify(cities)

@search_bp.route('/api/cities/validate')
def validate_city():
    """Check if a city name exists in our database"""
    name = request.args.get('name', '').strip()
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM cities WHERE LOWER(name) = LOWER(%s)", (name,))
    exists = cur.fetchone() is not None
    cur.close()
    return jsonify({'exists': exists})

@search_bp.route('/search/activities')
def search_activities():
    query = request.args.get('q', '').strip()
    city_id = request.args.get('city_id', '').strip()
    category = request.args.get('category', '').strip()
    cur = mysql.connection.cursor()

    sql = """
        SELECT a.*, c.name as city_name FROM activities a
        JOIN cities c ON a.city_id = c.id WHERE 1=1
    """
    params = []
    if query:
        sql += " AND a.name LIKE %s"
        params.append(f'%{query}%')
    if city_id:
        sql += " AND a.city_id = %s"
        params.append(city_id)
    if category:
        sql += " AND a.category = %s"
        params.append(category)
    sql += " ORDER BY a.cost ASC"

    cur.execute(sql, params)
    activities = cur.fetchall()

    cur.execute("SELECT DISTINCT category FROM activities WHERE category IS NOT NULL")
    categories = [r['category'] for r in cur.fetchall()]

    cur.execute("SELECT id, name FROM cities ORDER BY name")
    cities = cur.fetchall()
    cur.close()

    return render_template('search/activities.html', activities=activities,
                           categories=categories, cities=cities,
                           query=query, selected_city=city_id, selected_category=category)

from flask import Blueprint, redirect, url_for
from utils.decorators import login_required

budget_bp = Blueprint('budget', __name__)

# Budget is now part of the combined itinerary/view page
# This redirect ensures any old links still work
@budget_bp.route('/trips/<int:trip_id>/budget')
@login_required
def view(trip_id):
    return redirect(url_for('itinerary.view', trip_id=trip_id) + '#budget')

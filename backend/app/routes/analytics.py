"""
routes/analytics.py — Visitor tracking and analytics dashboard endpoints.
"""

from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from app import db
from app.models import AnalyticsEvent

analytics_bp = Blueprint('analytics', __name__)


# ─────────────────────────────────────────────
# POST /api/analytics/track
# ─────────────────────────────────────────────
@analytics_bp.route('/track', methods=['POST'])
def track_event():
    """Record a page view event from the frontend."""
    data = request.get_json() or {}
    
    # Parse user agent for device type
    ua = request.headers.get('User-Agent', '')
    device_type = _parse_device(ua)
    
    # Get IP (handle proxies from Render/Vercel)
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip:
        ip = ip.split(',')[0].strip()
    
    event = AnalyticsEvent(
        page=data.get('page', '/'),
        session_id=data.get('session_id', ''),
        ip_address=ip,
        user_agent=ua[:500],
        referrer=data.get('referrer', ''),
        duration=data.get('duration', 0),
        device_type=device_type,
    )
    
    db.session.add(event)
    db.session.commit()
    
    return jsonify({'message': 'Event tracked'}), 201


# ─────────────────────────────────────────────
# GET /api/analytics/summary
# ─────────────────────────────────────────────
@analytics_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_summary():
    """Get analytics summary for the admin dashboard."""
    # Date range (default: last 30 days)
    days = request.args.get('days', 30, type=int)
    since = datetime.utcnow() - timedelta(days=days)
    
    all_events = AnalyticsEvent.query.filter(AnalyticsEvent.created_at >= since).all()
    all_time = AnalyticsEvent.query.count()
    
    total_visits = len(all_events)
    unique_sessions = len(set(e.session_id for e in all_events if e.session_id))
    avg_duration = (
        sum(e.duration or 0 for e in all_events) / total_visits
        if total_visits > 0 else 0
    )
    
    # Page breakdown
    page_counts = {}
    for e in all_events:
        page = e.page or '/'
        page_counts[page] = page_counts.get(page, 0) + 1
    
    top_pages = sorted(page_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Device breakdown
    device_counts = {}
    for e in all_events:
        dt = e.device_type or 'desktop'
        device_counts[dt] = device_counts.get(dt, 0) + 1
    
    # Daily visits for chart (last 7 days)
    daily_visits = _get_daily_visits(7)
    
    return jsonify({
        'summary': {
            'total_visits': total_visits,
            'all_time_visits': all_time,
            'unique_sessions': unique_sessions,
            'avg_duration_seconds': round(avg_duration),
            'period_days': days,
        },
        'top_pages': [{'page': p, 'visits': c} for p, c in top_pages],
        'device_breakdown': device_counts,
        'daily_visits': daily_visits,
    }), 200


# ─────────────────────────────────────────────
# GET /api/analytics/pages
# ─────────────────────────────────────────────
@analytics_bp.route('/pages', methods=['GET'])
@jwt_required()
def get_page_analytics():
    """Get per-page visit analytics."""
    results = (
        db.session.query(
            AnalyticsEvent.page,
            func.count(AnalyticsEvent.id).label('visits'),
            func.avg(AnalyticsEvent.duration).label('avg_duration'),
        )
        .group_by(AnalyticsEvent.page)
        .order_by(func.count(AnalyticsEvent.id).desc())
        .all()
    )
    
    return jsonify({
        'pages': [
            {
                'page': r.page,
                'visits': r.visits,
                'avg_duration': round(r.avg_duration or 0)
            }
            for r in results
        ]
    }), 200


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def _parse_device(ua: str) -> str:
    """Determine device type from User-Agent string."""
    ua = ua.lower()
    if any(k in ua for k in ('mobile', 'android', 'iphone', 'ipod', 'blackberry')):
        return 'mobile'
    if any(k in ua for k in ('tablet', 'ipad')):
        return 'tablet'
    return 'desktop'


def _get_daily_visits(days: int) -> list:
    """Return visit counts per day for the last N days."""
    result = []
    for i in range(days - 1, -1, -1):
        day = datetime.utcnow().date() - timedelta(days=i)
        count = AnalyticsEvent.query.filter(
            func.date(AnalyticsEvent.created_at) == day
        ).count()
        result.append({'date': day.isoformat(), 'visits': count})
    return result

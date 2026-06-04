from flask import Blueprint, request
from sqlalchemy import and_, func, or_

from app.extensions import db
from app.models.house import House
from app.schemas.house import serialize_house
from app.utils.api_response import success_response

search_bp = Blueprint("search", __name__)


def _available_query():
    return House.query.filter(House.status == "available")


def _apply_common_filters(query):
    city = request.args.get("city")
    district = request.args.get("district")
    layout = request.args.get("layout")
    keyword = request.args.get("keyword")

    if city:
        query = query.filter(House.city == city)
    if district:
        query = query.filter(House.district == district)
    if layout:
        query = query.filter(House.layout == layout)
    if keyword:
        like_value = f"%{keyword}%"
        query = query.filter(
            or_(
                House.title.like(like_value),
                House.city.like(like_value),
                House.district.like(like_value),
                House.community.like(like_value),
                House.address_detail.like(like_value),
                House.layout.like(like_value),
            )
        )

    return query


def _parse_limit(default=6, maximum=20):
    try:
        value = int(request.args.get("limit", default))
    except (TypeError, ValueError):
        value = default
    return min(max(value, 1), maximum)


@search_bp.get("/regions")
def list_regions():
    query = _apply_common_filters(
        db.session.query(
            House.city,
            House.district,
            House.community,
            func.count(House.id).label("house_count"),
            func.min(House.rent).label("min_rent"),
            func.max(House.rent).label("max_rent"),
        ).filter(House.status == "available")
    )

    rows = (
        query.group_by(House.city, House.district, House.community)
        .order_by(func.count(House.id).desc(), House.city.asc(), House.district.asc())
        .all()
    )

    return success_response(
        [
            {
                "city": row.city,
                "district": row.district,
                "community": row.community,
                "house_count": row.house_count,
                "min_rent": float(row.min_rent) if row.min_rent is not None else None,
                "max_rent": float(row.max_rent) if row.max_rent is not None else None,
            }
            for row in rows
        ]
    )


@search_bp.get("/layouts")
def list_layouts():
    query = _apply_common_filters(
        db.session.query(
            House.layout,
            func.count(House.id).label("house_count"),
            func.min(House.rent).label("min_rent"),
            func.max(House.rent).label("max_rent"),
        ).filter(House.status == "available", House.layout.isnot(None), House.layout != "")
    )

    rows = (
        query.group_by(House.layout)
        .order_by(func.count(House.id).desc(), House.layout.asc())
        .all()
    )

    return success_response(
        [
            {
                "layout": row.layout,
                "house_count": row.house_count,
                "min_rent": float(row.min_rent) if row.min_rent is not None else None,
                "max_rent": float(row.max_rent) if row.max_rent is not None else None,
            }
            for row in rows
        ]
    )


@search_bp.get("/recommendations")
def recommendations():
    limit = _parse_limit()
    city = request.args.get("city")
    house_id = request.args.get("house_id", type=int)
    base_house = db.session.get(House, house_id) if house_id else None

    query = _available_query()
    if base_house:
        query = query.filter(House.id != base_house.id)
        similarity_filters = []
        if base_house.city:
            similarity_filters.append(House.city == base_house.city)
        if base_house.district:
            similarity_filters.append(House.district == base_house.district)
        if base_house.layout:
            similarity_filters.append(House.layout == base_house.layout)
        if base_house.rent is not None:
            similarity_filters.append(
                and_(
                    House.rent >= float(base_house.rent) * 0.8,
                    House.rent <= float(base_house.rent) * 1.2,
                )
            )
        if similarity_filters:
            query = query.filter(or_(*similarity_filters))
    elif city:
        query = query.filter(House.city == city)

    items = query.order_by(House.published_at.desc(), House.id.desc()).limit(limit).all()
    if base_house and len(items) < limit:
        existing_ids = {item.id for item in items}
        fallback = (
            _available_query()
            .filter(House.id != base_house.id, House.id.notin_(existing_ids or {-1}))
            .order_by(House.published_at.desc(), House.id.desc())
            .limit(limit - len(items))
            .all()
        )
        items.extend(fallback)

    return success_response([serialize_house(house, include_media=True) for house in items[:limit]])

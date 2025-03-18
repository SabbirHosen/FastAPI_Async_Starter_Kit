from fastapi import Request
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse


def get_pagination_urls(request: Request, total_count: int, page: int = 1, per_page: int = 10):
    url_parts = urlparse(request.url.__str__())
    query_params = parse_qs(url_parts.query)

    query_params["page"] = [str(page + 1)] if (page * per_page) < total_count else []
    next_url = urlunparse(url_parts._replace(query=urlencode(query_params, doseq=True))) if query_params["page"] else None

    query_params["page"] = [str(page - 1)] if page > 1 else []
    prev_url = urlunparse(url_parts._replace(query=urlencode(query_params, doseq=True))) if query_params["page"] else None

    return next_url, prev_url
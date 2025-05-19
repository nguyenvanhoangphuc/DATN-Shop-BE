from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
import math

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'
    page_query_param = 'page'
    max_page_size = 100

    def get_paginated_response(self, data):
        current_page = self.page.number
        total_pages = self.page.paginator.num_pages

        return Response({
            'data': data,
            'links': {
                'first': self.build_link(1),
                'last': self.build_link(total_pages),
                'prev': self.get_previous_link(),
                'next': self.get_next_link()
            },
            'meta': {
                'current_page': current_page,
                'from': (current_page - 1) * self.page.paginator.per_page + 1,
                'last_page': total_pages,
                'links': self.build_meta_links(current_page, total_pages),
                'path': self.request.build_absolute_uri().split('?')[0],
                'per_page': self.page.paginator.per_page,
                'to': (current_page - 1) * self.page.paginator.per_page + len(data),
                'total': self.page.paginator.count
            }
        })

    def build_link(self, page):
        if page > 0 and page <= self.page.paginator.num_pages:
            return self.request.build_absolute_uri().split('?')[0] + f'?page={page}&limit={self.page_size}'
        return None

    def build_meta_links(self, current_page, total_pages):
        meta_links = []

        meta_links.append({
            'url': self.build_link(current_page - 1) if current_page > 1 else None,
            'label': "&laquo; Previous",
            'active': False if current_page == 1 else True
        })

        for page in range(1, total_pages + 1):
            meta_links.append({
                'url': self.build_link(page),
                'label': str(page),
                'active': page == current_page
            })

        meta_links.append({
            'url': self.build_link(current_page + 1) if current_page < total_pages else None,
            'label': "Next &raquo;",
            'active': False if current_page >= total_pages else True
        })

        return meta_links
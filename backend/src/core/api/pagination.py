from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """PAGE_SIZE by default; clients may ask for up to 100 per page with ?page_size=."""
    page_size_query_param = 'page_size'
    max_page_size = 100

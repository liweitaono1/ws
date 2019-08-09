from rest_framework.pagination import PageNumberPagination


def Article_list(request):
    pass


def ArticleList(request):
    pass


def Article_Add(request):
    pass


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    # page_size_query_param = 'page_size'  # 每页设置展示多少条
    page_query_param = 'page'
    max_page_size = 100

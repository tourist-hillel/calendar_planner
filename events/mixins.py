from django.contrib.auth.mixins import UserPassesTestMixin

class CategoryFilterMixin:
    category_field = 'category'
    category_param = 'category'

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.GET.get(self.category_param)
        if category:
            queryset = queryset.filter(**{self.category_field: category})
        return queryset


class QueryFilterMixin:
    query_field = 'title'
    query_param = 'title'

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get(self.query_param)
        if query:
            queryset = queryset.filter(**{self.query_field: query})
        return queryset
    
class OwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        # return super().test_func()
        obj = self.get_object()
        return obj.user == self.request.user
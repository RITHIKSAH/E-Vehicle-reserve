from django.views.generic import TemplateView

class IndexView(TemplateView):
    template_name = "index.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user_authenticated'] = user.is_authenticated  
        context['is_operator'] = user.groups.filter(name= 'operator').exists()
        context['is_manager'] = user.groups.filter(name= 'manager').exists()
        context['is_customer'] = user.groups.filter(name= 'customer').exists()
        return context

from django.urls import path
from .views import AssignmentListView

app_name = 'assignments'
urlpatterns = [
    # CBV url path
    path("", AssignmentListView.as_view()), 
    # path("<int:assignment_id>/", AssignmentDetailView.as_view()),

]
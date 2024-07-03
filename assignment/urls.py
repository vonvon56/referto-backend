from django.urls import path
from .views import AssignmentListView

app_name = 'assignment'
urlpatterns = [
    # CBV url path
    path("", AssignmentListView.as_view()), 
    # path("<int:assignment_id>/", AssignmentDetailView.as_view()),

]

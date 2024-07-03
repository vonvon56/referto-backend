from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import Assignment
# Create your views here.
class AssignmentListView(APIView):
  def get(self, request):
    assignments = Assignment.objects.all()
    contents = [{"id": assignment.id,
                 "name": assignment.name} for assignment in assignments]
    
    return Response(contents, status=status.HTTP_200_OK)
  
  def post(self, request):
    name = request.data.get('name')
    if not name:
      return Response({"detail": "[name] field missing."}, status=status.HTTP_400_BAD_REQUEST)
    
    assignment = Assignment.objects.create(name=name)
    return Response({
      "id": assignment.id,
      "name": assignment.name
    }, status=status.HTTP_201_CREATED)
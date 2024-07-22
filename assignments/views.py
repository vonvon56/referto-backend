from rest_framework import generics, permissions
from .models import Assignment
from .serializers import AssignmentSerializer, AssignmentModifySerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# get: 그 유저의 assignment 목록 가져오기
# post: 그 유저의 assignment 추가
class AssignmentListView(generics.GenericAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="assignment 목록 로드",
        operation_description="해당 유저의 모든 Assignments를 가져옵니다.",
        responses={200: AssignmentSerializer(many=True)},
        manual_parameters=[openapi.Parameter("Authorization", openapi.IN_HEADER, description="access token", type=openapi.TYPE_STRING)]
    )
    def get(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated:
            assignments = Assignment.objects.filter(user=user)
            serializer = AssignmentSerializer(assignments, many=True)
            return Response(serializer.data)
        else:
            raise PermissionDenied("You must be logged in to view assignments.")

    @swagger_auto_schema(
        operation_id="assignment 생성",
        operation_description="새로운 Assignment를 생성합니다.",
        request_body=AssignmentSerializer,
        responses={201: AssignmentSerializer},
        manual_parameters=[openapi.Parameter("Authorization", openapi.IN_HEADER, description="access token", type=openapi.TYPE_STRING)]
    )
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied("You must be logged in to create an assignment.")
        serializer = AssignmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AssignmentDetailView(generics.GenericAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="assignment 수정",
        operation_description="특정 Assignment를 수정합니다.",
        responses={200: AssignmentSerializer},
        manual_parameters=[
            openapi.Parameter("Authorization", openapi.IN_HEADER, description="access token", type=openapi.TYPE_STRING)
        ]
    )
    def put(self, request, pk):
        user = self.request.user
        if not pk:
            return Response({"message": "Assignment ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            assignment = Assignment.objects.get(assignment_id=pk, user=user)
        except Assignment.DoesNotExist:
            return Response({"message": "Assignment not found or not yours"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AssignmentSerializer(assignment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_id="assignment 삭제",
        operation_description="특정 Assignment를 삭제합니다.",
        responses={204: 'No Content'},
        manual_parameters=[
            openapi.Parameter("Authorization", openapi.IN_HEADER, description="access token", type=openapi.TYPE_STRING)
        ]
    )
    def delete(self, request, pk, *args, **kwargs):
        user = self.request.user
        try:
            assignment = Assignment.objects.get(pk=pk, user=user)
        except Assignment.DoesNotExist:
            return Response({"message": "Assignment not found or not yours"}, status=status.HTTP_404_NOT_FOUND)
        
        assignment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @swagger_auto_schema(
            operation_id="개별 assignment 로드",
            operation_description="특정 Assignment를 가져옵니다.",
            responses={200: AssignmentSerializer},
            manual_parameters=[
            openapi.Parameter("Authorization", openapi.IN_HEADER, description="access token", type=openapi.TYPE_STRING)
        ]
        )
    def get(self, request, pk, *args, **kwargs):
        user = self.request.user
        try:
            assignment = Assignment.objects.get(pk=pk, user=user)
        except Assignment.DoesNotExist:
            return Response({"message": "Assignment not found or not yours"}, status=status.HTTP_404_NOT_FOUND)
        
        if assignment.user != request.user:
            raise PermissionDenied("You do not have permission to view this assignment.")
        serializer = AssignmentSerializer(assignment)
        return Response(serializer.data)
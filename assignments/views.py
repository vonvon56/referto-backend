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

class AssignmentListView(generics.GenericAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
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
        operation_description="새로운 Assignment를 생성합니다.",
        request_body=AssignmentSerializer,
        responses={201: AssignmentSerializer},
        manual_parameters=[openapi.Parameter("Authorization", openapi.IN_HEADER, description="access token", type=openapi.TYPE_STRING)]
    )
    def post(self, request, *args, **kwargs):
        print("00")
        if not request.user.is_authenticated:
            raise PermissionDenied("You must be logged in to create an assignment.")
        serializer = AssignmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # @swagger_auto_schema(
    #     operation_description="특정 Assignment를 삭제합니다.",
    #     responses={204: 'No Content'},
    #     request_body=openapi.Schema(
    #         type=openapi.TYPE_OBJECT,
    #         properties={
    #             'assignment_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Assignment ID')
    #         },
    #         required=['assignment_id']
    #     ),
    #     manual_parameters=[
    #         openapi.Parameter("Authorization", openapi.IN_HEADER, description="access token", type=openapi.TYPE_STRING)
    #     ]
    # )
    # def delete(self, request, *args, **kwargs):
    #     user = self.request.user
    #     assignment_id = request.data.get('assignment_id')
    #     if not assignment_id:
    #         return Response({"message": "Assignment ID is required"}, status=status.HTTP_400_BAD_REQUEST)
    #     try:
    #         assignment = Assignment.objects.get(assignment_id=assignment_id, user=user)
    #     except Assignment.DoesNotExist:
    #         return Response({"message": "Assignment not found or not yours"}, status=status.HTTP_404_NOT_FOUND)
        
    #     assignment.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)
    
    @swagger_auto_schema(
        operation_description="특정 Assignment를 수정합니다.",
        responses={200: AssignmentSerializer},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'assignment_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Assignment ID'),
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Assignment name'),
            },
            required=['assignment_id']
        ),
        manual_parameters=[
            openapi.Parameter("Authorization", openapi.IN_HEADER, description="access token", type=openapi.TYPE_STRING)
        ]
    )
    def put(self, request, assignment_id):
        user = self.request.user
        if not assignment_id:
            return Response({"message": "Assignment ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            assignment = Assignment.objects.get(assignment_id=assignment_id, user=user)
        except Assignment.DoesNotExist:
            return Response({"message": "Assignment not found or not yours"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AssignmentSerializer(assignment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AssignmentDetailView(generics.GenericAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
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
    

# class AssignmentDetailView(generics.GenericAPIView):
#     queryset = Assignment.objects.all()
#     serializer_class = AssignmentSerializer

#     @swagger_auto_schema(
#         operation_description="특정 Assignment를 가져옵니다.",
#         responses={200: AssignmentSerializer}
#     )
#     def get(self, request, *args, **kwargs):
#         assignment = self.get_object()
#         if assignment.user != request.user:
#             raise PermissionDenied("You do not have permission to view this assignment.")
#         serializer = AssignmentSerializer(assignment)
#         return Response(serializer.data)

#     @swagger_auto_schema(
#         operation_description="특정 Assignment를 업데이트합니다.",
#         request_body=AssignmentSerializer,
#         responses={200: AssignmentSerializer}
#     )
#     def put(self, request, *args, **kwargs):
#         assignment = self.get_object()
#         if assignment.user != request.user:
#             raise PermissionDenied("You do not have permission to update this assignment.")
#         serializer = AssignmentSerializer(assignment, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     @swagger_auto_schema(
#         operation_description="특정 Assignment를 삭제합니다.",
#         responses={204: openapi.Response(description="Assignment deleted successfully.")}
#     )
#     def delete(self, request, *args, **kwargs):
#         assignment = self.get_object()
#         if assignment.user != request.user:
#             raise PermissionDenied("You do not have permission to delete this assignment.")
#         assignment.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Memo, Paper
from .serializers import MemoSerializer

class MemoDetailView(generics.GenericAPIView):
    serializer_class = MemoSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="해당 메모를 가져옵니다.",
        responses={200: MemoSerializer()},
        manual_parameters=[
            openapi.Parameter(
                "Authorization", 
                openapi.IN_HEADER, 
                description="access token", 
                type=openapi.TYPE_STRING
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        if getattr(self, 'swagger_fake_view', False):
            return Response()
        
        paper_id = kwargs.get('pk')

        try:
            paper = Paper.objects.get(paper_id=paper_id)
        except Paper.DoesNotExist:
            return Response({"detail": "Paper not found."}, status=404)
        
        memo = Memo.objects.filter(paper=paper).first()

        if memo is None:
            return Response({"detail": "Memo not found."}, status=404)
        
        if paper.assignment.user != request.user:
            raise PermissionDenied("You do not have permission to view this memo.")

        serializer = self.serializer_class(memo)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="해당 메모를 수정하거나 없으면 생성합니다.",
        responses={200: MemoSerializer()},
        manual_parameters=[
            openapi.Parameter(
                "Authorization", 
                openapi.IN_HEADER, 
                description="access token", 
                type=openapi.TYPE_STRING
            )
        ],
        request_body=MemoSerializer
    )
    def put(self, request, *args, **kwargs):
        if getattr(self, 'swagger_fake_view', False):
            return Response()
        
        paper_id = kwargs.get('pk')

        try:
            paper = Paper.objects.get(paper_id=paper_id)
        except Paper.DoesNotExist:
            return Response({"detail": "Paper not found."}, status=404)
        
        memo = Memo.objects.filter(paper=paper).first()
        data = request.data.copy()

        if memo:
            if paper.assignment.user != request.user:
                raise PermissionDenied("You do not have permission to edit this memo.")
            serializer = self.serializer_class(memo, data=data, partial=True)
        else:
            serializer = MemoSerializer(data=data)

        if serializer.is_valid():
            serializer.save(paper=paper)
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
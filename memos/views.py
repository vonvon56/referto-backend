from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404
from rest_framework import status

from .models import Memo, Paper
from .serializers import MemoSerializer

class MemoDetailView(generics.GenericAPIView):
    serializer_class = MemoSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id='Memo 로드',
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
        operation_id="Memo 추가",
        operation_description="새로운 메모를 추가합니다.",
        responses={
            201: "Created", 404: "Not Found", 400: "Bad Request"
        }
    )
    def post(self, request, paper_id):
        paper = get_object_or_404(Paper, paper_id=paper_id)

        if not paper.pdf:
            return Response({"error": "PDF file not found."}, status=status.HTTP_404_NOT_FOUND)
        content = request.data.get("content")

        if not content:
            return Response({"detail":"[content] field missing."}, status=status.HTTP_400_BAD_REQUEST)
        
        memo = Memo.objects.create(content=content, paper=paper)
        serializer = MemoSerializer(memo)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_id="Memo 수정",
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
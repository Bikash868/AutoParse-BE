from django.shortcuts import render
from rest_framework import viewsets
from .models import Candidate
from .serializers import CandidateSerializer
from .services import ResumeParser, AIDocumentRequest

class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer

    def create(self, request, *args, **kwargs):
        resume_parser = ResumeParser(request.data['resume'])
        resume_text = resume_parser.parse()
# Create your views here.

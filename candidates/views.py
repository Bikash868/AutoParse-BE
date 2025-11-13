import os

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from django.core.files.storage import default_storage
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import Candidate
from .serializers import CandidateSerializer
from .services import ResumeParser

@method_decorator(csrf_exempt, name='dispatch')
class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def upload(self, request, *args, **kwargs):
        resume_file = request.FILES.get('resume')

        if not resume_file:
            return Response({'error': 'Resume file is required'}, status=status.HTTP_400_BAD_REQUEST)

        # saving the file
        file_path = default_storage.save(f'temp/{resume_file.name}', resume_file)
        full_file_path = os.path.join(default_storage.location, file_path)

        resume_parser = ResumeParser()
        resume_text = resume_parser.parse_resume(full_file_path)

        if not resume_text:
            return Response({'error': 'Failed to parse resume'}, status=status.HTTP_400_BAD_REQUEST)

        # creating a new candidate
        candidate = Candidate.objects.create(
            name=resume_text.get('name'),
            email=resume_text.get('email'),
            phone=resume_text.get('phone'),
            employer=resume_text.get('employer'),
            resume=full_file_path,
        )

        candidate.resume = resume_file
        candidate.save()

        # removing the temporary file
        try:
            os.remove(full_file_path)
        except OSError:
            pass

        serializer = self.get_serializer(candidate)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

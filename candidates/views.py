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
from .services import ResumeParser, AIDocumentRequestGenerator

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
            designation=resume_text.get('designation'),
            skills=resume_text.get('skills'),
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

    @action(detail=True, methods=['post'], url_path='request-documents')
    def request_documents(self, request, pk=None):
        """Generating and logging a personalized request for PAN/Aadhaar documents."""
        try:
            candidate = self.get_object()
            
            ai_generator = AIDocumentRequestGenerator()
            message = ai_generator.generate_request(candidate)
            
            candidate.document_request_message = message
            candidate.save()
            
            return Response({
                'message': message,
                'candidate_id': candidate.id,
                'candidate_name': candidate.name
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Failed to generate document request: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

import logging
from pathlib import Path

from django.core.files.base import ContentFile
from django.db import IntegrityError, transaction

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import ValidationError

from .models import Resume
from .services import validate_file, extract_document

from ai_engine.service import process_resume

from rest_framework.generics import ListAPIView, RetrieveAPIView
from .serializers import ResumeListSerializer, ResumeDetailSerializer

from django.shortcuts import get_object_or_404

from .models import Resume, CandidateProfile, ProcessingLog
from rest_framework.permissions import IsAdminUser

from ai_engine.pipeline import run_full_pipeline

logger = logging.getLogger(__name__)



class ResumeUploadView(APIView):

    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        uploaded_file = request.FILES.get("file")

        if not uploaded_file:
            return Response(
                {"error": "No file provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 1. Validate file and calculate hash
            content, file_hash, extension = validate_file(uploaded_file)

            # 2. Skip duplicates
            if Resume.objects.filter(file_hash=file_hash).exists():
                return Response(
                    {"error": "Resume already uploaded."},
                    status=status.HTTP_409_CONFLICT
                )

            # 3. Extract document text locally
            result = extract_document(content, extension)

            # 4. Identify candidate
            candidate_id = (
                request.data.get("candidate_identifier")
                or Path(uploaded_file.name).stem
            )

            # 5. Save original file and metadata
            with transaction.atomic():
                resume = Resume(
                    candidate_identifier=candidate_id,
                    original_filename=uploaded_file.name,
                    file_hash=file_hash,
                    extracted_text=result["text"],
                    extracted_pages=result["pages"],
                    page_count=result["page_count"],
                    extraction_status=result["status"],
                    extraction_error=result["error"]
                )

                resume.file.save(
                    uploaded_file.name,
                    ContentFile(content),
                    save=False
                )
                resume.save()

            return Response(
                {
                    "success": True,
                    "resume_id": resume.id,
                    "candidate_identifier": resume.candidate_identifier,
                    "filename": resume.original_filename,
                    "extraction_status": resume.extraction_status,
                    "page_count": resume.page_count,
                    "extracted_characters": len(result["text"]),
                    "ai_extraction_status": "pending",
                    "processing_status": "uploaded"
                },
                status=status.HTTP_201_CREATED
            )

        except ValidationError as error:
            return Response(
                {"error": error.detail},
                status=status.HTTP_400_BAD_REQUEST
            )

        except IntegrityError:
            return Response(
                {"error": "Resume already uploaded."},
                status=status.HTTP_409_CONFLICT
            )


class ResumeListView(ListAPIView):
    queryset = Resume.objects.all().order_by("-uploaded_at")
    serializer_class = ResumeListSerializer


class ResumeDetailView(RetrieveAPIView):
    queryset = Resume.objects.all()
    serializer_class = ResumeDetailSerializer
    permission_classes = [IsAdminUser]

    def delete(self, request, *args, **kwargs):
        resume = self.get_object()

        # Preserve original file reference before deleting database records
        file_storage = resume.file.storage
        file_name = resume.file.name

        # Cascade deletes profile, processing logs and ranking results
        with transaction.atomic():
            resume.delete()

        # Remove original uploaded document
        if file_name:
            try:
                file_storage.delete(file_name)
            except Exception:
                logger.exception("Failed to delete resume file: %s", file_name)

        return Response(
            {"success": True, "message": "Candidate deleted successfully."},
            status=status.HTTP_200_OK
        )

class ResumeProcessView(APIView):

    def post(self, request, pk):
        resume = get_object_or_404(Resume, pk=pk)

        try:
            result = run_full_pipeline(resume)

            return Response(result, status=status.HTTP_200_OK)

        except Exception:
            logger.exception("Resume pipeline failed for resume_id=%s", resume.id)
            return Response(
                {
                    "success": False,
                    "resume_id": resume.id,
                    "processing_status": "failed",
                    "message": "Pipeline processing failed. Check processing status."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ResumeStatusView(APIView):

    def get(self, request, pk):
        resume = get_object_or_404(Resume, pk=pk)

        latest_log = resume.processing_logs.order_by(
            "-created_at", "-id"
        ).first()

        if latest_log is None:
            return Response({
                "resume_id": resume.id,
                "processing_status": "not_started",
                "message": "AI processing has not started."
            })

        return Response({
            "resume_id": resume.id,
            "processing_status": latest_log.status,
            "stage": latest_log.stage,
            "message": latest_log.message,
            "updated_at": latest_log.created_at
        })

from unittest.mock import patch

from django.test import TestCase

from job_profiles.models import JobProfile
from job_profiles.services import process_job_description


class JobProfileServiceTests(TestCase):

    @patch("job_profiles.services.extract_jd_with_llm")
    def test_create_job_profile(self, mock_extract):

        mock_extract.return_value = self.make_profile()

        profile, created = process_job_description(
            job_id="JD1",
            jd_text="Python Developer required.",
        )

        self.assertTrue(created)
        self.assertEqual(profile.job_id, "JD1")
        self.assertEqual(JobProfile.objects.count(), 1)

    @patch("job_profiles.services.extract_jd_with_llm")
    def test_update_existing_job_profile(self, mock_extract):

        mock_extract.return_value = self.make_profile()

        first, created = process_job_description(
            "JD1",
            "Original description",
        )

        second, created = process_job_description(
            "JD1",
            "Updated description",
        )

        self.assertFalse(created)
        self.assertFalse(created)
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(
            JobProfile.objects.count(),
            1,
        )
        self.assertEqual(
            second.original_description,
            "Updated description",
        )

    def test_empty_job_id_rejected(self):

        with self.assertRaises(ValueError):
            process_job_description("", "Some JD")

    def test_empty_jd_rejected(self):

        with self.assertRaises(ValueError):
            process_job_description("JD1", "")

    @staticmethod
    def make_profile():
        from job_profiles.schemas import JobProfileSchema

        return JobProfileSchema.model_validate({
            "job_id": "JD1",
            "title": "Python Developer",
            "role_summary": "Backend development role.",
            "mandatory_criteria": {},
            "preferred_criteria": {},
            "responsibilities": [],
            "synonyms": {},
            "scoring_criteria": {},
        })

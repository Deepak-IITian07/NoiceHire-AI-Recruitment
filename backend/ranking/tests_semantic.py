
from unittest import TestCase
from unittest.mock import patch
from ranking.semantic_matching import build_candidate_evidence

from ranking.semantic_matching import (
    build_candidate_corpus,
    tfidf_similarity,
    calculate_semantic_similarity,
)
from ranking.scoring import validate_weights
from ranking.score_calculator import calculate_candidate_score

class SemanticMatchingTests(TestCase):

    def setUp(self):
        self.candidate = {
            "personal_info": {},
            "skills": [
                {"name": "Figma", "category": "Design"}
            ],
            "experience": [
                {
                    "position": "UI/UX Designer",
                    "description": (
                        "Designed user interfaces and conducted "
                        "usability testing."
                    ),
                }
            ],
            "projects": [
                {
                    "name": "Shopping App",
                    "description": (
                        "Created wireframes and interactive prototypes."
                    ),
                    "technologies": ["Figma"],
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Design",
                    "field_of_study": "Design",
                }
            ],
        }

        self.profile = {
            "job_id": "JD2",
            "title": "UI/UX Designer Intern",
            "scoring_criteria": {
                "skills": 35,
                "tools": 20,
                "experience": 15,
                "projects": 25,
                "education": 5,
            },
            "mandatory_criteria": {
                "skills": [
                    {
                        "name": "UI/UX design principles",
                        "description": "Human-centred design",
                        "importance": "high",
                    }
                ],
                "tools": [
                    {
                        "name": "Figma",
                        "description": "Interface design",
                        "importance": "high",
                    }
                ],
                "experience": [
                    {
                        "name": "UX/UI design experience",
                        "description": "Designing user interfaces",
                        "importance": "high",
                    }
                ],
                "projects": [
                    {
                        "name": "Portfolio",
                        "description": "Design case studies",
                        "importance": "medium",
                    }
                ],
                "education": [],
            },
            "preferred_criteria": {},
        }

    def test_candidate_corpus(self):
        corpus = build_candidate_corpus(self.candidate)
        self.assertIn("Figma", corpus["skills"])
        self.assertIn("wireframes", corpus["projects"])

    def test_tfidf_similarity(self):
        score = tfidf_similarity(
            "user interface design",
            "designed user interfaces",
        )
        self.assertIsNotNone(score)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 1)

    def test_missing_text_is_unknown(self):
        result = calculate_semantic_similarity(
            "Python programming",
            "",
            method="tfidf",
        )
        self.assertIsNone(result["score"])
        self.assertEqual(result["status"], "unknown")

    def test_invalid_weights(self):
        with self.assertRaises(ValueError):
            validate_weights({"skills": 100})

    @patch(
        "ranking.semantic_matching.embedding_similarity",
        return_value=0.8,
    )
    def test_complete_score_calculation(self, mock_embedding):
        result = calculate_candidate_score(
            self.candidate,
            self.profile,
            method="combined",
        )

        self.assertIsNotNone(result["score"])
        self.assertGreaterEqual(result["score"], 0)
        self.assertLessEqual(result["score"], 100)
        self.assertIn("information_availability_coverage", result)
        self.assertEqual(result["job_id"], "JD2")

    def test_missing_category_is_not_zero(self):
        candidate = {
            "skills": [],
            "experience": [],
            "projects": [],
            "education": [],
        }

        result = calculate_candidate_score(
            candidate,
            self.profile,
            method="tfidf",
        )

        self.assertIsNone(
            result["category_scores"]["skills"]["score"]
        )
        self.assertIn("skills", result["missing_information"])
        
    def test_candidate_evidence(self):
        evidence = build_candidate_evidence(self.candidate)

        self.assertIn("skills", evidence)
        self.assertIn("Figma", str(evidence["skills"]))

        self.assertIn("projects", evidence)
        self.assertIn("Shopping App", str(evidence["projects"]))
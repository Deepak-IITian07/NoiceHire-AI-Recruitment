
from unittest import TestCase

from ranking.classification import classify_candidate
from ranking.ranker import rank_candidates, rank_for_both_jobs


class ClassificationTests(TestCase):

    def setUp(self):
        self.jd1 = {
            "score": 85,
            "information_availability_coverage": 90,
        }
        self.jd2 = {
            "score": 60,
            "information_availability_coverage": 80,
        }

        self.policy = {
            "minimum_score": 50,
            "minimum_information_availability_coverage": 50,
            "minimum_score_margin": 10,
        }

    def test_uncalibrated_policy_returns_uncertain(self):
        result = classify_candidate(self.jd1, self.jd2)
        self.assertEqual(
            result["classification"],
            "NEITHER_UNCERTAIN",
        )

    def test_jd1_stronger(self):
        result = classify_candidate(
            self.jd1, self.jd2, self.policy
        )
        self.assertEqual(
            result["classification"],
            "JD1_STRONGER",
        )

    def test_both(self):
        result = classify_candidate(
            {
                "score": 80,
                "information_availability_coverage": 90,
            },
            {
                "score": 78,
                "information_availability_coverage": 90,
            },
            self.policy,
        )
        self.assertEqual(result["classification"], "BOTH")

    def test_insufficient_information(self):
        result = classify_candidate(
            {
                "score": None,
                "information_availability_coverage": 0,
            },
            self.jd2,
            self.policy,
        )
        self.assertEqual(
            result["classification"],
            "NEITHER_UNCERTAIN",
        )


class RankingTests(TestCase):

    def setUp(self):
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
                        "name": "Figma",
                        "description": "Interface design",
                        "importance": "high",
                    }
                ]
            },
            "preferred_criteria": {},
        }

        self.candidates = [
            {
                "candidate_identifier": "CAND-002",
                "candidate_data": {
                    "skills": [{"name": "Figma"}]
                },
            },
            {
                "candidate_identifier": "CAND-001",
                "candidate_data": {
                    "skills": [{"name": "Figma"}]
                },
            },
        ]

    def test_ranking_ties_are_stable(self):
        results = rank_candidates(
            self.candidates,
            self.profile,
            method="tfidf",
        )

        self.assertEqual(
            [r["candidate_identifier"] for r in results],
            ["CAND-001", "CAND-002"],
        )

    def test_rank_for_both_jobs(self):
        result = rank_for_both_jobs(
            self.candidates,
            self.profile,
            self.profile,
            method="tfidf",
        )

        self.assertIn("JD1", result["rankings"])
        self.assertIn("JD2", result["rankings"])
        self.assertEqual(len(result["classifications"]), 2)

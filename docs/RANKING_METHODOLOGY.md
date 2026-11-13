# NoiceHire Ranking Methodology

This document describes the ranking behavior implemented in the current NoiceHire codebase. It does not define a new ranking policy.

## 1. End-to-end flow

1. A resume is uploaded and its document text is extracted locally.
2. `ai_engine.service.process_resume` sends the extracted text to the configured resume provider:
   - Gemini by default (`RESUME_LLM_PROVIDER=gemini`).
   - Ollama when `RESUME_LLM_PROVIDER=ollama`.
3. The provider returns structured candidate data. The result is normalized and validated with the Pydantic candidate schema, then stored in `CandidateProfile` using `update_or_create`.
4. `ai_engine.pipeline.run_full_pipeline` loads the stored JD1 and JD2 profiles and all candidate profiles with data.
5. `ranking.ranker.rank_for_both_jobs` calls `rank_candidates` once for JD1 and once for JD2. These are separate rankings; there is no single combined JD1/JD2 ranking.
6. Each result is persisted as a `MatchResult` for the resume and job profile. The database enforces one result per resume/job pair.

The ranking engine itself accepts plain dictionaries and does not access Django directly.

## 2. Job descriptions and scoring weights

Job descriptions are extracted into structured job profiles by `job_profiles.jd_extractor` using the local Ollama model `llama3.2:latest`. The extracted profile contains mandatory criteria, preferred criteria, responsibilities, and other fields. `job_profiles.services.process_job_description` also adds the default scoring configuration and stores the profile.

The default scoring templates are defined in `job_profiles/scoring_criteria.py`:

| Category | JD1: LCA Consultant | JD2: UI/UX Designer Intern |
| --- | ---: | ---: |
| Skills | 35% | 35% |
| Tools | 20% | 20% |
| Experience | 25% | 15% |
| Projects | 15% | 25% |
| Education | 5% | 5% |
| **Total** | **100%** | **100%** |

The ranking code uses the `scoring_criteria` stored on each `JobProfile`. The weights are validated to contain exactly the five categories above and to total 100.

The default criterion-importance weights are also implemented in `ranking/scoring.py`:

- `high`: 3.0
- `medium`: 2.0
- `low`: 1.0
- Any other importance value: 1.0

Mandatory and preferred criteria are combined per category. Duplicate criteria are removed using a normalized category/name key, with the mandatory criterion taking precedence because mandatory criteria are processed first.

## 3. Resume data used for comparison

`ranking.semantic_matching.build_candidate_corpus` builds category-specific text from the structured candidate data:

- `skills`: skill names, categories, and evidence
- `tools`: skill text plus project text
- `experience`: positions, companies, employment types, descriptions, evidence, and total experience
- `projects`: project names, descriptions, technologies, and evidence
- `education`: degrees, fields of study, institutions, and grades

Candidate personal information and certifications are retained as supplementary text but are not part of the five weighted scoring categories.

The candidate's extraction confidence and verification-status fields are not used as score multipliers or filters by the ranking implementation.

## 4. Criterion matching and score calculation

For every applicable JD criterion, the matcher creates a query from the criterion `name` and `description`.

When individual resume evidence exists for the category, each evidence entry is compared separately and the highest similarity is selected. If no individual entries exist, the category corpus is used as a fallback. A criterion with no usable resume text receives an unknown result with no numeric score.

The default pipeline method is `combined`. Its implemented semantic similarity is:

```text
combined_similarity = 0.30 * TF-IDF_similarity
                    + 0.70 * embedding_similarity
```

The components are:

- TF-IDF cosine similarity using `TfidfVectorizer` with lowercase text, unigram/bigram features, and sublinear term frequency.
- Sentence embedding cosine similarity using `sentence-transformers/all-MiniLM-L6-v2`. The cosine value is converted to the range 0-1.

The matcher also supports `tfidf` and `embedding` methods, but the full pipeline calls the default `combined` method.

### Category scores

Within a category, only applicable criteria with numeric scores are evaluated. The category score is an importance-weighted average of those criterion scores, converted from the 0-1 similarity range to 0-100:

```text
category_score = 100 * sum(criterion_score * importance_weight)
                       / sum(importance_weight)
```

The category is marked unavailable when it has no evaluated criteria.

### Final score

Only available categories participate in the final score denominator. Missing categories are not treated as zero:

```text
final_score = sum(category_score * category_weight)
              / sum(category_weight for available categories)
```

The final score is rounded to two decimal places. If no category has an evaluated score, the final score is `None`.

This normalization means a candidate can receive a score from the categories for which resume information is available; the separate information-availability value is used to expose how much of the original criteria could be evaluated.

## 5. Information availability and missing data

For each category, criterion coverage is the importance-weighted proportion of applicable criteria that received a numeric score. Overall information availability is the category-weighted coverage across the five original scoring categories and is returned as a percentage rounded to two decimals.

The result includes `missing_information`, containing categories that have no available category score. A missing category is excluded from the final score denominator rather than assigned a zero.

If resume text is absent, the resume cannot be processed. If a category or criterion has no usable text, its similarity is unknown (`None`). If all categories are unavailable, the final score is `None` and the explanation reports insufficient resume information.

## 6. Ranking order and JD-specific ranking

`ranking.ranker.rank_candidates` produces one ordered list for one job profile. It sorts by:

1. Numeric score descending.
2. Candidates with `None` scores after candidates with numeric scores.
3. Candidate identifier alphabetically, case-insensitively, for ties.

`rank_for_both_jobs` runs this independently for JD1 and JD2 and returns separate `rankings["JD1"]` and `rankings["JD2"]` lists.

The database API also orders `MatchResult` rows by score descending with null scores last, then by most recently updated. The ranking serializer exposes the score and ranking details but does not expose a stored numeric rank field. Therefore, a displayed rank is the candidate's position in the relevant ordered JD list; the backend does not persist rank numbers.

The uniqueness constraint on `(resume, job_profile)` and the pipeline's `update_or_create` persistence prevent duplicate match-result rows for the same resume and job profile.

## 7. Evidence and explanations

`ranking.semantic_matching.build_candidate_evidence` preserves individual evidence entries with sources such as:

- `resume_skill`
- `resume_experience`
- `resume_project`
- `project_technology`
- `resume_education`

For each criterion with a numeric match, the strongest matching evidence entry is retained with its text and source. `ranking.explainability.build_explanation` groups these matches into skills, tools, projects, experience, and education evidence. It also includes the similarity value, criterion, importance, missing categories, score, and information availability.

The persisted `MatchResult.explanation` contains:

- The deterministic score explanation and evidence from the ranking engine.
- The cross-job classification result for the candidate.

The explanation is generated from the structured candidate data and matching results. It is not a second generative AI explanation step.

## 8. Classification and human review

Cross-job classification compares the JD1 and JD2 results, but the default classification policy has no calibrated values for minimum score, minimum information coverage, or minimum score margin. With that default policy, classification returns `NEITHER_UNCERTAIN` unless the scores are unavailable, in which case it also reports insufficient information.

The code includes support for an explicitly supplied calibrated policy, including `BOTH`, `JD1_STRONGER`, `JD2_STRONGER`, and `NEITHER_UNCERTAIN`, but the repository does not define production calibration thresholds.

The frontend presents ranking results as requiring human review. Scores and classifications are decision-support outputs, not automatic hiring decisions.

## 9. Limitations and unimplemented behavior

- Resume and job-description extraction is AI/LLM-generated. Pydantic validation checks structure and allowed value shapes; it does not prove that extracted facts are true.
- The semantic blend is marked in code as experimental and not calibrated as a hiring threshold.
- No reviewed hiring outcomes or recruiter feedback are used to calibrate category weights, criterion weights, similarity thresholds, or classification thresholds.
- The synonym map is stored with job profiles, and helper functions exist for canonical skill names, but the current semantic ranking path does not apply those synonyms during matching.
- Certifications, personal information, and extraction confidence are not included in the weighted score categories.
- No hard mandatory-criterion disqualification rule is implemented. Mandatory and preferred criteria affect the score through criterion presence and importance, but a mandatory mismatch does not automatically reject a candidate.
- No backend rank number is stored in the database or returned by the serializer; rank is derived from ordered results.
- The implementation does not claim that a higher score guarantees job performance or hiring suitability. Human review remains required.

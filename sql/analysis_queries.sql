-- ============================================================
-- India Job Market Intelligence — SQL Analysis Queries
-- Dataset: Glassdoor DA/DS Job Postings
-- ============================================================


-- ── 1. TOP 10 HIRING CITIES ───────────────────────────────
SELECT
    SPLIT_PART(location, ',', 1) AS city,
    COUNT(*)                     AS job_count
FROM job_postings
GROUP BY city
ORDER BY job_count DESC
LIMIT 10;


-- ── 2. AVERAGE SALARY BY ROLE ─────────────────────────────
SELECT
    role,
    ROUND(AVG(salary_mid), 1) AS avg_salary_k,
    COUNT(*)                  AS total_jobs
FROM job_postings
WHERE salary_mid IS NOT NULL
GROUP BY role
ORDER BY avg_salary_k DESC;


-- ── 3. TOP 10 IN-DEMAND SKILLS ────────────────────────────
SELECT
    skill,
    COUNT(*) AS demand_count
FROM skills_data
WHERE skill IS NOT NULL AND skill != ''
GROUP BY skill
ORDER BY demand_count DESC
LIMIT 10;


-- ── 4. TOP 20 HIRING COMPANIES ────────────────────────────
SELECT
    company_clean                 AS company,
    COUNT(*)                      AS job_postings,
    ROUND(AVG(salary_mid), 1)     AS avg_salary_k,
    ROUND(AVG(rating), 2)         AS avg_rating
FROM job_postings
GROUP BY company_clean
ORDER BY job_postings DESC
LIMIT 20;


-- ── 5. SALARY BY SECTOR (TOP 10) ──────────────────────────
SELECT
    sector,
    ROUND(AVG(salary_mid), 1) AS avg_salary_k,
    COUNT(*)                  AS job_count
FROM job_postings
WHERE salary_mid IS NOT NULL
  AND sector IS NOT NULL
GROUP BY sector
HAVING COUNT(*) >= 5
ORDER BY avg_salary_k DESC
LIMIT 10;


-- ── 6. SKILLS DEMAND BY ROLE ──────────────────────────────
SELECT
    s.role,
    s.skill,
    COUNT(*) AS demand_count
FROM skills_data s
WHERE s.skill IS NOT NULL AND s.skill != ''
GROUP BY s.role, s.skill
ORDER BY s.role, demand_count DESC;


-- ── 7. COMPANY SIZE vs AVERAGE SALARY ─────────────────────
SELECT
    size,
    ROUND(AVG(salary_mid), 1) AS avg_salary_k,
    COUNT(*)                  AS job_count
FROM job_postings
WHERE salary_mid IS NOT NULL
  AND size NOT IN ('-1', 'Unknown')
GROUP BY size
ORDER BY avg_salary_k DESC;


-- ── 8. JOBS BY OWNERSHIP TYPE ─────────────────────────────
SELECT
    type_of_ownership,
    COUNT(*)                  AS job_count,
    ROUND(AVG(salary_mid), 1) AS avg_salary_k
FROM job_postings
WHERE type_of_ownership NOT IN ('-1', 'Unknown')
GROUP BY type_of_ownership
ORDER BY job_count DESC;


-- ── 9. EASY APPLY JOB PERCENTAGE BY ROLE ──────────────────
SELECT
    role,
    COUNT(*)                                             AS total_jobs,
    SUM(CASE WHEN easy_apply = 'True' THEN 1 ELSE 0 END) AS easy_apply_jobs,
    ROUND(
        100.0 * SUM(CASE WHEN easy_apply = 'True' THEN 1 ELSE 0 END) / COUNT(*),
        1
    )                                                    AS easy_apply_pct
FROM job_postings
GROUP BY role
ORDER BY easy_apply_pct DESC;


-- ── 10. TOP CITIES FOR DATA ANALYST ROLES ─────────────────
SELECT
    SPLIT_PART(location, ',', 1) AS city,
    COUNT(*)                     AS da_jobs,
    ROUND(AVG(salary_mid), 1)    AS avg_salary_k
FROM job_postings
WHERE role = 'Data Analyst'
  AND salary_mid IS NOT NULL
GROUP BY city
HAVING COUNT(*) >= 3
ORDER BY da_jobs DESC
LIMIT 10;

-- Highest priority counties in 2023.
SELECT locationname, stateabbr, burden_index, access_gap_index, need_priority_score
FROM county_scores
WHERE year = 2023
ORDER BY need_priority_score DESC
LIMIT 10;

-- Number of counties and average score by state.
SELECT stateabbr, COUNT(*) AS counties, ROUND(AVG(need_priority_score), 3) AS avg_score
FROM county_scores
WHERE year = 2023
GROUP BY stateabbr
ORDER BY avg_score DESC;

-- Counties above the three-state average on both parts of the score.
-- Each index is built from z-scores, so zero represents the average.
SELECT locationname, stateabbr,
       ROUND(burden_index, 3) AS burden_index,
       ROUND(access_gap_index, 3) AS access_gap_index,
       ROUND(need_priority_score, 3) AS need_priority_score
FROM county_scores
WHERE year = 2023
  AND burden_index > 0
  AND access_gap_index > 0
ORDER BY need_priority_score DESC
LIMIT 20;

-- How many counties meet both conditions, by state?
SELECT stateabbr, COUNT(*) AS counties_above_both_averages
FROM county_scores
WHERE year = 2023
  AND burden_index > 0
  AND access_gap_index > 0
GROUP BY stateabbr
ORDER BY stateabbr;

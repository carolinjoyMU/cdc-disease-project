# Tableau dashboard build guide

Use `county_priority_scores.csv` as a **Text File** data source in Tableau Desktop. The CSV has one row per county for measure year 2023. Keep `Year` filtered to 2023 and treat `Locationid` as a dimension so each county is a separate mark.

## Sheet 1: Burden vs access gap

1. Put `Burden Index` on Columns and `Access Gap Index` on Rows.
2. Put `Locationid` on Detail and `Stateabbr` on Color. Set mark type to Circle.
3. Put `Locationname`, `Stateabbr`, and `Need Priority Score` in the tooltip.
4. Add reference lines at zero on both axes. The upper-right quadrant contains counties above the group average on both indices.
5. Check the status bar: **257 marks** with all three states selected.

## Sheet 2: Top 15 counties

1. Put `Locationname` and `Stateabbr` on Rows and `Need Priority Score` on Columns. Keep `Locationid` on Detail so counties with the same name remain distinct.
2. Filter `Locationid` to the top 15 by `Need Priority Score`, then sort descending by score.
3. Put `Burden Index`, `Access Gap Index`, and all six raw measure values in the tooltip.
4. Title the sheet **Highest relative priority counties (2023)**.

## Sheet 3: State summary

1. Put `Stateabbr` on Rows and average `Need Priority Score` on Columns.
2. Show the county count in the tooltip. Use `COUNTD(Locationid)` if Tableau is aggregating records.
3. Label the axis **Average county score**. These are unweighted county averages, not state prevalence estimates.

## Dashboard layout

Create a dashboard named **County health priority | IL, MI, WI | 2023**. Put the scatter plot on the left, the top-15 chart on the right, and the state summary beneath them. Add a state filter that applies to all three worksheets. Add a short caption:

> Relative score from six CDC PLACES crude-prevalence measures. Higher means greater combined burden and service-use gap among these 257 counties. Scores are not clinical risk estimates.

Check the selected state changes all three views and that clearing the filter restores 257 counties. Save the workbook in this directory as `county_health_priority.twbx` using **File > Save As > Tableau Packaged Workbook**. Publish the same workbook to Tableau Public, then add its public URL to the project README.

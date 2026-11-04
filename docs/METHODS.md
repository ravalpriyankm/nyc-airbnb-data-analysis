# Methodology and limits

## Preparation
1. Normalise column labels to lowercase snake_case and reject collisions.
2. Count and remove *exact* duplicate source rows before analysing.
3. Correct known borough spellings `brookln` and `manhatan`; never guess missing boroughs.
4. Convert source USD price strings; exclude zero/negative or non-numeric listed prices from price summaries.
5. Retain missing data; do not fill unknown values with invented medians or categories.
6. Validate `availability_365` within 0–365 and minimum stay at least one night.
7. Count duplicate listing IDs separately for review, because IDs can represent source inconsistency.

## Analysis
- Report listing counts by borough and room type.
- Report median and mean *listed* price using valid rows, with denominators.
- Summarise cancellation-policy category counts without inferring that a room type "has a strict policy" unless the labels and rates substantiate it.
- Count listings whose minimum permitted stay is no longer than 10 nights; not booked stays.
- Summarise available days; do not infer booked nights or occupancy (unavailable dates can have many causes).
- Treat a construction year as a source-reported listing attribute, not verified construction history.

## Not supported
This is **descriptive EDA**, not causal inference, price forecasting, verified transaction data, an Airbnb market census, or evidence of current NYC housing conditions. The Kaggle source may contain deliberately introduced inconsistencies, and missing or transformed values affect conclusions. No independent reproduction of the original notebook's numeric findings was possible without the CSV.

For a robust real-data study: acquire a documented dated extract, validate sampling/representativeness, justify exclusion criteria, report outlier sensitivity, and include uncertainty estimates where meaningful.

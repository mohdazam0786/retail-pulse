# RetailPulse — RFM Customer Segmentation Insights

## Overview
RetailPulse segments identified customers using Recency, Frequency, and Monetary (RFM) metrics. The analysis uses cleaned positive-sales transactions from the Online Retail dataset.

## Key Findings
- **Champions:** 947 customers with recorded spend of 5,730,402.80.
- **Hibernating:** 1,066 customers, the largest segment by count.
- **Loyal Customers:** 712 customers with average invoice frequency of 5.20.
- **Potential Loyalists:** 737 customers who may respond to repeat-purchase campaigns.
- **At Risk:** 221 customers who may need targeted reactivation.

## Recommended Actions
1. Reward Champions through loyalty benefits and personalized offers.
2. Test reactivation campaigns for Hibernating and At Risk customers.
3. Encourage repeat purchases among Potential Loyalists and Recent Customers.
4. Measure campaign results before scaling discounts or incentives.

## Methodology and Limitations
RFM scores are assigned using quintiles for recency, frequency, and monetary value. Segment labels are based on heuristic SQL rules and should be validated against business objectives.

Recorded spend represents revenue from the cleaned positive-sales dataset. It is not profit or customer lifetime value. Currency and campaign effectiveness have not been independently validated.

## Data Summary
- Customers segmented: 4,338
- Segments: 7
- Largest segment: Hibernating
- Highest recorded spend: Champions

# Codebook - hotel_bookings_categorized.csv

Generated automatically by `scripts/categorize_data.py` from `hotel_bookings_clean.csv`. Do not edit by hand.

All columns are categorical. Ordinal attributes carry a numeric prefix so that sorted order
equals real order (needed for CleverMiner `seq` coefficients). Binary derived attributes are
named with a verb/prefix and coded 0 / 1. Month and weekday are plain numbers.

Load the file with all columns as text, otherwise pandas infers mixed int/str types in
columns such as `previous_cancellations_cat` (values 0, 1, 2+):

```python
df = pd.read_csv('data/processed/hotel_bookings_categorized.csv', dtype=str)
```

- Rows: 118558
- Columns: 28
- Not included on purpose: assigned_room_type, booking_changes (post-booking information),
  agent, company (raw ids), arrival_date_week_number, arrival_date_day_of_month.

## Columns

### `hotel`

Main segmentation: City Hotel / Resort Hotel (unchanged).

- distinct values: 2, missing: 0

| value | count | share | cancel rate |
|---|---|---|---|
| City Hotel | 78894 | 66.5% | 41.9% |
| Resort Hotel | 39664 | 33.5% | 28.0% |

### `is_canceled`

TARGET. 1 = canceled (incl. no-show), 0 = checked out (unchanged).

- distinct values: 2, missing: 0

| value | count | share | cancel rate |
|---|---|---|---|
| 0 | 74387 | 62.7% | 0.0% |
| 1 | 44171 | 37.3% | 100.0% |

### `lead_time_cat`

Days between booking and arrival: 0-7, 8-30, 31-90, 91-180, 181-365, 365+ (ordinal, prefixed).

- distinct values: 6, missing: 0

| value | count | share | cancel rate |
|---|---|---|---|
| 1_0-7 | 19243 | 16.2% | 9.7% |
| 2_8-30 | 18847 | 15.9% | 28.0% |
| 3_31-90 | 29436 | 24.8% | 37.8% |
| 4_91-180 | 26383 | 22.3% | 44.8% |
| 5_181-365 | 21505 | 18.1% | 55.5% |
| 6_365+ | 3144 | 2.7% | 67.7% |

### `arrival_year`

Year of arrival. 2015 covers only Jul-Dec, 2017 only Jan-Aug.

- distinct values: 3, missing: 0

| value | count | share | cancel rate |
|---|---|---|---|
| 2015 | 21815 | 18.4% | 37.3% |
| 2016 | 56234 | 47.4% | 36.1% |
| 2017 | 40509 | 34.2% | 38.8% |

### `arrival_month`

Month of arrival as number, 1 = January ... 12 = December.

- distinct values: 12, missing: 0

| value | count | share | cancel rate |
|---|---|---|---|
| 1 | 5871 | 5.0% | 30.7% |
| 2 | 7998 | 6.7% | 33.6% |
| 3 | 9714 | 8.2% | 32.4% |
| 4 | 11045 | 9.3% | 40.9% |
| 5 | 11704 | 9.9% | 39.9% |
| 6 | 10891 | 9.2% | 41.6% |
| 7 | 12585 | 10.6% | 37.6% |
| 8 | 13808 | 11.6% | 37.9% |
| 9 | 10477 | 8.8% | 39.3% |
| 10 | 11064 | 9.3% | 38.4% |
| 11 | 6712 | 5.7% | 31.6% |
| 12 | 6689 | 5.6% | 35.4% |

### `season`

Meteorological season of arrival: winter (Dec-Feb), spring (Mar-May), summer (Jun-Aug), autumn (Sep-Nov).

- distinct values: 4, missing: 0

| value | count | share | cancel rate |
|---|---|---|---|
| 1_winter | 20558 | 17.3% | 33.3% |
| 2_spring | 32463 | 27.4% | 38.0% |
| 3_summer | 37284 | 31.4% | 38.9% |
| 4_autumn | 28253 | 23.8% | 37.1% |

### `arrival_weekday`

Day of week of arrival as number, 1 = Monday ... 7 = Sunday.

- distinct values: 7, missing: 0

| value | count | share | cancel rate |
|---|---|---|---|
| 1 | 18045 | 15.2% | 34.3% |
| 2 | 13835 | 11.7% | 33.2% |
| 3 | 15997 | 13.5% | 36.4% |
| 4 | 19132 | 16.1% | 41.4% |
| 5 | 19509 | 16.5% | 40.8% |
| 6 | 17966 | 15.2% | 39.7% |
| 7 | 14074 | 11.9% | 32.4% |

### `is_weekend_arrival`

1 = arrival on Saturday or Sunday.

- distinct values: 2, missing: 0

| value | count | share | cancel rate |
|---|---|---|---|
| 0 | 86518 | 73.0% | 37.5% |
| 1 | 32040 | 27.0% | 36.5% |

### `total_nights_cat`

Length of stay in nights: 1, 2-3, 4-7, 8+ (ordinal, prefixed).

- distinct values: 4, missing: 0

| value | count | share | cancel rate |
|---|---|---|---|
| 1_1 | 21003 | 17.7% | 25.1% |
| 2_2-3 | 54694 | 46.1% | 43.0% |
| 3_4-7 | 37636 | 31.7% | 35.9% |
| 4_8+ | 5225 | 4.4% | 35.9% |

### `stay_type`

weekend_only / weekday_only / mixed, from weekend vs. week nights.

- distinct values: 3, missing: 0

| value | count | share | cancel rate |
|---|---|---|---|
| mixed | 60385 | 50.9% | 37.8% |
| weekday_only | 51247 | 43.2% | 38.0% |
| weekend_only | 6926 | 5.8% | 27.1% |

### `guests_cat`

Total guests (adults + children + babies): 1, 2, 3+.

- distinct values: 3, missing: 0

| value | count | share | cancel rate |
|---|---|---|---|
| 1 | 22381 | 18.9% | 29.2% |
| 2 | 81652 | 68.9% | 39.9% |
| 3+ | 14525 | 12.3% | 34.9% |

### `has_children`

1 = at least one child or baby in the booking.

- distinct values: 2, missing: 0

| value | count | share | cancel rate |
|---|---|---|---|
| 0 | 109266 | 92.2% | 37.4% |
| 1 | 9292 | 7.8% | 35.1% |

### `meal`

Meal package BB / HB / FB / SC (unchanged).

- distinct values: 4, missing: 0

| value | count | share | cancel rate |
|---|---|---|---|
| BB | 91715 | 77.4% | 37.6% |
| FB | 797 | 0.7% | 60.0% |
| HB | 14383 | 12.1% | 34.6% |
| SC | 11663 | 9.8% | 36.3% |

### `country_group`

Country of origin: PRT / GBR / FRA / ESP / DEU / Other / Unknown.

- distinct values: 7, missing: 0

| value | count | share | cancel rate |
|---|---|---|---|
| DEU | 7285 | 6.1% | 16.7% |
| ESP | 8544 | 7.2% | 25.5% |
| FRA | 10389 | 8.8% | 18.6% |
| GBR | 12094 | 10.2% | 20.3% |
| Other | 31836 | 26.9% | 27.8% |
| PRT | 47937 | 40.4% | 57.3% |
| Unknown | 473 | 0.4% | 12.1% |

### `market_segment`

Market segment (unchanged).

- distinct values: 7, missing: 0

| value | count | share | cancel rate |
|---|---|---|---|
| Aviation | 231 | 0.2% | 22.1% |
| Complementary | 715 | 0.6% | 12.2% |
| Corporate | 5231 | 4.4% | 18.9% |
| Direct | 12447 | 10.5% | 15.5% |
| Groups | 19758 | 16.7% | 61.2% |
| Offline TA/TO | 24048 | 20.3% | 34.5% |
| Online TA | 56128 | 47.3% | 36.9% |

### `distribution_channel`

Distribution channel (unchanged).

- distinct values: 4, missing: 0

| value | count | share | cancel rate |
|---|---|---|---|
| Corporate | 6584 | 5.6% | 22.2% |
| Direct | 14450 | 12.2% | 17.6% |
| GDS | 190 | 0.2% | 19.5% |
| TA/TO | 97334 | 82.1% | 41.2% |

### `customer_type`

Customer type (unchanged).

- distinct values: 4, missing: 0

| value | count | share | cancel rate |
|---|---|---|---|
| Contract | 4056 | 3.4% | 31.1% |
| Group | 569 | 0.5% | 10.2% |
| Transient | 88933 | 75.0% | 41.0% |
| Transient-Party | 25000 | 21.1% | 25.5% |

### `deposit_type`

Deposit type (unchanged).

- distinct values: 3, missing: 0

| value | count | share | cancel rate |
|---|---|---|---|
| No Deposit | 103810 | 87.6% | 28.6% |
| Non Refund | 14586 | 12.3% | 99.4% |
| Refundable | 162 | 0.1% | 22.2% |

### `is_repeated_guest`

1 = repeated guest (unchanged).

- distinct values: 2, missing: 0

| value | count | share | cancel rate |
|---|---|---|---|
| 0 | 115060 | 97.0% | 37.9% |
| 1 | 3498 | 3.0% | 15.7% |

### `previous_cancellations_cat`

Previous cancellations by the customer: 0 / 1 / 2+.

- distinct values: 3, missing: 0

| value | count | share | cancel rate |
|---|---|---|---|
| 0 | 112083 | 94.5% | 34.1% |
| 1 | 6044 | 5.1% | 94.5% |
| 2+ | 431 | 0.4% | 52.9% |

### `previous_bookings_not_canceled_cat`

Previous non-canceled bookings by the customer: 0 / 1+.

- distinct values: 2, missing: 0

| value | count | share | cancel rate |
|---|---|---|---|
| 0 | 114976 | 97.0% | 38.2% |
| 1+ | 3582 | 3.0% | 5.6% |

### `reserved_room_type_cat`

Reserved room type: A / D / E / F / G / Other.

- distinct values: 6, missing: 0

| value | count | share | cancel rate |
|---|---|---|---|
| A | 85395 | 72.0% | 39.4% |
| D | 19096 | 16.1% | 31.9% |
| E | 6482 | 5.5% | 29.4% |
| F | 2879 | 2.4% | 30.6% |
| G | 2074 | 1.7% | 36.8% |
| Other | 2632 | 2.2% | 34.8% |

### `has_agent`

1 = booked through a travel agent (agent id present).

- distinct values: 2, missing: 0

| value | count | share | cancel rate |
|---|---|---|---|
| 0 | 16076 | 13.6% | 24.9% |
| 1 | 102482 | 86.4% | 39.2% |

### `has_company`

1 = company booking (company id present).

- distinct values: 2, missing: 0

| value | count | share | cancel rate |
|---|---|---|---|
| 0 | 111863 | 94.4% | 38.4% |
| 1 | 6695 | 5.6% | 17.6% |

### `was_on_waiting_list`

1 = booking spent at least one day on the waiting list.

- distinct values: 2, missing: 0

| value | count | share | cancel rate |
|---|---|---|---|
| 0 | 114866 | 96.9% | 36.4% |
| 1 | 3692 | 3.1% | 63.9% |

### `adr_cat`

Average daily rate: 0 / 1-75 / 76-125 / 126-200 / 200+ (ordinal, prefixed).

- distinct values: 5, missing: 0

| value | count | share | cancel rate |
|---|---|---|---|
| 1_0 | 1165 | 1.0% | 14.2% |
| 2_1-75 | 35539 | 30.0% | 35.5% |
| 3_76-125 | 51411 | 43.4% | 38.2% |
| 4_126-200 | 25515 | 21.5% | 38.7% |
| 5_200+ | 4928 | 4.2% | 38.4% |

### `needs_parking`

1 = at least one car parking space required.

- distinct values: 2, missing: 0

| value | count | share | cancel rate |
|---|---|---|---|
| 0 | 111166 | 93.8% | 39.7% |
| 1 | 7392 | 6.2% | 0.0% |

### `special_requests_cat`

Number of special requests: 0 / 1 / 2+.

- distinct values: 3, missing: 0

| value | count | share | cancel rate |
|---|---|---|---|
| 0 | 69798 | 58.9% | 48.0% |
| 1 | 33002 | 27.8% | 22.1% |
| 2+ | 15758 | 13.3% | 21.2% |

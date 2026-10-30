# Codebook - hotel_bookings_clean.csv

Generated automatically by `scripts/prepare_data.py`. Do not edit by hand.

## Summary

- Raw rows: 119390
- Clean rows: 118558 (832 removed)
- Columns: 33
- Exact duplicate rows kept on purpose: 32184

### Cancellation rate by hotel

| hotel | bookings | canceled | cancel rate |
|---|---|---|---|
| City Hotel | 78894 | 33061 | 41.9% |
| Resort Hotel | 39664 | 11110 | 28.0% |
| **Total** | 118558 | 44171 | 37.3% |

## Cleaning log

- Loaded raw file with 119390 rows and 32 columns.
- children: 4 rows with text 'NA' recoded to 0; column cast to integer.
- country: 488 rows with text 'NULL' converted to missing (empty in CSV).
- agent: 16340 rows with text 'NULL' converted to missing (empty in CSV).
- company: 112593 rows with text 'NULL' converted to missing (empty in CSV).
- meal: 1169 rows with 'Undefined' merged into 'SC'.
- Derived numeric helper columns added: total_nights, total_guests, arrival_date.
- Dropped 180 rows - no guests: adults + children + babies == 0 (booking without a single guest is invalid).
- Dropped 645 rows - zero nights: stays_in_weekend_nights + stays_in_week_nights == 0 (no stay).
- Dropped 1 rows - negative adr: adr < 0 (invalid price).
- Dropped 1 rows - extreme adr: adr > 1000 (single outlier of 5400).
- Dropped 2 rows - undefined market segment: market_segment == 'Undefined'.
- Dropped 3 rows - undefined distribution channel: distribution_channel == 'Undefined'.
- Dropped columns reservation_status, reservation_status_date (alternative encoding of the target is_canceled).
- Final clean dataset: 118558 rows, 33 columns.

## Columns

### `hotel`

Hotel type: City Hotel or Resort Hotel (main segmentation of the project).

- dtype: `str`, missing: 0
- distinct values: 2

| value | count | share | cancel rate |
|---|---|---|---|
| City Hotel | 78894 | 66.5% | 41.9% |
| Resort Hotel | 39664 | 33.5% | 28.0% |

### `is_canceled`

TARGET. 1 = booking was canceled (incl. no-show), 0 = guest checked out.

- dtype: `int64`, missing: 0
- distinct values: 2

| value | count | share | cancel rate |
|---|---|---|---|
| 0 | 74387 | 62.7% | 0.0% |
| 1 | 44171 | 37.3% | 100.0% |

### `lead_time`

Days between booking creation and arrival date.

- dtype: `int64`, missing: 0
- min 0, 25% 18, median 70, 75% 161, max 709, mean 104.51
- distinct values: 478

### `arrival_date_year`

Year of arrival (2015 covers only Jul-Dec, 2017 only Jan-Aug).

- dtype: `int64`, missing: 0
- min 2015, 25% 2016, median 2016, 75% 2017, max 2017, mean 2016.16
- distinct values: 3

### `arrival_date_month`

Month of arrival (English name).

- dtype: `str`, missing: 0
- distinct values: 12

| value | count | share | cancel rate |
|---|---|---|---|
| January | 5871 | 5.0% | 30.7% |
| February | 7998 | 6.7% | 33.6% |
| March | 9714 | 8.2% | 32.4% |
| April | 11045 | 9.3% | 40.9% |
| May | 11704 | 9.9% | 39.9% |
| June | 10891 | 9.2% | 41.6% |
| July | 12585 | 10.6% | 37.6% |
| August | 13808 | 11.6% | 37.9% |
| September | 10477 | 8.8% | 39.3% |
| October | 11064 | 9.3% | 38.4% |
| November | 6712 | 5.7% | 31.6% |
| December | 6689 | 5.6% | 35.4% |

### `arrival_date_week_number`

ISO week number of arrival.

- dtype: `int64`, missing: 0
- min 1, 25% 16, median 28, 75% 38, max 53, mean 27.16
- distinct values: 53

### `arrival_date_day_of_month`

Day of month of arrival.

- dtype: `int64`, missing: 0
- min 1, 25% 8, median 16, 75% 23, max 31, mean 15.80
- distinct values: 31

### `stays_in_weekend_nights`

Nights on Saturday/Sunday.

- dtype: `int64`, missing: 0
- min 0, 25% 0, median 1, 75% 2, max 19, mean 0.93
- distinct values: 17

### `stays_in_week_nights`

Nights Monday-Friday.

- dtype: `int64`, missing: 0
- min 0, 25% 1, median 2, 75% 3, max 50, mean 2.51
- distinct values: 33

### `adults`

Number of adults.

- dtype: `int64`, missing: 0
- min 0, 25% 2, median 2, 75% 2, max 55, mean 1.86
- distinct values: 14

### `children`

Number of children (raw 'NA' recoded to 0).

- dtype: `int64`, missing: 0
- min 0, 25% 0, median 0, 75% 0, max 10, mean 0.10
- distinct values: 5

### `babies`

Number of babies.

- dtype: `int64`, missing: 0
- min 0, 25% 0, median 0, 75% 0, max 10, mean 0.01
- distinct values: 5

### `meal`

Meal package: BB, HB, FB, SC (raw 'Undefined' merged into SC).

- dtype: `str`, missing: 0
- distinct values: 4

| value | count | share | cancel rate |
|---|---|---|---|
| BB | 91715 | 77.4% | 37.6% |
| HB | 14383 | 12.1% | 34.6% |
| SC | 11663 | 9.8% | 36.3% |
| FB | 797 | 0.7% | 60.0% |

### `country`

Country of origin, ISO 3166-3 code; empty = unknown.

- dtype: `str`, missing: 473
- distinct values: 177

| value | count | share | cancel rate |
|---|---|---|---|
| PRT | 47937 | 40.4% | 57.3% |
| GBR | 12094 | 10.2% | 20.3% |
| FRA | 10389 | 8.8% | 18.6% |
| ESP | 8544 | 7.2% | 25.5% |
| DEU | 7285 | 6.1% | 16.7% |
| ITA | 3756 | 3.2% | 35.5% |
| IRL | 3373 | 2.8% | 24.7% |
| BEL | 2338 | 2.0% | 20.2% |
| BRA | 2217 | 1.9% | 37.4% |
| NLD | 2101 | 1.8% | 18.4% |
| USA | 2089 | 1.8% | 24.0% |
| CHE | 1724 | 1.5% | 24.8% |
| CN | 1278 | 1.1% | 19.9% |
| AUT | 1262 | 1.1% | 18.1% |
| SWE | 1019 | 0.9% | 22.3% |
| ... (163 more values) | | | |

### `market_segment`

Market segment (Online TA, Offline TA/TO, Groups, Direct, Corporate, ...).

- dtype: `str`, missing: 0
- distinct values: 7

| value | count | share | cancel rate |
|---|---|---|---|
| Online TA | 56128 | 47.3% | 36.9% |
| Offline TA/TO | 24048 | 20.3% | 34.5% |
| Groups | 19758 | 16.7% | 61.2% |
| Direct | 12447 | 10.5% | 15.5% |
| Corporate | 5231 | 4.4% | 18.9% |
| Complementary | 715 | 0.6% | 12.2% |
| Aviation | 231 | 0.2% | 22.1% |

### `distribution_channel`

Distribution channel (TA/TO, Direct, Corporate, GDS).

- dtype: `str`, missing: 0
- distinct values: 4

| value | count | share | cancel rate |
|---|---|---|---|
| TA/TO | 97334 | 82.1% | 41.2% |
| Direct | 14450 | 12.2% | 17.6% |
| Corporate | 6584 | 5.6% | 22.2% |
| GDS | 190 | 0.2% | 19.5% |

### `is_repeated_guest`

1 = repeated guest.

- dtype: `int64`, missing: 0
- min 0, 25% 0, median 0, 75% 0, max 1, mean 0.03
- distinct values: 2

### `previous_cancellations`

Number of previous bookings canceled by the customer.

- dtype: `int64`, missing: 0
- min 0, 25% 0, median 0, 75% 0, max 26, mean 0.09
- distinct values: 15

### `previous_bookings_not_canceled`

Number of previous bookings not canceled by the customer.

- dtype: `int64`, missing: 0
- min 0, 25% 0, median 0, 75% 0, max 72, mean 0.14
- distinct values: 73

### `reserved_room_type`

Room type code reserved.

- dtype: `str`, missing: 0
- distinct values: 9

| value | count | share | cancel rate |
|---|---|---|---|
| A | 85395 | 72.0% | 39.4% |
| D | 19096 | 16.1% | 31.9% |
| E | 6482 | 5.5% | 29.4% |
| F | 2879 | 2.4% | 30.6% |
| G | 2074 | 1.7% | 36.8% |
| B | 1106 | 0.9% | 32.8% |
| C | 923 | 0.8% | 33.3% |
| H | 597 | 0.5% | 41.0% |
| L | 6 | 0.0% | 33.3% |

### `assigned_room_type`

Room type code assigned (post-booking information, may differ from reserved).

- dtype: `str`, missing: 0
- distinct values: 11

| value | count | share | cancel rate |
|---|---|---|---|
| A | 73787 | 62.2% | 44.6% |
| D | 25205 | 21.3% | 25.2% |
| E | 7763 | 6.5% | 25.3% |
| F | 3728 | 3.1% | 24.9% |
| G | 2532 | 2.1% | 30.8% |
| C | 2350 | 2.0% | 19.0% |
| B | 2139 | 1.8% | 23.7% |
| H | 707 | 0.6% | 35.5% |
| I | 219 | 0.2% | 1.8% |
| K | 127 | 0.1% | 7.9% |
| L | 1 | 0.0% | 100.0% |

### `booking_changes`

Number of changes made to the booking (post-booking information).

- dtype: `int64`, missing: 0
- min 0, 25% 0, median 0, 75% 0, max 18, mean 0.22
- distinct values: 19

### `deposit_type`

No Deposit / Non Refund / Refundable.

- dtype: `str`, missing: 0
- distinct values: 3

| value | count | share | cancel rate |
|---|---|---|---|
| No Deposit | 103810 | 87.6% | 28.6% |
| Non Refund | 14586 | 12.3% | 99.4% |
| Refundable | 162 | 0.1% | 22.2% |

### `agent`

ID of the travel agency; empty = booked without an agent.

- dtype: `Int64`, missing: 16076
- min 1, 25% 9, median 14, 75% 229, max 535, mean 86.52
- distinct values: 333

### `company`

ID of the company; empty = not a company booking.

- dtype: `Int64`, missing: 111863
- min 6, 25% 62, median 178, 75% 270, max 543, mean 189.14
- distinct values: 347

### `days_in_waiting_list`

Days the booking waited before confirmation.

- dtype: `int64`, missing: 0
- min 0, 25% 0, median 0, 75% 0, max 391, mean 2.33
- distinct values: 127

### `customer_type`

Transient / Transient-Party / Contract / Group.

- dtype: `str`, missing: 0
- distinct values: 4

| value | count | share | cancel rate |
|---|---|---|---|
| Transient | 88933 | 75.0% | 41.0% |
| Transient-Party | 25000 | 21.1% | 25.5% |
| Contract | 4056 | 3.4% | 31.1% |
| Group | 569 | 0.5% | 10.2% |

### `adr`

Average daily rate (sum of lodging transactions / staying nights).

- dtype: `float64`, missing: 0
- min 0, 25% 70, median 95, 75% 126, max 510, mean 102.48
- distinct values: 8864

### `required_car_parking_spaces`

Number of parking spaces required.

- dtype: `int64`, missing: 0
- min 0, 25% 0, median 0, 75% 0, max 8, mean 0.06
- distinct values: 5

### `total_of_special_requests`

Number of special requests.

- dtype: `int64`, missing: 0
- min 0, 25% 0, median 0, 75% 1, max 5, mean 0.57
- distinct values: 6

### `total_nights`

DERIVED. stays_in_weekend_nights + stays_in_week_nights.

- dtype: `int64`, missing: 0
- min 1, 25% 2, median 3, 75% 4, max 69, mean 3.44
- distinct values: 41

### `total_guests`

DERIVED. adults + children + babies.

- dtype: `int64`, missing: 0
- min 1, 25% 2, median 2, 75% 2, max 55, mean 1.97
- distinct values: 14

### `arrival_date`

DERIVED. Arrival date as ISO date (from year/month/day).

- dtype: `object`, missing: 0
- range: 2015-07-01 to 2017-08-31

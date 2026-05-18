# Tests

Minimum test coverage:
- indicator seed/import creates exactly 118 indicators
- indicator numbers are unique
- score summary calculates correctly
- evidence status updates current score correctly
- register entry creation works
- recurring due/overdue logic works
- printable report views return HTTP 200
- non-admin cannot edit locked master indicator fields
- deployment health endpoint returns HTTP 200

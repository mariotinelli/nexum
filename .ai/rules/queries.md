---
paths:
  - 'app/Brain/Queries/**'
---

# Queries

## Reserve Queries for complex reusable reads
Create a Brain Query only when a read is both complex and reusable. Keep simple or one-screen reads in Eloquent or a public local scope.

## Allowlist relationship-column sorting
For sortable relationship columns, join the related table, select aliased columns, and map requested sort names through an allowlist to real database columns.

## Suffix Brain Queries by type
Name every Brain Query with the Query suffix.

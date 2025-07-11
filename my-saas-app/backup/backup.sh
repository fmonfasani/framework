#!/bin/bash
pg_dump -h localhost -U postgres -d ${DB_NAME:-db} > backup.sql

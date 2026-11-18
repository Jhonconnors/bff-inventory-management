FROM postgres:16-alpine

COPY 01-esquema.sql /docker-entrypoint-initdb.d/01-esquema.sql
COPY 02-datos-prueba.sql /docker-entrypoint-initdb.d/02-datos-prueba.sql

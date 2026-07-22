# Apache Jena/Fuseki runtime

Runtime cô lập dùng riêng cho đánh giá semantic:

- `Dockerfile`: cài Fuseki 6.1.0 và kiểm SHA-512 archive.
- `config.ttl`: assembler dataset và SPARQL endpoint `/movies/sparql`.
- `movie.rules`: domain, range, inverse và symmetric rules.

Docker Compose mount ontology và RDF snapshot ở chế độ read-only. Service này
không nằm trên critical path của API hoặc `make demo`.

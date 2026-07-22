FROM eclipse-temurin:21-jre-jammy

ARG JENA_VERSION=6.1.0
ARG JENA_SHA512=75457f45d14397876a41ed51abe7ae5d2f1e708dfe1315765f858158bc5c6813bc036ec1539ddc4dffd26201f5cc31fadec299ca5c3dc2548b723513ed31d326

ADD https://archive.apache.org/dist/jena/binaries/apache-jena-fuseki-${JENA_VERSION}.tar.gz /tmp/fuseki.tar.gz
RUN echo "${JENA_SHA512}  /tmp/fuseki.tar.gz" | sha512sum -c - \
    && mkdir -p /opt/jena \
    && tar -xzf /tmp/fuseki.tar.gz --strip-components=1 -C /opt/jena \
    && rm /tmp/fuseki.tar.gz \
    && useradd --system --home /fuseki --create-home fuseki \
    && chown -R fuseki:fuseki /opt/jena /fuseki

USER fuseki
WORKDIR /fuseki
EXPOSE 3030
ENTRYPOINT ["/opt/jena/fuseki-server"]
CMD ["--config=/fuseki/config.ttl"]

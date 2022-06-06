FROM golang:1.16.2
RUN go get github.com/cosmtrek/air@v1.29.0
WORKDIR /go/src/app
COPY . .

ENV MODE=PRODUCT
RUN go build -o server .

# dockerize
ENV DOCKERIZE_VERSION v0.5.0

EXPOSE 8082

RUN curl -sL https://deb.nodesource.com/setup_6.x | bash \
  && apt-get install -y \
    wget \
  && wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
  && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
  && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
  && apt-get purge -y --auto-remove wget \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

CMD ["air", "-c", ".air.toml"]
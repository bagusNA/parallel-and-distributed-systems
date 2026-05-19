FROM golang:1.18-alpine

RUN mkdir /app

RUN addgroup -S etmin
RUN adduser -S -D -h /app bagus etmin
RUN chown -R bagus:etmin /app
USER bagus

COPY main.go /app

EXPOSE 8080
CMD go run /app/main.go
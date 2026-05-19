FROM alpine:3

LABEL author="Bagus"

RUN mkdir hello
RUN echo "Hello World" > "hello/world.txt"

CMD cat "hello/world.txt"


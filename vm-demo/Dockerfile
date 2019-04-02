FROM alpine:latest

RUN mkdir -p /app/data && \
	apk add \
	libstdc++ \
	python3 \
	libgcc \
    gcompat

ADD requirements.txt /app

RUN pip3 install -r /app/requirements.txt

WORKDIR /app/data
ADD constellation /app
ADD vm-lang /app
ADD monitor.py /app

EXPOSE 8000-8020

#ENTRYPOINT ["/app/monitor.py"]


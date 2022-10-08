FROM python:3-alpine

RUN apk add net-tools;apk add --update bind-tools;apk --no-cache add curl
RUN mkdir -p /app
ADD requirements.txt /app
RUN pip install -r /app/requirements.txt
COPY . /app
WORKDIR /app
ENV LOGO https://raw.githubusercontent.com/seungkyua/rsvpapp/master/static/k8s_logo.png
ENV COMPANY DEMO
EXPOSE 80
ENTRYPOINT ["python"]
CMD ["rsvp.py"]

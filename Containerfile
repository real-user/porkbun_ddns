FROM alpine:latest
RUN apk add python3 py3-pip && \
    pip install requests
WORKDIR /porkbun_ddns
COPY config.json porkbun-ddns.py domains.cfg .
CMD ["python3", "porkbun-ddns.py"] 

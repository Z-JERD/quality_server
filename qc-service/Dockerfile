FROM reg.xiaoneng.cn/centos/centos:7.2

COPY . /ai-qc/
WORKDIR /ai-qc

RUN  pip3 install -r requirements.txt -i http://pypi.douban.com/simple --trusted-host pypi.douban.com

ENV TZ "Asia/Shanghai"

ENTRYPOINT ["/bin/sh", "/ai-qc/docker-entrypoint.sh"]
CMD ["gunicorn", "AI.wsgi", "--workers=5", "--bind=0.0.0.0:8000", "--reload"]

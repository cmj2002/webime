FROM python:3.6
WORKDIR /app

COPY . .
RUN ls -a -l && pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

EXPOSE 80
CMD ["gunicorn", "server:server", "-c", "./gunicorn.conf.py"]
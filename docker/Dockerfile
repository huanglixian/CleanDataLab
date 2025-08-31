# 二阶段构建：Python构建 + 运行环境
FROM python:3.11-slim-amd64 AS python-builder
WORKDIR /app
COPY requirements.txt .
# 国内APT源加速
RUN sed -i 's@http://deb.debian.org@https://mirrors.aliyun.com@g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update \
    && apt-get install -y --no-install-recommends gcc g++ libc6-dev libffi-dev \
    && pip install --no-cache-dir --user -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn \
    && find /root/.local -name '*.pyc' -delete \
    && find /root/.local -name '__pycache__' -exec rm -rf {} + || true \
    && apt-get purge -y gcc g++ libc6-dev libffi-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* /tmp/* /root/.cache

# 运行环境
FROM python:3.11-slim-amd64 AS production
# 国内APT源加速
RUN sed -i 's@http://deb.debian.org@https://mirrors.aliyun.com@g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update \
    && apt-get install -y --no-install-recommends wget libreoffice-calc libreoffice-writer \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 复制Python包
COPY --from=python-builder /root/.local /usr/local

# 复制应用代码
COPY app.py ./
COPY README.md ./
COPY common/ ./common/
COPY pages/ ./pages/
COPY .streamlit/ ./.streamlit/

# 清理Python缓存
RUN find /usr/local -name '*.pyc' -delete \
    && find /usr/local -name '__pycache__' -exec rm -rf {} + || true

# 暴露端口
EXPOSE 8419

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8419/ || exit 1

# 启动命令
CMD ["/usr/local/bin/streamlit", "run", "app.py", "--server.port=8419", "--server.address=0.0.0.0"]
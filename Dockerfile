# Real-Time Transfer Scam Guard
#
# 基础镜像使用 IBM 官方为 s390x 预编译的 Jupyter AI/ML 镜像：
# 它已包含 TensorFlow / PyTorch / XGBoost / scikit-learn / llama-cpp-python
# 以及 IBM Granite GGUF，这些在 s390x 上无法通过 pip 直接安装。
#
# 构建：
#   docker build -t scam-guard:1.0 .
# 运行：
#   docker run -d --network host --name scam-guard \
#     -v /home/linux1/shared/fraud-shield/models:/app/models \
#     scam-guard:1.0
#
# 说明：--network host 是 LinuxONE Community Cloud 的推荐用法，
#       简化端口映射；如需隔离，可改为 -p 8000:8000。

FROM registry.linuxone.cloud.marist.edu/l1cc/jupyterlab-image-s390x:latest

LABEL org.opencontainers.image.title="Real-Time Transfer Scam Guard"
LABEL org.opencontainers.image.description="Streaming scam-transfer decision engine on IBM LinuxONE (s390x)"
LABEL org.opencontainers.image.version="1.0"

ENV PYTHONUNBUFFERED=1 \
    MODEL_DIR=/app/models \
    GRANITE_PATH=/home/ibm-user/granite-4.0-h-350m-base-be.f16.gguf

# 应用代码
WORKDIR /app
COPY app/ /app/app/
COPY static/ /app/static/
COPY tests/ /app/tests/
COPY train/ /app/train/
COPY benchmark.py /app/benchmark.py

# Web 运行时依赖（基础镜像未预装；均为纯 Python 包，s390x 可直接安装）
RUN python3 -m pip install --no-cache-dir --quiet \
        fastapi==0.143.3 uvicorn==0.54.0 pydantic==2.14.1

# 训练产物（也可用 volume 挂载，便于替换模型而不重建镜像）
COPY models/ /app/models/

# 确保应用与模型对所有用户可读
# 基础镜像以 USER 1000 运行，需临时切到 root 才能修正属主/权限
USER root
RUN find /app -name "._*" -delete 2>/dev/null; chmod -R a+rX /app
USER 1000

# 服务端口
EXPOSE 8000

# 健康检查：确认引擎与解释层都已就绪
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python3 -c "import urllib.request,sys; \
sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=4).status==200 else 1)"

# 单进程 uvicorn：3 vCPU 环境下避免多 worker 争抢，
# 决策路径与 Granite 解释共享 CPU 的取舍已在文档中说明。
CMD ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

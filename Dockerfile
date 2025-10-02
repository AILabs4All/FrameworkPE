# Dockerfile para Security Incident Framework
FROM python:3.11-slim

# Instalar dependências do sistema e ferramentas de compilação
RUN apt-get update && apt-get install -y \
    curl \
    jq \
    bash \
    gcc \
    g++ \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Copiar requirements e instalar dependências Python
COPY requirements-docker.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove \
        gcc \
        g++ \
        build-essential \
        python3-dev \
    && apt-get clean

# Copiar todo o código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p logs results data/output

# Tornar scripts executáveis
RUN chmod +x script.sh scripts/*.sh

# Definir variáveis de ambiente
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Usuário não-root para segurança
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Comando padrão
CMD ["bash"]
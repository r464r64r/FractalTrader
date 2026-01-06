# Fractal Trader Development Environment
# Compatible with Docker Desktop 4.15+ / Engine 20.10+

FROM python:3.11-slim-bookworm

LABEL maintainer="FractalTrader"
LABEL description="SMC Algorithmic Trading Development Environment"

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# System dependencies (minimal for vectorbt)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user (optional, for security)
# RUN useradd -m -s /bin/bash trader
# USER trader

WORKDIR /app

# Install Python dependencies in layers (better caching)
# Layer 1: Core scientific stack (rarely changes)
RUN pip install --no-cache-dir \
    numpy>=1.24.0 \
    pandas>=2.0.0 \
    scipy>=1.11.0

# Layer 2: vectorbt (heavy, cache separately)
RUN pip install --no-cache-dir vectorbt>=0.26.0

# Layer 3: Trading & development tools
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project (done last for better cache)
COPY . .

# Install project in editable mode
RUN pip install -e .

# Verify installation
RUN python3 -c "import vectorbt; print(f'vectorbt {vectorbt.__version__}')" && \
    python3 -c "from core.market_structure import find_swing_points; print('Core modules OK')"

# Default command
CMD ["bash"]

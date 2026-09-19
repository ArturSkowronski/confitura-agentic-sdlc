# Obraz kroków linii: build Javy, mózg fabryki w Pythonie, git, gitleaks (sekrety) i cosign (podpis księgi).
# Ten sam obraz z pakietem `mcp` służy jako serwer warsztatu (platforma/warsztat/Dockerfile).
FROM maven:3.9-eclipse-temurin-21
ARG GITLEAKS_VERSION=8.30.1
ARG COSIGN_VERSION=3.1.3
ARG TARGETARCH
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip jq git curl ca-certificates \
 && rm -rf /var/lib/apt/lists/* \
 && git config --system --add safe.directory '*' \
 && curl -fsSL "https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_linux_${TARGETARCH:-arm64}.tar.gz" | tar -xz -C /usr/local/bin gitleaks \
 && curl -fsSL -o /usr/local/bin/cosign "https://github.com/sigstore/cosign/releases/download/v${COSIGN_VERSION}/cosign-linux-${TARGETARCH:-arm64}" \
 && chmod +x /usr/local/bin/cosign
WORKDIR /work
CMD ["bash"]

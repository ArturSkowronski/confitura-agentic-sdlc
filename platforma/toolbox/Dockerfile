# Obraz kroków linii: build Javy, mózg fabryki w Pythonie, git, gitleaks (sekrety) i cosign (podpis księgi).
# Rozgrzewa cache Mavena dla system/ i scenarios/, żeby na sali nic nie ciągnąć z sieci.
# Kontekst builda to korzeń repo: docker build -f platforma/toolbox/Dockerfile .
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
COPY system /tmp/warm/system
COPY scenarios /tmp/warm/scenarios
RUN cd /tmp/warm/system && mvn -B -q verify -DskipTests && mvn -B -q install -DskipTests \
 && mvn -B -q org.pitest:pitest-maven:mutationCoverage -DskipTests -Dpit.skip=true >/dev/null 2>&1 || true \
 && cd /tmp/warm/scenarios && (mvn -B -q -fae test-compile >/dev/null 2>&1 || true) \
 && rm -rf /tmp/warm
WORKDIR /work
CMD ["bash"]

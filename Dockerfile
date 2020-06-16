ARG GIT_COMMIT=unspecified
ARG GIT_REMOTE=unspecified
ARG VERSION=unspecified

FROM python:3.7-alpine

ARG GIT_COMMIT
ARG GIT_REMOTE
ARG VERSION

LABEL git_commit=${GIT_COMMIT}
LABEL git_remote=${GIT_REMOTE}
LABEL maintainer="bryce.beuerlein@cisa.dhs.gov"
LABEL vendor="Cyber and Infrastructure Security Agency"
LABEL version=${VERSION}

ARG PCA_UID=421
ENV PCA_HOME="/home/pca"
ENV GOPHISH_TOOLS_SRC="/usr/src/gophish-tools"

RUN addgroup --system --gid ${PCA_UID} pca \
  && adduser --system --uid ${PCA_UID} --ingroup pca pca

RUN apk --update --no-cache add \
  bash \
  py-pip

VOLUME ${PCA_HOME}

WORKDIR ${GOPHISH_TOOLS_SRC}
COPY . ${GOPHISH_TOOLS_SRC}

RUN pip install --no-cache-dir .
RUN chmod +x ${GOPHISH_TOOLS_SRC}/var/getenv
RUN ln -snf ${GOPHISH_TOOLS_SRC}/var/getenv /usr/local/bin

USER pca
WORKDIR ${PCA_HOME}
CMD ["getenv"]

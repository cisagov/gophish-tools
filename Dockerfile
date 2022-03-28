ARG GIT_COMMIT=unspecified
ARG GIT_REMOTE=unspecified
ARG VERSION=unspecified

FROM python:3.9.11-alpine

ARG GIT_COMMIT
ARG GIT_REMOTE
ARG VERSION

LABEL git_commit=$GIT_COMMIT
LABEL git_remote=$GIT_REMOTE
LABEL maintainer="bryce.beuerlein@cisa.dhs.gov"
LABEL vendor="Cyber and Infrastructure Security Agency"
LABEL version=$VERSION

ARG CISA_UID=421
ENV CISA_HOME="/home/cisa"
ENV GOPHISH_TOOLS_SRC="/usr/src/gophish-tools"

RUN addgroup --system --gid $CISA_UID cisa \
  && adduser --system --uid $CISA_UID --ingroup cisa cisa

RUN apk --update --no-cache add \
  bash \
  py-pip

VOLUME $CISA_HOME

WORKDIR $GOPHISH_TOOLS_SRC
COPY . $GOPHISH_TOOLS_SRC

RUN pip install --no-cache-dir .
RUN chmod +x ${GOPHISH_TOOLS_SRC}/var/getenv
RUN ln -snf ${GOPHISH_TOOLS_SRC}/var/getenv /usr/local/bin

USER cisa
WORKDIR $CISA_HOME
CMD ["getenv"]

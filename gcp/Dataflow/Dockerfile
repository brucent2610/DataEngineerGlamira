FROM gcr.io/dataflow-templates-base/python3-template-launcher-base

ARG WORKDIR=/dataflow/template

RUN mkdir -p ${WORKDIR}
WORKDIR ${WORKDIR}

RUN apt-get update && apt-get install -y libffi-dev && rm -rf /var/lib/apt/lists/*

COPY data/* data
COPY glamira_streaming_pipeline.py .
COPY glamira_streaming_pipeline_test.py .

ENV FLEX_TEMPLATE_PYTHON_PY_FILE="${WORKDIR}/glamira_streaming_pipeline.py"

RUN python3 -m pip install apache-beam[gcp] IP2Location

RUN python3 ${WORKDIR}/glamira_streaming_pipeline_test.py

ENTRYPOINT ["/entrypoint.sh"]
CMD ["start"]
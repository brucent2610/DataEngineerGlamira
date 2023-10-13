FROM gcr.io/dataflow-templates-base/python3-template-launcher-base

ARG WORKDIR=/dataflow/template

RUN mkdir -p ${WORKDIR}
WORKDIR ${WORKDIR}

RUN pip install --upgrade pip

RUN apt-get update && apt-get install -y libffi-dev unzip && rm -rf /var/lib/apt/lists/*

COPY glamira_streaming_pipeline.py .
COPY IP2Location.zip .
COPY Ip2location_test.py .

ENV FLEX_TEMPLATE_PYTHON_PY_FILE="${WORKDIR}/glamira_streaming_pipeline.py"

RUN python3 -m pip install apache-beam[gcp]

RUN unzip IP2Location.zip -d IP2Location
RUN cd ${WORKDIR}/IP2Location/IP2Location-Python-master && python3 setup.py build && python3 setup.py install

RUN python3 Ip2location_test.py


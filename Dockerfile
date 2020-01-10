FROM inspirehep/poetry:2.7

ENTRYPOINT [ "" ]

RUN echo "deb https://deb.nodesource.com/node_12.x buster main" > /etc/apt/sources.list.d/nodesource.list && \
    wget -qO- https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add - && \
    echo "deb https://dl.yarnpkg.com/debian/ stable main" > /etc/apt/sources.list.d/yarn.list && \
    wget -qO- https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - && \
    apt-get update && \
    apt-get install -yqq --no-install-recommends imagemagick && \
    apt-get install -yqq --no-install-recommends uuid-dev && \
    apt-get install -yqq nodejs yarn  && \
    sed -i 's/domain="coder" rights="none"/domain="coder" rights="read\|write"/' /etc/ImageMagick-6/policy.xml

COPY . /code
WORKDIR /code

RUN npm install -g --unsafe-perm \
        node-sass \
        clean-css@^3.4.24 \
        requirejs \
        uglify-js

RUN pip install pip --upgrade && \
    poetry install -E all -E xrootd -n

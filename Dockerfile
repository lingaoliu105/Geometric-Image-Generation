FROM texlive/texlive:latest
WORKDIR /
COPY requirements.txt /
RUN apt update
RUN apt -y install pip
RUN apt -y install poppler-utils
RUN pip install -r requirements.txt --break-system-packages
COPY ./ /


FROM computas/fyc-base:latest

RUN set -ex \
  && apt-get update && apt-get install -y \
    build-essential \
    cmake \
    unzip \
    pkg-config \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libgtk-3-dev \
    libatlas-base-dev \
    gfortran \
    wget \
  && pip install numpy==1.14.5 \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* \
  && rm -rf ~/.cache/pip

WORKDIR /opt
RUN set -ex \
  && wget -q -O opencv.zip https://github.com/opencv/opencv/archive/3.4.1.zip \
  && wget -q -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/3.4.1.zip \
  && unzip -q opencv.zip \
  && unzip -q opencv_contrib.zip \
  && mkdir opencv-3.4.1/build \
  && cd opencv-3.4.1/build \
  && cmake \
    -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D OPENCV_EXTRA_MODULES_PATH=/opt/opencv_contrib-3.4.1/modules \
    -D BUILD_DOCS=OFF \
    -D BUILD_EXAMPLES=OFF \
    -D BUILD_TESTS=OFF \
    -D BUILD_PERF_TESTS=OFF \
    -D BUILD_opencv_java=OFF \
    -D WITH_TBB=ON \
    -D WITH_QT=OFF \
    -D WITH_CUDA=OFF \
    -D WITH_FFMPEG=OFF \
    .. \
  && make -j $(nproc) \
  && make install \
  && ldconfig \
  && cd /usr/local/lib/python3.6/dist-packages/ \
  && mv cv2.cpython-36m-x86_64-linux-gnu.so cv2.so \
  && cd /opt \
  && rm -f opencv.zip opencv_contrib.zip \
  && rm -rf opencv-3.4.1 opencv_contrib-3.4.1 \

#!/bin/bash
CMAKE_BUILD_DIR=build-alpine

mkdir -p "$CMAKE_BUILD_DIR"
cd "$CMAKE_BUILD_DIR"

cmake -DFETCH_STATIC_LINK=ON ..
make -j "$@"


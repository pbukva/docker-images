#!/bin/bash

DOCKER_IMAGE_TAG=fetch-ledger-develop:latest
DOCKERFILE=./Dockerfile
DOCKER_BUILD_CONTEXT_DIR=../
WORKDIR=/build
DOCKER_LOCAL_MAKE=cmake-make.sh


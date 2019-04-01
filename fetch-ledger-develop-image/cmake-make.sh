#!/bin/bash -e

CMAKE_BUILD_DIR=build

mkdir -p "$CMAKE_BUILD_DIR"
cd "$CMAKE_BUILD_DIR"

split_params()
{
  local CALLBACK_FNC_NAME=$1
  local LEFT_PARAMS_GROUP=
  local RIGHT_PARAMS_GROUP=
  local FOUND=false

  # ommiting the first parameter in the $@ array (making $@ params
  # array to start from its originally second item)
  shift
  
  for i in "$@"
  do
    if [[ "$FOUND" != "true" ]] && [[ "$i" == "--" ]]
    then
      FOUND=true
      LEFT_PARAMS_GROUP=$RIGHT_PARAMS_GROUP
      RIGHT_PARAMS_GROUP=
      continue;
    fi

    local escaped_i=$i
    if [[ $i =~ [[:space:]] ]]
    then
      escaped_i=\"${i/\"/\\\"}\"
    fi

    RIGHT_PARAMS_GROUP=$RIGHT_PARAMS_GROUP" "$escaped_i
  done

  "$CALLBACK_FNC_NAME" "$LEFT_PARAMS_GROUP" "$RIGHT_PARAMS_GROUP"
}

run_build() {
    local CMAKE_PARAMS="$1"
    local MAKE_PARAMS="$2"
    local CMAKE_COMMAND="cmake $CMAKE_PARAMS .."
    local MAKE_COMMAND="make -j $MAKE_PARAMS"
    echo $CMAKE_COMMAND
    $CMAKE_COMMAND
    echo $MAKE_COMMAND
    $MAKE_COMMAND
}

split_params run_build "$@"


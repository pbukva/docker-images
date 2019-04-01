#!/usr/bin/env python3
import os
import shutil
import subprocess
import argparse

GCR_PROJECT = 'organic-storm-201412'

PROJECT_PATH = os.path.abspath(os.getcwd())
DOCKER_IMAGES_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ALPINE_PATH = os.path.join(DOCKER_IMAGES_PATH, 'fetch-ledger-develop-image')

def parse_commandline():
    parser = argparse.ArgumentParser()
    parser.add_argument('--rebuild', action='store_true', help='Rebuild the image')
    parser.add_argument('-p', '--publish', action='store_true', help='Publish the image to GCR')
    return parser.parse_args()


def check_project_path():
    tests = [
        os.path.isdir(PROJECT_PATH),
        os.path.isfile(os.path.join(PROJECT_PATH, 'CMakeLists.txt')),
        os.path.isfile(os.path.join(PROJECT_PATH, 'Jenkinsfile')),
        os.path.isfile(os.path.join(PROJECT_PATH, 'LICENSE')),
        os.path.isfile(os.path.join(PROJECT_PATH, 'README.md')),
    ]

    if not all(tests):
        raise RuntimeError('Failed to detect project layout')


def get_project_version():
    return subprocess.check_output(['git', 'describe', '--dirty=-wip'], cwd=PROJECT_PATH).decode().strip()


def build_alpine_constellation():
    build_image_script_path = os.path.join(ALPINE_PATH, 'scripts', 'docker-build-img.sh')
    docker_build_path = os.path.join(ALPINE_PATH, 'scripts', 'docker-run.sh')
    compile_script_path = os.path.join('/docker-images', 'fetch-ledger-develop-image', 'cmake-make.sh')

    # build the image
    subprocess.check_call([build_image_script_path], cwd=PROJECT_PATH)

    # compile the code (inside the development image)
    user_id = '{}:{}'.format(os.geteuid(), os.getegid())
    subprocess.check_call([docker_build_path, '-u', user_id, '--', compile_script_path, '-DFETCH_STATIC_LINK=ON', '-DFETCH_VERBOSE_CMAKE=ON', '--', 'constellation'], cwd=PROJECT_PATH)
    subprocess.check_call([docker_build_path, '-u', user_id, '--', compile_script_path, '-DFETCH_STATIC_LINK=ON', '-DFETCH_VERBOSE_CMAKE=ON', '--', 'vm-lang'], cwd=PROJECT_PATH)


def main():
    working_path = os.path.dirname(__file__)

    args = parse_commandline()

    # build the parent project first
    check_project_path()
    version = get_project_version()
    build_root = os.path.abspath(os.path.join(PROJECT_PATH, 'build'))

    latest_docker_tag = 'fetch-vm-demo:latest'
    local_docker_tag = 'fetch-vm-demo:{}'.format(version)
    remote_docker_tag = 'gcr.io/{}/{}'.format(GCR_PROJECT, local_docker_tag)

    # clean up
    if args.rebuild:
        shutil.rmtree(build_root)
        os.makedirs(build_root, exist_ok=True)

    # compile the project
    build_alpine_constellation()

    # detect the build folder
    if not os.path.isdir(build_root):
        raise RuntimeError('Unable to find build root at: {}'.format(build_root))

    # copy the output folder
    constellation_app_path = os.path.join(build_root, 'apps', 'constellation', 'constellation')
    shutil.copy(constellation_app_path, working_path)

    vm_lang_app_path = os.path.join(build_root, 'apps', 'vm-lang', 'vm-lang')
    shutil.copy(vm_lang_app_path, working_path)


    # build the docker image
    cmd = [
        'docker',
        'build',
        '-t', latest_docker_tag,
        '.'
    ]
    subprocess.check_call(cmd, cwd=working_path)

    # also do the tag the image
    cmd = [
        'docker',
        'tag',
        latest_docker_tag,
        local_docker_tag,
    ]
    subprocess.check_call(cmd, cwd=working_path)

    if args.publish:

        # make the remote tag
        cmd = [
            'docker',
            'tag',
            local_docker_tag,
            remote_docker_tag,
        ]
        subprocess.check_call(cmd)

        # push the remote tag
        cmd = [
            'docker',
            'push',
            remote_docker_tag
        ]
        subprocess.check_call(cmd)


if __name__ == '__main__':
    main()

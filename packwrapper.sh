#!/bin/bash

parse_args() {
    
    if [ $# -eq 0 ]; then
        show_usage1
        exit 0
    fi

    case $1 in
        requirementsGenerate | reqGen)
            pip install pipreqs
            pipreqs . --encoding=utf8 --force
            exit 0
            ;;
        requirementsInstall | reqInstl)
            pip install -r requirements.txt
            exit 0
            ;;
        build)
            python PackWrapperLauncher.py
            exit 0
            ;;
        init | download | downl)
            python PackWrapperDownloader.py
            exit 0
            ;;
        --help | -h)
            show_usage2
            exit 0
            ;;
        *)
            echo "Unknown command: $1"
            show_usage1
            exit 1
            ;;
    esac
}

show_usage1() {
    echo "No arguments provided, please use one of the following:"
    echo
    show_usage2
}

show_usage2() {
    echo "Tasks:"
    echo "  requirementsGenerate, reqGen"
    echo "  requirementsInstall, reqInstl"
    echo "  build"
    echo "  init, download, downl"
    echo
    echo "Options:"
    echo "  -h, --help    Show this help message"
}

parse_args "$@"
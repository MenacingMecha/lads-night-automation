#!/usr/bin/env sh

py generate_playlist.py
mpv --playlist=playlist.txt
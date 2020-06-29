#!/usr/bin/env python3

import os
import glob
import random
from typing import List, TextIO

class Playlist:
    def __init__(self, playlist_file: TextIO, num_of_inbetweens: int):
        self._playlist_file = playlist_file
        self._num_of_inbetweens = num_of_inbetweens
    
    def add_clip(self, path_to_clip: str):
        self._playlist_file.write(path_to_clip)
        self._playlist_file.write("\n")
    
    def add_show(self, path_to_show: List[str], path_to_inbetweens: List[str], should_end_with_inbetweens: bool):
        while len(path_to_show) > 0:
            self.add_clip(path_to_show.pop(0))
            should_add_inbetween = True
            if len(path_to_show) == 0 and not should_end_with_inbetweens:
                should_add_inbetween = False
            if should_add_inbetween:
                for x in range(self._num_of_inbetweens):
                    self.add_clip(path_to_inbetweens.pop())

def get_clips_from_dir(directory: str, should_shuffle: bool) -> List[str]:
    clips = []
    for ext in ('*.mp4', '*.mkv'):
        clips.extend(glob.glob(os.path.join(directory, ext)))
    if should_shuffle:
        random.shuffle(clips)
    return clips

if __name__ == "__main__":
    intros = get_clips_from_dir("intro", True)
    inbetweens = get_clips_from_dir("inbetween", True)
    intermissions = get_clips_from_dir("intermission", True)
    outros = get_clips_from_dir("outro", True)
    first_show = get_clips_from_dir("show_01", False)
    second_show = get_clips_from_dir("show_02", False)
    third_show = get_clips_from_dir("show_03", False)
    playlist_path = "playlist.txt"
    with open(playlist_path, "w") as playlist_file:
        playlist = Playlist(playlist_file, 2)
        playlist.add_clip(intros.pop())
        playlist.add_show(first_show, inbetweens, True)
        playlist.add_show(second_show, inbetweens, False)
        playlist.add_clip(intermissions.pop())
        playlist.add_show(third_show, inbetweens, False)
        playlist.add_clip(outros.pop())

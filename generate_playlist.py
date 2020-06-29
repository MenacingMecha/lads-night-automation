#!/usr/bin/env python3

import os
import glob
import random
from typing import List, TextIO

class Playlist:
    def __init__(self, playlist_file: TextIO, inbetweens: List[str], num_of_inbetweens: int):
        self._playlist_file = playlist_file
        self._inbetweens = inbetweens
        self._num_of_inbetweens = num_of_inbetweens
    
    def add_clip(self, path_to_clip: str):
        self._playlist_file.write(path_to_clip)
        self._playlist_file.write("\n")
    
    def add_show(self, path_to_show: List[str], should_end_with_inbetweens: bool):
        while len(path_to_show) > 0:
            self.add_clip(path_to_show.pop(0))
            should_add_inbetween = True
            if len(path_to_show) == 0 and not should_end_with_inbetweens:
                should_add_inbetween = False
            if should_add_inbetween:
                for x in range(self._num_of_inbetweens):
                    self.add_clip(self._inbetweens.pop())

class ClipGroups:
    def __init__(self):
        self._clip_groups = {}
    
    def add_clips_from_dir(self, group_name: str, path_to_dir: str, randomise_order: bool):
        clips = []
        for ext in ('*.mp4', '*.mkv'):
            clips.extend(glob.glob(os.path.join(path_to_dir, ext)))
        if randomise_order:
            random.shuffle(clips)
        self._clip_groups[group_name] = clips

    def get_clip_from_group(self, group_name: str) -> str:
        return self._clip_groups[group_name].pop(0)
    
    def get_clip_group(self, group_name: str) -> List[str]:
        return self._clip_groups[group_name]

if __name__ == "__main__":
    temp_blocklist_path = "temp_blocklist.txt"
    clip_groups.add_clips_from_dir("intro", "intro", True)
    clip_groups.add_clips_from_dir("inbetween", "inbetween", True)
    clip_groups.add_clips_from_dir("intermission", "intermission", True)
    clip_groups.add_clips_from_dir("outro", "outro", True)
    clip_groups.add_clips_from_dir("show_01", "show_01", False)
    clip_groups.add_clips_from_dir("show_02", "show_02", False)
    clip_groups.add_clips_from_dir("show_03", "show_03", False)
    playlist_path = "playlist.txt"
    with open(playlist_path, "w") as playlist_file:
        playlist = Playlist(playlist_file, clip_groups.get_clip_group("inbetween"), 2)
        playlist.add_clip(clip_groups.get_clip_from_group("intro"))
        playlist.add_show(clip_groups.get_clip_group("show_01"), True)
        playlist.add_show(clip_groups.get_clip_group("show_02"), False)
        playlist.add_clip(clip_groups.get_clip_from_group("intermission"))
        playlist.add_show(clip_groups.get_clip_group("show_03"), False)
        playlist.add_clip(clip_groups.get_clip_from_group("outro"))

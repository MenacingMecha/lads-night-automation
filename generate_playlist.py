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
        self._temp_blocklist_additions = []
    
    def add_clip(self, path_to_clip: str, add_to_temp_blocklist: bool):
        self._playlist_file.write(path_to_clip)
        self._playlist_file.write("\n")
        if add_to_temp_blocklist:
            self._temp_blocklist_additions.append(path_to_clip)
    
    def add_show(self, path_to_show: List[str], should_end_with_inbetweens: bool):
        while len(path_to_show) > 0:
            self.add_clip(path_to_show.pop(0), False)
            should_add_inbetween = True
            if len(path_to_show) == 0 and not should_end_with_inbetweens:
                should_add_inbetween = False
            if should_add_inbetween:
                for x in range(self._num_of_inbetweens):
                    self.add_clip(self._inbetweens.pop(), True)
    
    def get_temp_blocklist_additions(self) -> List[str]:
        return self._temp_blocklist_additions

class ClipGroups:
    def __init__(self, temp_blocklist_file: TextIO):
        if temp_blocklist_file is not None:
            self._temp_blocklist = temp_blocklist_file.read().splitlines()
        else:
            self._temp_blocklist = []
        self._clip_groups = {}
    
    def add_clips_from_dir(self, group_name: str, path_to_dir: str, randomise_order: bool):
        clips = []
        for ext in ('*.mp4', '*.mkv'):
            clips.extend(glob.glob(os.path.join(path_to_dir, ext)))
        for clip in clips:
            if clip in self._temp_blocklist:
                clips.remove(clip)
        if randomise_order:
            random.shuffle(clips)
        self._clip_groups[group_name] = clips

    def get_clip_from_group(self, group_name: str) -> str:
        return self._clip_groups[group_name].pop(0)
    
    def get_clip_group(self, group_name: str) -> List[str]:
        return self._clip_groups[group_name]

if __name__ == "__main__":
    temp_blocklist_path = "temp_blocklist.txt"
    try:
        os.path.isfile(temp_blocklist_path)
    except NameError:
        clip_groups = ClipGroups(None)
    else:
        with open(temp_blocklist_path, "r") as temp_blocklist_file:
            clip_groups = ClipGroups(temp_blocklist_file)
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
        playlist.add_clip(clip_groups.get_clip_from_group("intro"), False)
        playlist.add_show(clip_groups.get_clip_group("show_01"), True)
        playlist.add_show(clip_groups.get_clip_group("show_02"), False)
        playlist.add_clip(clip_groups.get_clip_from_group("intermission"), False)
        playlist.add_show(clip_groups.get_clip_group("show_03"), False)
        playlist.add_clip(clip_groups.get_clip_from_group("outro"), True)
    with open(temp_blocklist_path, "w") as temp_blocklist_file:
        temp_blocklist_file.writelines(x + "\n" for x in playlist.get_temp_blocklist_additions())

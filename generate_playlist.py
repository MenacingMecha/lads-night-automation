#!/usr/bin/env python3

import os
import glob
import random
import yaml
from typing import List, TextIO

class Playlist:
    def __init__(self, playlist_file: TextIO):
        self._playlist_file = playlist_file
        self._temp_blocklist_additions = []
    
    def add_clip(self, path_to_clip: str, add_to_temp_blocklist: bool):
        self._playlist_file.write(path_to_clip)
        self._playlist_file.write("\n")
        if add_to_temp_blocklist:
            self._temp_blocklist_additions.append(path_to_clip)
    
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
            clips.extend(glob.glob(os.path.join(os.path.expanduser(path_to_dir), ext)))
        for clip in clips:
            if clip in self._temp_blocklist:
                clips.remove(clip)
        if randomise_order:
            random.shuffle(clips)
        else:
            clips.sort()
        self._clip_groups[group_name] = clips

    def get_clip_from_group(self, group_name: str) -> str:
        return self._clip_groups[group_name].pop(0)
    
if __name__ == "__main__":
    temp_blocklist_path = "temp_blocklist.txt"
    if (os.path.isfile(temp_blocklist_path)):
        with open(temp_blocklist_path, "r") as temp_blocklist_file:
            clip_groups = ClipGroups(temp_blocklist_file)
    else:
        clip_groups = ClipGroups(None)

    config_path = "lads-night.yaml"
    with open(config_path) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
        for key, value in config["clip groups"].items():
            clip_groups.add_clips_from_dir(key, value["path"], value["shuffle"])

        playlist_path = "playlist.txt"
        with open(playlist_path, "w") as playlist_file:
            playlist = Playlist(playlist_file)
            for group in config["schedule"]:
                playlist.add_clip(clip_groups.get_clip_from_group(group), config["clip groups"][group]["blocklist type"] == "temporary")

    with open(temp_blocklist_path, "w") as temp_blocklist_file:
        temp_blocklist_file.writelines(x + "\n" for x in playlist.get_temp_blocklist_additions())

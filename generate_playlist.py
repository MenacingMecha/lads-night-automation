#!/usr/bin/env python3

import os
import glob
import random
import yaml
import logging
from typing import List, TextIO

class Playlist:
    def __init__(self, playlist_file: TextIO):
        self._playlist_file = playlist_file
        self._temp_blocklist_additions = []
        self._perm_blocklist_additions = []
    
    def add_clip(self, path_to_clip: str, blocklist_type: str):
        if path_to_clip is not None:
            self._playlist_file.write(path_to_clip)
            self._playlist_file.write("\n")
            if blocklist_type == "temporary":
                self._temp_blocklist_additions.append(path_to_clip)
            elif blocklist_type == "permanent":
                self._perm_blocklist_additions.append(path_to_clip)
    
    def get_temp_blocklist_additions(self) -> List[str]:
        return self._temp_blocklist_additions

    def get_perm_blocklist_additions(self) -> List[str]:
        return self._perm_blocklist_additions

class ClipGroups:
    def __init__(self, temp_blocklist: List[str], perm_blocklist: List[str]):
        self._temp_blocklist = temp_blocklist
        self._perm_blocklist = perm_blocklist
        self._clip_groups = {}
    
    def add_clips_from_dir(self, group_name: str, path_to_dir: str, randomise_order: bool):
        clips = []
        for ext in ('*.mp4', '*.mkv'):
            clips.extend(glob.glob(os.path.join(os.path.expanduser(path_to_dir), ext)))
        valid_clips = []
        for clip in clips:
            if clip not in self.__get_blocklist():
                valid_clips.append(clip)
        if len(valid_clips) == 0:
            logging.warning("Group '" + group_name + "' has no valid clips.") 
        if randomise_order:
            random.shuffle(valid_clips)
        else:
            valid_clips.sort()
        self._clip_groups[group_name] = valid_clips

    def get_clip_from_group(self, group_name: str) -> str:
        if (len(self._clip_groups[group_name]) > 0):
            return self._clip_groups[group_name].pop(0)
        else:
            return None
    
    def __get_blocklist(self) -> List[str]:
        return self._temp_blocklist + self._perm_blocklist

def get_blocklist_from_file(path: str) -> List[str]:
    if (os.path.isfile(path)):
        with open(path, "r") as file:
            blocklist = file.read().splitlines()
    else:
        blocklist = []
    return blocklist

if __name__ == "__main__":
    temp_blocklist_path = "temp_blocklist.txt"
    perm_blocklist_path = "perm_blocklist.txt"
    clip_groups = ClipGroups(get_blocklist_from_file(temp_blocklist_path), get_blocklist_from_file(perm_blocklist_path))
    # print(clip_groups._temp_blocklist + clip_groups._perm_blocklist)

    config_path = "lads-night.yaml"
    with open(config_path) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
        for key, value in config["clip groups"].items():
            clip_groups.add_clips_from_dir(key, value["path"], value["shuffle"])

        playlist_path = "playlist.txt"
        with open(playlist_path, "w") as playlist_file:
            playlist = Playlist(playlist_file)
            for group in config["schedule"]:
                playlist.add_clip(clip_groups.get_clip_from_group(group), config["clip groups"][group]["blocklist type"])

    with open(temp_blocklist_path, "w") as temp_blocklist_file:
        temp_blocklist_file.writelines(x + "\n" for x in playlist.get_temp_blocklist_additions())

    with open(perm_blocklist_path, "a") as perm_blocklist_file:
        perm_blocklist_file.writelines(x + "\n" for x in playlist.get_perm_blocklist_additions())
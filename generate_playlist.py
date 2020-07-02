#!/usr/bin/env python3

import os
import glob
import random
import yaml
import logging
import argparse
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
    blocklist = []
    if path is not None:
        if (os.path.isfile(path)):
            with open(path, "r") as file:
                blocklist = file.read().splitlines()
    return blocklist

def config_has_key(config: dict, key: str, key_location: str) -> bool:
    try:
        config[key]
    except KeyError:
        logging.exception("Key: '" + key + "' not found in '" + key_location + "'")
    else:
        return True

def write_to_blocklist(blocklist_path: str, blocklist_additions: List[str], file_mode: str):
    if blocklist_path is not None:
        with open(blocklist_path, file_mode) as blocklist_file:
            blocklist_file.writelines(x + "\n" for x in blocklist_additions)

def get_args() -> argparse:
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', dest="config_path", type=str, default='config.yaml', help="Specify an alternate config path. Defaults to 'config.yaml'.")
    return parser.parse_args()

if __name__ == "__main__":
    with open(get_args().config_path) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
    
    if config_has_key(config, "blocklist paths", "base yaml"):
        config_blocklist_paths = config["blocklist paths"]
        if config_has_key(config_blocklist_paths, "temporary", "blocklist paths"):
            temp_blocklist_path = config_blocklist_paths["temporary"]
        else:
            temp_blocklist_path = None
        if config_has_key(config_blocklist_paths, "permanent", "blocklist paths"):
            perm_blocklist_path = config_blocklist_paths["permanent"]
        else:
            perm_blocklist_path = None

    clip_groups = ClipGroups(get_blocklist_from_file(temp_blocklist_path), get_blocklist_from_file(perm_blocklist_path))

    if config_has_key(config, "clip groups", "base yaml"):
        config_clip_groups = config["clip groups"]
        try:
            config_clip_groups.keys()
        except AttributeError:
            logging.exception("'clip groups' contains no entries")
        else:
            for key, value in config_clip_groups.items():
                if config_has_key(value, "path", key) and config_has_key(value, "shuffle", key):
                    clip_groups.add_clips_from_dir(key, value["path"], value["shuffle"])

    playlist_path = "playlist.txt"
    with open(playlist_path, "w") as playlist_file:
        playlist = Playlist(playlist_file)
        if config_has_key(config, "schedule", "base yaml"):
            try:
                len(config["schedule"]) < 1
            except TypeError:
                logging.exception("Schedule contains no entries")
            else:
                for group in config["schedule"]:
                    if config_has_key(config["clip groups"][group], "blocklist type", group):
                        playlist.add_clip(clip_groups.get_clip_from_group(group), config["clip groups"][group]["blocklist type"])

    write_to_blocklist(temp_blocklist_path, playlist.get_temp_blocklist_additions(), "w")
    write_to_blocklist(perm_blocklist_path, playlist.get_perm_blocklist_additions(), "a")
#!/usr/bin/env python3

import yaml

if __name__ == "__main__":
    config = dict(
        blocklist_paths = dict(
            temporary = "temp_blocklist.txt",
            permanent = "perm_blocklist.txt"
        ),
        clip_groups = dict(
            example_show_01 = dict(
                path = "path/to/dir",
                shuffle = True,
                blocklist_type = "temporary"
            ),
            example_show_02 = dict(
                path = "path/to/dir",
                shuffle = False,
                blocklist_type = "permanent"
            )
        ),
        schedule = [
            "example_show_01",
            "example_show_02",
            "example_show_01",
            "example_show_02"
        ]
    )

    config_path = "config.yaml"
    with open(config_path, "w") as config_file:
        yaml.dump(config, config_file)

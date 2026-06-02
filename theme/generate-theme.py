#!/usr/bin/env python3

import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "theme"

PALETTE_KEYS = [
    "bg",
    "main_border",
    "dark_purple",
    "light_purple",
    "pop_border",
    "inner_border",
    "text_special",
    "text_muted",
    "text_bright",
    "select",
    "black"
]

with open(CONFIG_DIR / "palette.json") as f:
    colors = json.load(f)

for key in PALETTE_KEYS:
    if key not in colors:
        raise ValueError(f"Missing palette key: {key}")

# ------------------------
# Sway
# ------------------------

sway = f"""set $bg      {colors["bg"]} 
set $main_border      {colors["main_border"]}
set $dark_purple  {colors["dark_purple"]}
set $light_purple {colors["light_purple"]}
set $pop_border    {colors["pop_border"]}
set $text_special    {colors["text_special"]}
set $text_muted   {colors["text_muted"]}
set $text_bright  {colors["text_bright"]}
"""

(CONFIG_DIR / "sway-colors.conf").write_text(sway)

# ------------------------
# Waybar
# ------------------------

waybar = f"""@define-color bg {colors["bg"]};
@define-color main_border {colors["main_border"]};
@define-color dark_purple {colors["dark_purple"]};
@define-color light_purple {colors["light_purple"]};
@define-color pop_border {colors["pop_border"]};
@define-color text_special {colors["text_special"]};
@define-color text_muted {colors["text_muted"]};
@define-color text_bright {colors["text_bright"]};
"""

(CONFIG_DIR / "waybar-colors.css").write_text(waybar)

# ------------------------
# Foot
# ------------------------

strip = lambda c: c.lstrip("#")

foot = f"""
[csd]
border-width=10
border-color={strip(colors["light_purple"])}
[main]
pad=8x8 center
[colors-dark]

background={strip(colors["bg"])}
foreground={strip(colors["text_bright"])}

regular0={strip(colors["dark_purple"])}
regular1={strip(colors["pop_border"])}
regular2={strip(colors["light_purple"])}
regular6={strip(colors["text_special"])}

selection-background={strip(colors["text_special"])}
selection-foreground={strip(colors["bg"])}
"""

(CONFIG_DIR / "foot-theme.ini").write_text(foot)

# ------------------------
# Rofi
# ------------------------

rofi = f"""* {{
    bg:     {colors["bg"]};
    fg:     {colors["text_muted"]};
    popborder:   {colors["pop_border"]};
    dark:   {colors["dark_purple"]};
    light:  {colors["light_purple"]};
    bright: {colors["text_bright"]};
    textspecial: {colors["text_special"]};
    select: {colors["select"]};
    black: {colors["black"]};
}}
"""

(CONFIG_DIR / "rofi-colors.rasi").write_text(rofi)
print("Theme files generated.")
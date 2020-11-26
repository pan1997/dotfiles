#!/bin/bash

zscroll -l 30 \
        --delay 0.1 \
        --match-command "playerctl status" \
        --match-text "" "--scroll 1" \
        --match-text "" "--scroll 0" \
        --update-check true ~/.config/waybar/scripts/playerctl.sh &

wait

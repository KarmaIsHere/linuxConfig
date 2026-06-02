source /usr/share/cachyos-fish-config/cachyos-config.fish

function kswayconfig
    set file ~/.config/sway/config

    if test (count $argv) -gt 0
        set file $file.$argv[1]
    end

    code $file
end

function kcolors
        # 3. Try running the theme engine script
    if not python3 ~/.config/theme/generate-theme.py
        echo "Warning: Configs updated, but Python theme engine failed to run." >&2
        return 1
    end
end

function kswayup
    read -P "Apply Valhalla config? [y/N] " reply

    if string match -qr '^(y|yes)$' -- (string lower $reply)
        # 1. Try backing up the original config
        if not cp ~/.config/sway/config ~/.config/sway/config.bak
            echo "Error: Failed to create config backup." >&2
            return 1
        end

        # 2. Try copying the Valhalla config over
        if not cp ~/.config/sway/config.vallhalla ~/.config/sway/config
            echo "Error: Failed to copy Valhalla config over active config." >&2
            return 1
        end

        echo "Sway config updated successfully."

        # 3. Try running the theme engine script
        if not python3 ~/.config/theme/generate-theme.py
            echo "Warning: Configs updated, but Python theme engine failed to run." >&2
            return 1
        end

        echo "Theme generated. Run 'swaymsg reload' if things look stagnant!"
    else
        echo "Cancelled."
    end
end

        if not python3 ~/.config/theme/generate-theme.py
            echo "Warning: Configs updated, but Python theme engine failed to run." >&2
            return 1
        end


function kswaydown
    read -P "Restore backup config? [y/N] " reply

    if string match -qr '^(y|yes)$' -- (string lower $reply)
        cp ~/.config/sway/config.bak ~/.config/sway/config
        and echo "Restored."
    else
        echo "Cancelled."
    end
end


# overwrite greeting
# potentially disabling fastfetch
#function fish_greeting
#    # smth smth
#end

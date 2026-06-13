#!/usr/bin/env python3
import logging
import threading
import i3ipc

# -----------------------------
# CONFIG
# -----------------------------

GRID_COLS = 3
GRID_ROWS = 2
GAP = 12

# FORCE 1:1 WINDOWS ONLY
WINDOW_WIDTH = 1
WINDOW_HEIGHT = 1

# -----------------------------
# STATE
# -----------------------------

# workspace_name -> set((col,row))
occupied_slots = {}
window_slots = {}

# -----------------------------
# LOGGING
# -----------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)

sway = i3ipc.Connection()

# -----------------------------
# GRID HELPERS
# -----------------------------

def get_ws_rect(tree, ws_name):
    for ws in tree.workspaces():
        if ws.name == ws_name:
            return ws.rect
    return None


def grid_to_px(ws_rect, col, row):
    cell_w = ws_rect.width // GRID_COLS
    cell_h = ws_rect.height // GRID_ROWS

    x = ws_rect.x + col * cell_w
    y = ws_rect.y + row * cell_h
    w = cell_w
    h = cell_h

    return x, y, w, h

def find_free_slot(ws_name):
    used = occupied_slots.setdefault(ws_name, set())

    for y in range(GRID_ROWS):
        for x in range(GRID_COLS - 1, -1, -1):
            if (x, y) not in used:
                return x, y

    return None

# -----------------------------
# CORE SNAP
# -----------------------------

def snap_window():
    tree = sway.get_tree()
    focused = tree.find_focused()

    if not focused:
        return

    if focused.floating not in ["auto_on", "user_on"]:
        return

    ws = focused.workspace()
    if not ws:
        return

    ws_rect = get_ws_rect(tree, ws.name)
    if not ws_rect:
        return

    slot = find_free_slot(ws.name)
    if not slot:
        logging.info("No free slots.")
        return

    col, row = slot

    window_slots[focused.id] = (ws.name, col, row)
    occupied_slots[ws.name].add((col, row))

    x, y, w, h = grid_to_px(ws_rect, col, row)

    logging.info(f"Placing '{focused.name}' at ({col},{row})")

    sway.command(f'[con_id={focused.id}] floating enable')
    sway.command(f'[con_id={focused.id}] resize set {w} {h}')
    sway.command(f'[con_id={focused.id}] move absolute position {x} {y}')

def reflow_workspace(ws_name):
    tree = sway.get_tree()
    ws_rect = get_ws_rect(tree, ws_name)
    if not ws_rect:
        return

    used = occupied_slots.get(ws_name, set())
    if not used:
        return

    # rebuild ordered list (row-major, right-to-left consistent with your allocator)
    slots = sorted(list(used), key=lambda p: (p[1], -p[0]))

    new_used = set()
    new_window_slots = {}

    for i, (old_x, old_y) in enumerate(slots):
        new_x = GRID_COLS - 1 - (i % GRID_COLS)
        new_y = i // GRID_COLS

        new_used.add((new_x, new_y))

        # find window that used this slot
        for win_id, data in list(window_slots.items()):
            if data[1:] == (old_x, old_y):
                win = tree.find_by_id(win_id)
                if not win:
                    continue

                window_slots[win_id] = (ws_name, new_x, new_y)

                x, y, w, h = grid_to_px(ws_rect, new_x, new_y)

                sway.command(f'[con_id={win.id}] move absolute position {x} {y}')
                sway.command(f'[con_id={win.id}] resize set {w} {h}')

    occupied_slots[ws_name] = new_used

# -----------------------------
# EVENT
# -----------------------------

def on_window_new(sway, event):
    threading.Timer(0.05, snap_window).start()

def on_window_close(conn, event):
    win = event.container

    data = window_slots.pop(win.id, None)
    if not data:
        return

    ws_name, x, y = data

    used = occupied_slots.get(ws_name)
    if used:
        used.discard((x, y))

    reflow_workspace(ws_name)

# -----------------------------
# MAIN
# -----------------------------

def main():
    logging.info("Grid WM started (1:1 fixed grid).")

    sway.on("window::new", on_window_new)
    sway.on("window::close", on_window_close)

    sway.main()

if __name__ == "__main__":
    main()
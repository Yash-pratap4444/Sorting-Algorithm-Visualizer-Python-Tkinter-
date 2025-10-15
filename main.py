import tkinter as tk
import random

# layout constants
LEFT_START = 5        # left x of index 0
STEP_X = 10           # horizontal step between bar slots (also bar "width")
COUNT = 60            # number of bars
CANVAS_W = LEFT_START + STEP_X * COUNT + 5
CANVAS_H = 400
BOTTOM = CANVAS_H - 10

# globals used by sorts and animation
barList = []
lengthList = []
worker = None

# --- helpers ------------------------------------------------

def move_bar_to_index(bar_id, index):
    """Move rectangle 'bar_id' so its left x becomes LEFT_START + index*STEP_X."""
    coords = canvas.coords(bar_id)        # [left, top, right, bottom]
    current_left = coords[0]
    target_left = LEFT_START + index * STEP_X
    dx = target_left - current_left
    if dx != 0:
        canvas.move(bar_id, dx, 0)

def swap_adjacent(a_id, b_id):
    """Swap two adjacent bars visually (used by bubble/selection)."""
    a1, _, a2, _ = canvas.coords(a_id)
    b1, _, b2, _ = canvas.coords(b_id)
    canvas.move(a_id, b1 - a1, 0)
    canvas.move(b_id, a2 - b2, 0)

def disable_buttons():
    insert_btn.config(state='disabled')
    select_btn.config(state='disabled')
    bubble_btn.config(state='disabled')
    merge_btn.config(state='disabled')
    shuffle_btn.config(state='disabled')

def enable_buttons():
    insert_btn.config(state='normal')
    select_btn.config(state='normal')
    bubble_btn.config(state='normal')
    merge_btn.config(state='normal')
    shuffle_btn.config(state='normal')

# --- generator-based sorting algorithms --------------------

def _insertion_sort():
    global barList, lengthList
    n = len(lengthList)
    for i in range(1, n):
        cursor_val = lengthList[i]
        cursor_bar = barList[i]
        pos = i
        # shift larger elements right
        while pos > 0 and lengthList[pos - 1] > cursor_val:
            lengthList[pos] = lengthList[pos - 1]
            barList[pos] = barList[pos - 1]
            move_bar_to_index(barList[pos], pos)
            yield
            pos -= 1
        # place cursor
        lengthList[pos] = cursor_val
        barList[pos] = cursor_bar
        move_bar_to_index(cursor_bar, pos)
        yield

def _bubble_sort():
    global barList, lengthList
    n = len(lengthList)
    for i in range(n - 1):
        for j in range(n - i - 1):
            if lengthList[j] > lengthList[j + 1]:
                # swap logical arrays
                lengthList[j], lengthList[j + 1] = lengthList[j + 1], lengthList[j]
                barList[j], barList[j + 1] = barList[j + 1], barList[j]
                # swap visuals (adjacent)
                swap_adjacent(barList[j], barList[j + 1])
                yield

def _selection_sort():
    global barList, lengthList
    n = len(lengthList)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if lengthList[j] < lengthList[min_idx]:
                min_idx = j
        if min_idx != i:
            lengthList[i], lengthList[min_idx] = lengthList[min_idx], lengthList[i]
            barList[i], barList[min_idx] = barList[min_idx], barList[i]
            swap_adjacent(barList[i], barList[min_idx])  # visually swap the two (works because positions update)
            yield

# --- Merge sort (generator + correct placement of bars) -----

def _merge_sort(left, right):
    """Generator-based merge sort over inclusive indices [left..right]."""
    if left >= right:
        return
    mid = (left + right) // 2
    yield from _merge_sort(left, mid)
    yield from _merge_sort(mid + 1, right)
    yield from _merge(left, mid, right)

def _merge(left, mid, right):
    """Merge step: place bars into their target slots and yield to animate each placement."""
    global barList, lengthList

    left_vals = lengthList[left:mid + 1]
    right_vals = lengthList[mid + 1:right + 1]
    left_bars = barList[left:mid + 1]
    right_bars = barList[mid + 1:right + 1]

    i = j = 0
    k = left

    while i < len(left_vals) and j < len(right_vals):
        if left_vals[i] <= right_vals[j]:
            lengthList[k] = left_vals[i]
            barList[k] = left_bars[i]
            move_bar_to_index(barList[k], k)
            i += 1
        else:
            lengthList[k] = right_vals[j]
            barList[k] = right_bars[j]
            move_bar_to_index(barList[k], k)
            j += 1
        k += 1
        yield

    while i < len(left_vals):
        lengthList[k] = left_vals[i]
        barList[k] = left_bars[i]
        move_bar_to_index(barList[k], k)
        i += 1
        k += 1
        yield

    while j < len(right_vals):
        lengthList[k] = right_vals[j]
        barList[k] = right_bars[j]
        move_bar_to_index(barList[k], k)
        j += 1
        k += 1
        yield

# --- triggering functions ----------------------------------

def start_insertion():
    global worker
    if worker is None:
        worker = _insertion_sort()
        disable_buttons()
        animate()

def start_bubble():
    global worker
    if worker is None:
        worker = _bubble_sort()
        disable_buttons()
        animate()

def start_selection():
    global worker
    if worker is None:
        worker = _selection_sort()
        disable_buttons()
        animate()

def start_merge():
    global worker
    if worker is None and len(lengthList) > 0:
        worker = _merge_sort(0, len(lengthList) - 1)
        disable_buttons()
        animate()

# --- animation loop ----------------------------------------

def animate():
    global worker
    if worker is not None:
        try:
            next(worker)
            delay = max(1, 101 - speed_scale.get())   # speed slider: larger -> faster
            window.after(delay, animate)
        except StopIteration:
            worker = None
            enable_buttons()

# --- data generator ---------------------------------------

def generate():
    global barList, lengthList, worker
    if worker is not None:
        return  # don't shuffle while sorting is running
    canvas.delete('all')
    barList = []
    lengthList = []
    for i in range(COUNT):
        left = LEFT_START + i * STEP_X
        right = left + (STEP_X - 1)
        top = random.randint(5, CANVAS_H - 60)
        rect = canvas.create_rectangle(left, top, right, BOTTOM, fill='purple', outline='')
        barList.append(rect)
        lengthList.append(BOTTOM - top)

# --- GUI setup --------------------------------------------

window = tk.Tk()
window.title("Sorting Visualizer - Purple Bars")
window.geometry(f"{CANVAS_W+120}x{CANVAS_H+60}")

canvas = tk.Canvas(window, width=CANVAS_W, height=CANVAS_H, bg='white')
canvas.grid(column=0, row=0, columnspan=10, padx=6, pady=6)

# Buttons
shuffle_btn = tk.Button(window, text="Shuffle", width=10, command=generate)
insert_btn = tk.Button(window, text="Insertion Sort", width=12, command=start_insertion)
select_btn = tk.Button(window, text="Selection Sort", width=12, command=start_selection)
bubble_btn = tk.Button(window, text="Bubble Sort", width=10, command=start_bubble)
merge_btn = tk.Button(window, text="Merge Sort", width=10, command=start_merge)

shuffle_btn.grid(column=0, row=1, padx=4, pady=6)
insert_btn.grid(column=1, row=1, padx=4, pady=6)
select_btn.grid(column=2, row=1, padx=4, pady=6)
bubble_btn.grid(column=3, row=1, padx=4, pady=6)
merge_btn.grid(column=4, row=1, padx=4, pady=6)

# speed slider
speed_scale = tk.Scale(window, from_=1, to=100, orient='horizontal', label='Speed')
speed_scale.set(50)
speed_scale.grid(column=5, row=1, padx=8)

# initialize
generate()
window.mainloop()
#made by-YASH PRATAP SINGH

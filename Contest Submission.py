from collections import deque
import numpy as np
from PIL import Image
from pathlib import Path
import sys

# -------------------------------
# Handle input folder (robust)
# -------------------------------
if len(sys.argv) > 1:
    image_folder = Path(sys.argv[1])
else:
    image_folder = Path.cwd()

if not image_folder.exists():
    print(f"Error: folder does not exist -> {image_folder}")
    sys.exit(1)

print(f"Using image folder: {image_folder}")

# -------------------------------
# BFS setup
# -------------------------------
moves = [(-1,0),(1,0),(0,-1),(0,1)]

def bfs_seed(grid, start_row, start_col, visited, group, group_id, threshold=15):
    rows, cols = grid.shape
    seed_value = int(grid[start_row, start_col])

    q = deque()
    q.append((start_row, start_col))

    visited[start_row, start_col] = True
    group[start_row, start_col] = group_id

    while q:
        x, y = q.popleft()

        for dx, dy in moves:
            nx, ny = x + dx, y + dy

            if 0 <= nx < rows and 0 <= ny < cols:
                if not visited[nx, ny]:
                    if abs(seed_value - int(grid[nx, ny])) <= threshold:
                        visited[nx, ny] = True
                        group[nx, ny] = group_id
                        q.append((nx, ny))

# -------------------------------
# Output folder, Creates folder for images
# -------------------------------
output_folder = image_folder / "outputs"
output_folder.mkdir(exist_ok=True)

# -------------------------------
# MAIN LOOP
# -------------------------------
found_any = False

for file_path in image_folder.rglob("*.png"):
    found_any = True
    print(f"\nProcessing: {file_path.name}")

    img = Image.open(file_path).convert('L')
    grid = np.array(img, dtype=np.int16)

    visited = np.zeros(grid.shape, dtype=bool)
    group = np.zeros(grid.shape, dtype=int)

    group_id = 1

    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            if not visited[i, j]:
                bfs_seed(grid, i, j, visited, group, group_id)
                group_id += 1

    total_groups = group_id - 1
    print(f"Total groups: {total_groups}")

    # Save segmentation image (preserve IDs)
    save_path = output_folder / f"{file_path.stem}.png"
    Image.fromarray(group.astype(np.uint16)).save(save_path)
    print("Saved image to:", save_path)

    # Save summary
    summary_path = output_folder / f"{file_path.stem}_summary.txt"
    with open(summary_path, "w") as f:
        f.write(f"Total segments: {total_groups}\n")
    print("Saved summary to:", summary_path)

# -------------------------------
# Final check
# -------------------------------
if not found_any:
    print("No PNG images found in the specified folder.")
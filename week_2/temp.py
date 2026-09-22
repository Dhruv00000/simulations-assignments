from __future__ import annotations

from enum import IntEnum

import numpy as np
import pygame


class Material(IntEnum):
    EMPTY = 0
    SAND = 1
    WATER = 2
    WOOD = 3
    FIRE = 4
    SMOKE = 5

PALETTE = {
    Material.EMPTY: (0, 0, 0),
    Material.SAND: (194, 178, 128),
    Material.WATER: (52, 120, 235),
    Material.WOOD: (139, 69, 19),
    Material.FIRE: (230, 69, 0),
    Material.SMOKE: (128, 128, 128)
}
_COLORS = np.array([PALETTE[m] for m in Material], dtype=np.uint8)


_rng = np.random.default_rng()


class SandSim:

    def __init__(self, width: int, height: int, cell_size: int = 4, fps: int = 60) -> None:
        self.cell_size = cell_size
        self.fps = fps
        self.brush = Material.SAND
        self.brush_radius = 2
        self.resize_cells(width, height)

    def resize_cells(self, new_width: int, new_height: int) -> None:
        """Replace the grid with a fresh empty one of the given size."""
        self.width = int(new_width)
        self.height = int(new_height)
        self._types = np.zeros((self.height, self.width), dtype=np.uint8)
        self._ages = np.zeros((self.height, self.width), dtype=np.uint8)


    def paint_at(self, x: int, y: int) -> None:
        """Place the current brush material in a disc of cells at (x, y).

        ``x``/``y`` are in *grid* coordinates (screen pixels / cell_size).
        """
        r = self.brush_radius
        x_left, x_right = max(0, x - r), min(self.width, x + r + 1)
        y_top, y_bottom = max(0, y - r), min(self.height, y + r + 1)
        if x_right <= x_left or y_bottom <= y_top:
            return
        y_grid, x_grid = np.mgrid[y_top : y_bottom, x_left : x_right]
        disc: np.ndarray = ((x_grid - x) ** 2 + (y_grid - y) ** 2) <= r ** 2
        self._types[y_grid[disc], x_grid[disc]] = int(self.brush)
        self._ages[y_grid[disc], x_grid[disc]] = 0


    def update(self) -> None:
        """Advance the simulation by one tick."""
        grid_copy = self._types
        for row_index in range(self.height - 1, 0, -1):
            for column_index in np.random.permutation(range(self.width)):

                cell_content = self._types[row_index, column_index]

                if cell_content == 4 and self._ages[row_index, column_index] == 60:
                    grid_copy[row_index, column_index] = 0
                    continue
                if cell_content == 5 and self._ages[row_index, column_index] == 40:
                    grid_copy[row_index, column_index] = 0
                    continue

                if cell_content == 4 or cell_content == 5:
                    self._ages[row_index, column_index] += 1

                if cell_content == 0 or cell_content == 3:
                    continue

                is_not_bottommost_row: bool = row_index != self.height - 1
                is_not_rightmost_column: bool = column_index != self.width - 1
                is_not_leftmost_column: bool = column_index != 0
                if is_not_bottommost_row: lower_row = row_index + 1
                if is_not_leftmost_column: left_column = column_index - 1
                if is_not_rightmost_column: right_column = column_index + 1
                if is_not_leftmost_column and is_not_bottommost_row: cell_down_left = self._types[lower_row, left_column]
                if is_not_rightmost_column and is_not_bottommost_row: cell_down_right = self._types[lower_row, right_column]

                if (cell_content == 1 or cell_content == 2) and is_not_bottommost_row: # Moving sand and water downwards
                    if not self._types[lower_row, column_index]:
                        grid_copy[row_index, column_index], grid_copy[lower_row, column_index] = 0, cell_content
                        continue
                    if is_not_rightmost_column:
                        if is_not_leftmost_column and not (cell_down_left or cell_down_right):
                            grid_copy[row_index, column_index] = 0
                            if _rng.random() > 0.5:
                                grid_copy[lower_row, right_column] = cell_content
                            else:
                                grid_copy[lower_row, left_column] = cell_content
                            continue
                        if not cell_down_right:
                            grid_copy[row_index, column_index], grid_copy[lower_row, right_column] = 0, cell_content
                            continue
                    if is_not_leftmost_column and not cell_down_left:
                        grid_copy[row_index, column_index], grid_copy[lower_row, left_column] = 0, cell_content
                        continue
                
                is_not_topmost_row: bool = row_index != 0
                if is_not_topmost_row: upper_row = row_index - 1

                if cell_content == 4:

                    if is_not_topmost_row: # Extinguishing fire
                        if self._types[upper_row, column_index] == 2:
                            grid_copy[upper_row, column_index] = 0
                            self._ages[row_index, column_index] = 0
                            grid_copy[row_index, column_index] = 5
                            continue
                        if is_not_leftmost_column and self._types[upper_row, left_column] == 2:
                            grid_copy[upper_row, left_column] = 0
                            self._ages[row_index, column_index] = 0
                            grid_copy[row_index, column_index] = 5
                            continue
                        if is_not_rightmost_column and self._types[upper_row, right_column] == 2:
                            grid_copy[upper_row, right_column] = 0
                            self._ages[row_index, column_index] = 0
                            grid_copy[row_index, column_index] = 5
                            continue
                    if is_not_bottommost_row:
                        if self._types[lower_row, column_index] == 2:
                            grid_copy[lower_row, column_index] = 0
                            self._ages[row_index, column_index] = 0
                            grid_copy[row_index, column_index] = 5
                            continue
                        if is_not_leftmost_column and self._types[lower_row, left_column] == 2:
                            grid_copy[lower_row, left_column] = 0
                            self._ages[row_index, column_index] = 0
                            grid_copy[row_index, column_index] = 5
                            continue
                        if is_not_rightmost_column and self._types[lower_row, right_column] == 2:
                            grid_copy[lower_row, right_column] = 0
                            self._ages[row_index, column_index] = 0
                            grid_copy[row_index, column_index] = 5
                            continue
                    if is_not_leftmost_column and self._types[row_index, left_column] == 2:
                        grid_copy[row_index, left_column] = 0
                        self._ages[row_index, column_index] = 0
                        grid_copy[row_index, column_index] = 5
                        continue
                    if is_not_rightmost_column and self._types[row_index, right_column] == 2:
                        grid_copy[row_index, right_column] = 0
                        self._ages[row_index, column_index] = 0
                        grid_copy[row_index, column_index] = 5
                        continue

                    if is_not_topmost_row: # Burning wood
                        if self._types[upper_row, column_index] == 3 and _rng.random() > 0.8:
                            grid_copy[upper_row, column_index] = 4
                            self._ages[upper_row, column_index] = 0
                        if is_not_leftmost_column and self._types[upper_row, left_column] == 3 and _rng.random() > 0.8:
                            grid_copy[upper_row, left_column] = 4
                            self._ages[upper_row, left_column] = 0
                        if is_not_rightmost_column and self._types[upper_row, right_column] == 3 and _rng.random() > 0.8:
                            grid_copy[upper_row, right_column] = 4
                            self._ages[upper_row, right_column] = 0
                    if is_not_bottommost_row:
                        if self._types[lower_row, column_index] == 3 and _rng.random() > 0.8:
                            grid_copy[lower_row, column_index] = 4
                            self._ages[lower_row, column_index] = 0
                        if is_not_leftmost_column and self._types[lower_row, left_column] == 3 and _rng.random() > 0.8:
                            grid_copy[lower_row, left_column] = 4
                            self._ages[lower_row, left_column] = 0
                        if is_not_rightmost_column and self._types[lower_row, right_column] == 3 and _rng.random() > 0.8:
                            grid_copy[lower_row, right_column] = 4
                            self._ages[lower_row, right_column] = 0
                    if is_not_leftmost_column and self._types[row_index, left_column] == 3 and _rng.random() > 0.8:
                        grid_copy[row_index, left_column] = 4
                        self._ages[row_index, left_column] = 0
                    if is_not_rightmost_column and self._types[row_index, right_column] == 3 and _rng.random() > 0.8:
                        grid_copy[row_index, right_column] = 4
                        self._ages[row_index, right_column] = 0

                if (cell_content == 4 or cell_content == 5) and is_not_topmost_row and self._types[upper_row, column_index] == 0: # Moving smoke and fire upwards.
                    grid_copy[upper_row, column_index], grid_copy[row_index, column_index] = cell_content, 0
                    self._ages[row_index, column_index], self._ages[upper_row, column_index] = self._ages[upper_row, column_index], self._ages[row_index, column_index]
                    continue
                if cell_content == 4 or cell_content == 5 or cell_content == 2: # Moving smoke, water, and fire sideways
                    is_left_empty: bool = is_not_leftmost_column and self._types[row_index, left_column] == 0
                    is_right_empty: bool = is_not_rightmost_column and self._types[row_index, right_column] == 0
                    if is_left_empty and is_right_empty:
                        if _rng.random() > 0.5:
                            grid_copy[row_index, right_column], grid_copy[row_index, column_index] = cell_content, 0
                            self._ages[row_index, column_index], self._ages[row_index, right_column] = self._ages[row_index, right_column], self._ages[row_index, column_index]
                        else:
                            grid_copy[row_index, left_column], grid_copy[row_index, column_index] = cell_content, 0
                            self._ages[row_index, column_index], self._ages[row_index, left_column] = self._ages[row_index, left_column], self._ages[row_index, column_index]
                        continue
                    if is_not_leftmost_column and is_left_empty:
                        grid_copy[row_index, left_column], grid_copy[row_index, column_index] = cell_content, 0
                        self._ages[row_index, column_index], self._ages[row_index, left_column] = self._ages[row_index, left_column], self._ages[row_index, column_index]
                        continue
                    if is_not_rightmost_column and is_right_empty:
                        grid_copy[row_index, right_column], grid_copy[row_index, column_index] = cell_content, 0
                        self._ages[row_index, column_index], self._ages[row_index, right_column] = self._ages[row_index, right_column], self._ages[row_index, column_index]


    def surface(self) -> pygame.Surface:
        """Snapshot the grid as a pygame.Surface, scaled up by cell_size.

        _COLORS[grid] turns the cell-material grid into a grid of RGB
        pixels in one shot. pygame expects the axes as (WIDTH, HEIGHT),
        numpy stores them as (HEIGHT, WIDTH), so transpose swaps them back.
        """
        rgb = _COLORS[self._types]
        surf = pygame.surfarray.make_surface(
            np.ascontiguousarray(np.transpose(rgb, (1, 0, 2)))
        )
        if self.cell_size > 1:
            surf = pygame.transform.scale(
                surf, (self.width * self.cell_size, self.height * self.cell_size)
            )
        return surf


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
    pygame.display.set_caption("1-5 materials, [ ] brush, C clear")
    clock = pygame.time.Clock()

    sim = SandSim(800 // 4, 600 // 4)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                k = event.key
                if k == pygame.K_ESCAPE:
                    running = False
                elif k == pygame.K_1:
                    sim.brush = Material.SAND
                elif k == pygame.K_2:
                    sim.brush = Material.WATER
                elif k == pygame.K_3:
                    sim.brush = Material.WOOD
                elif k == pygame.K_4:
                    sim.brush = Material.FIRE
                elif k == pygame.K_5:
                    sim.brush = Material.SMOKE
                elif k in (pygame.K_0, pygame.K_e):
                    sim.brush = Material.EMPTY
                elif k == pygame.K_LEFTBRACKET:
                    sim.brush_radius = max(1, sim.brush_radius - 1)
                elif k == pygame.K_RIGHTBRACKET:
                    sim.brush_radius = min(40, sim.brush_radius + 1)
                elif k == pygame.K_c:
                    sim._types[:] = 0
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                sim.resize_cells(event.size[0] // sim.cell_size, event.size[1] // sim.cell_size)

        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            sim.paint_at(mx // sim.cell_size, my // sim.cell_size)

        sim.update()
        screen.blit(sim.surface(), (0, 0))

        pygame.display.flip()
        clock.tick(sim.fps)

    pygame.quit()


if __name__ == "__main__":
    main()
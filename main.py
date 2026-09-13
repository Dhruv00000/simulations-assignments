from random import randint as random_int
from random import uniform as random_uniform

import pygame

import cv2

from numpy import array, column_stack, cos, ndarray, pi, sin, triu_indices, rot90
from numpy import dot as dot_product
from numpy.linalg import norm


# Simulation configuration
window_width: int = 600
window_height: int = 400
origin: ndarray = array([window_width / 2, window_height / 2], dtype=float)
bowl_radius: float = 180
framerate: int = 60

ball_count: int = 8

radius_range: tuple[int, int] = (6, 10)
initial_speed_range: tuple[float, float] = (100.0, 200.0)
mass_range: tuple[float, float] = (0.5, 2.0)

gravitational_acceleration: float = 500.0
restitution_with_wall: float = 1.0
restitution_with_balls: float = 1.0


radii: list[int] = []
positions: list[ndarray] = []
velocities: list[ndarray] = []
colours: list[tuple[int, int, int]] = []
masses: list[float] = []

for ball_index in range(ball_count):

    radii.append(random_uniform(radius_range[0], radius_range[1]))

    ball_spawn_angle: float = random_uniform(0, 2 * pi)
    positions.append(origin +
        random_uniform(0, (bowl_radius - radii[ball_index]) * 0.9) * array([ # 0.9 here avoids spawning a ball close to the boundary
            cos(ball_spawn_angle),
            sin(ball_spawn_angle)
    ], dtype=float))

    velocity_angle: float = random_uniform(0, 2 * pi)
    velocities.append(random_uniform(initial_speed_range[0], initial_speed_range[1]) * array([
        cos(velocity_angle),
        sin(velocity_angle)
    ]))

    colours.append((random_int(50, 255), random_int(50, 255), random_int(50, 255))) # An attempt at making balls easier to track (by giving them all different colours). 50 is an endpoint of the range of possible r/g/b values here instead of 0 in order to ensure that the balls are bright enough to be visible on the dark background of the simulation.

    masses.append(random_uniform(mass_range[0], mass_range[1]))


pygame.init()

# screen = pygame.display.set_mode((window_width, window_height))
screen = pygame.display.set_mode((window_width, window_height + 320))
pygame.display.set_caption("Collision Simulation")
video_capture = cv2.VideoCapture("video.mp4")

clock = pygame.time.Clock()

running: bool = True


while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False

    dt: float = clock.tick(framerate) / 1000.0


    for ball_index in range(ball_count):

        velocities[ball_index][1] += gravitational_acceleration * dt
        positions[ball_index] += velocities[ball_index] * dt
        ball_position_vector: ndarray = positions[ball_index] - origin
        distance_from_center: float = float(norm(ball_position_vector))
        max_allowed_distance: float = bowl_radius - radii[ball_index]

        if distance_from_center >= max_allowed_distance:

            radial_unit_vector = ball_position_vector / distance_from_center
            positions[ball_index] = origin + (radial_unit_vector * max_allowed_distance)
            velocity_radial = float(dot_product(velocities[ball_index], radial_unit_vector))

            if velocity_radial > 0: # If a ball has already collided, but is still intersecting with the walls, it is left alone, instead of getting vibrated at the wall forever.
                velocities[ball_index] -= (1 + restitution_with_wall) * (velocity_radial * radial_unit_vector) # V = V_t + V_r => V_t + (-V_r * e) = V - V_r * (1 + e) (basically, I am flipping (and scaling) the radial component of the velocity vector here)


    for ball_pair in column_stack(triu_indices(ball_count, k=1)):

        index_of_first_ball: int = ball_pair[0]
        index_of_second_ball: int = ball_pair[1]
        normal_vector: ndarray = positions[index_of_second_ball] - positions[index_of_first_ball]
        sum_of_radii: float = radii[index_of_second_ball] + radii[index_of_first_ball]
        distance_between_centres: float = norm(normal_vector)

        if distance_between_centres <= sum_of_radii:

            mass_1: float = masses[index_of_first_ball]
            mass_2: float = masses[index_of_second_ball]
            normal_unit_vector: ndarray = normal_vector / distance_between_centres
            speed_of_approach: float = float(dot_product(velocities[index_of_second_ball], normal_unit_vector) - dot_product(velocities[index_of_first_ball], normal_unit_vector))
            total_mass: float = mass_1 + mass_2
            offset_factor: ndarray = (normal_unit_vector * (sum_of_radii - distance_between_centres)) / total_mass
            
            positions[index_of_first_ball] += offset_factor * mass_2
            positions[index_of_second_ball] -= offset_factor * mass_1
            
            if speed_of_approach < 0: # If the balls are already separating, then applying the collision code to them would make them approach each other again.
                impulse: ndarray = (-(1 + restitution_with_balls) * speed_of_approach * (mass_1 * mass_2 / total_mass)) * normal_unit_vector
                velocities[index_of_first_ball] -= impulse / mass_1
                velocities[index_of_second_ball] += impulse / mass_2

    screen.fill((20, 20, 25))

    pygame.draw.circle(
        surface = screen,
        color = (180, 180, 180),
        center = origin.astype(int),
        radius = bowl_radius,
        width = 3
    )

    for ball_index in range(ball_count):
        pygame.draw.circle(
            surface = screen,
            color = colours[ball_index],
            center = positions[ball_index].astype(int),
            radius = radii[ball_index]
        )
    
    ret, frame = video_capture.read()
    if not ret:
        video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = video_capture.read()

    if ret:
        frame = cv2.resize(frame, (window_width, 320))
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_surface = pygame.surfarray.make_surface(rot90(frame_rgb))
        screen.blit(frame_surface, (0, window_height))

    pygame.display.flip()

pygame.quit()

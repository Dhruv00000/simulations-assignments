# Assignment brief

Answer to question 1: The collision detection fails because in one frame, the ball is inside the bowl, and in the next frame, it is outside. It never intersects the boundary of the bowl, which is what the collision logic actually checks. Both, ∆t, and |v| determine whether or not this bug occurs. If ∆t is not small enough, or if |v| is very large, the bug will occur.

To solve this, we can change the collision check to be something like `if norm(ball_centre - bowl_centre) >= bowl_radius - ball_radius`

Answer to question 2: The extra energy is coming from the errors in our estimation of integration, which get accumulated over time.
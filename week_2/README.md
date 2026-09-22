# Assignment brief

Answer to question 1: If G^' started as a grid of zeroes, then a cell that doesnt get updated during the current iteration would disappear as soon as the current iteration's update process ends.

Answer to question 2: If the order in which columns are visited is not randomly generated every time, and is instead left-to-right, then that would create a bias in the simulation that would skew sand piles to the right. (sand cells in the columns on the left would fall first, occupying lower positions, and hence cells in columns on the right would have nowhere to fall (they would occupy higher positions).)

Answers to other questions in the assignment PDF:
- Yes, sand did pile up how I expected it to.
- No, water did not pool flat. This is because our physics logic for water causes the bottom-most row of water cells to move left and right randomly, having no effective motion. In order to make water pool flat, we would have to make it prefer spreading out, instead of assigning a 50-50 probability to left and right movement each.
- For bonus materials, I made this scene: (screenshot attached below); and what surprised me was the speed at which fire and smoke rose up.
![Example scene](./example_screenshot.png)
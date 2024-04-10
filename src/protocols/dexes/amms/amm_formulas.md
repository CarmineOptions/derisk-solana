# Formulas used through out this folder


## Some CF-AMM formulas: 
$$ x_1 y_1 = k = x_2 y_2 $$
$$ p_1 = \frac{y_1}{x_1}  $$
$$ p_2 = \frac{y_2}{x_2} $$
$$y_2 = p_2x_2$$
$$x_1y_1 = k = x_2 (p_2 x_2) = p_2x_2^2$$
$$x_2 = \sqrt{\frac{x_1y_1}{p_2}}$$

#### Deltas of tokens:
$$\Delta x = x_2 - x_1 = \sqrt{\frac{x_1y_1}{p_2}} - x_1$$
$$\Delta y = y_2 - y_1 = \frac{k}{x_2} - y_1 = \frac{k}{x_1 + \Delta x} - y_1


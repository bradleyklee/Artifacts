from artifact24.geometry import VERTICES, COMMON_IMAGE, polynomial_map
from artifact24.plots import build_interactive_figure
import numpy as np

mapped = polynomial_map(VERTICES)
assert np.max(np.linalg.norm(mapped - COMMON_IMAGE, axis=1)) < 1e-10
fig = build_interactive_figure(
    red_count=8,
    auxiliary_count=4,
    samples=240,
    show_background=False,
)
assert len(fig.data) > 0
print("PASS")

"""Example: build a figure document in code and export it, headlessly.

Run with:

    python -m matplotlib_designer.examples.example_basic

Demonstrates the model layer and export backends without launching the GUI:
useful for scripted report generation or for verifying an install.
"""
from __future__ import annotations

from pathlib import Path

from matplotlib_designer.commands.undo import UndoManager
from matplotlib_designer.designer.canvas import SceneCanvas
from matplotlib_designer.export.image_export import export_image
from matplotlib_designer.export.script_export import export_script
from matplotlib_designer.models.annotation_model import AnnotationModel
from matplotlib_designer.models.axes_model import AxesModel
from matplotlib_designer.models.figure_model import FigureModel
from matplotlib_designer.models.plot_model import PlotModel
from matplotlib_designer.models.shape_model import ShapeModel
from matplotlib_designer.serialization.project_serializer import save_project


def build_demo_figure() -> FigureModel:
    """Construct a small demo figure: a sine wave with an annotation and a box."""
    figure = FigureModel(name="Demo Figure", width_in=8, height_in=5)
    axes = AxesModel(name="Axes 1")
    axes.title.content = "Example Signal"
    axes.xlabel.content = "Time (s)"
    axes.ylabel.content = "Amplitude"
    axes.show_grid = True
    axes.show_legend = True

    import math

    xs = [i / 20 for i in range(200)]
    ys = [math.sin(2 * math.pi * x) for x in xs]
    axes.plots.append(PlotModel(name="Sine", kind="line", x=xs, y=ys, label="sin(x)", color="#1f77b4"))

    axes.shapes.append(ShapeModel(name="Highlight", kind="rectangle", x=0.55, y=0.55, width=0.15, height=0.15,
                                   face_color="#ffcc00", edge_color="#886600", opacity=0.4))
    axes.annotations.append(AnnotationModel(name="Peak", text="Peak here", x=0.25, y=0.9, xtext=0.4, ytext=0.95))

    figure.axes.append(axes)
    return figure


def main() -> None:
    """Build the demo figure and export it to the current directory."""
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    # SceneCanvas is a QWidget (it embeds a live FigureCanvasQTAgg), so a
    # QApplication must exist before it can be constructed, even for this
    # headless, GUI-less export example.
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])

    figure = build_demo_figure()
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    save_project(figure, output_dir / "demo_project.json")
    export_script(figure, output_dir / "demo_generated.py")

    canvas = SceneCanvas(figure, UndoManager())
    export_image(canvas, output_dir / "demo_figure.png")

    print(f"Wrote demo_project.json, demo_generated.py and demo_figure.png to {output_dir}")


if __name__ == "__main__":
    main()

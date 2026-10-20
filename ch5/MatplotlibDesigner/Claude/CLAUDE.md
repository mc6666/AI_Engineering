# SKILLS.md

# Project
Matplotlib Designer V2

## Goal

Develop a professional desktop application for designing Matplotlib figures visually.

The application should resemble a lightweight version of:

- MATLAB Figure Editor
- OriginLab Graph Editor
- PowerPoint (for annotations)
- Adobe Illustrator (object editing)

while generating native Matplotlib figures.

The entire project shall be written in Python.

---

# Technology Stack

Python 3.12+

GUI
- PySide6

Plot Engine
- matplotlib

Numerical
- numpy
- pandas

Optional
- scipy
- pillow

Serialization
- json

Project Build
- pyproject.toml

Testing
- pytest

Documentation
- mkdocs

---

# Project Architecture

matplotlib_designer/

```
app.py
main.py

designer/

    main_window.py
    canvas.py
    toolbar.py
    ribbon.py
    property_panel.py
    object_tree.py
    statusbar.py

models/

    figure_model.py
    axes_model.py
    text_model.py
    shape_model.py
    annotation_model.py

commands/

    command.py
    undo.py
    redo.py
    add_text.py
    add_arrow.py
    delete.py
    move.py
    resize.py

tools/

    select_tool.py
    text_tool.py
    arrow_tool.py
    annotation_tool.py
    rectangle_tool.py
    ellipse_tool.py
    line_tool.py

widgets/

dialogs/

serialization/

export/

resources/

tests/

examples/
```

---

# GUI Requirements

Window Layout

```
------------------------------------------------------
Menu

Toolbar

------------------------------------------------------

Object Tree

Matplotlib Canvas

Property Inspector

------------------------------------------------------

Status Bar
```

Dock widgets shall be movable.

---

# Menu

File

Edit

View

Insert

Plot

Layout

Window

Help

---

# Toolbar

Selection

Move

Zoom

Pan

Title

Subtitle

X Label

Y Label

Tick Editor

Text

Annotation

Arrow

Rectangle

Ellipse

Line

Legend

Grid

Image

Line Plot

Scatter Plot

Bar Plot

Histogram

Heatmap

Multiple Subplots

Export

---

# Canvas

Must support

Selection

Dragging

Resize Handles

Object Highlight

Rubber Band Selection

Zoom

Pan

Snap To Grid

Guidelines

---

# Object Types

Figure

Axes

Title

Subtitle

X Label

Y Label

Tick Labels

Legend

Annotation

Arrow

Rectangle

Ellipse

Circle

Text

Line

Scatter

Bar

Heatmap

Image

---

# Property Panel

Support editing

Text

Font

Font Size

Bold

Italic

Underline

Color

Background

Alignment

Rotation

Visibility

Opacity

Z-order

Position

Width

Height

Line Style

Line Width

Marker

Marker Size

Arrow Style

Padding

Margins

---

# Object Tree

Display

Figure

Axes

Plots

Text

Shapes

Annotations

Support

Rename

Delete

Duplicate

Drag hierarchy

Hide

Lock

---

# Figure Features

Support

Single Figure

Multiple Axes

GridSpec

TwinX

TwinY

Polar

3D

Inset Axes

Shared Axes

Tight Layout

Constrained Layout

---

# Plot Types

Line

Scatter

Bar

Horizontal Bar

Histogram

Pie

Box Plot

Violin

Stem

Step

Heatmap

Contour

Image

Error Bar

Stack Plot

Area Plot

---

# Text Editing

Double click edits text

Live preview

Unicode

LaTeX

MathText

Auto wrapping

Alignment

---

# Annotation

Support

Arrow

Text

Rounded Box

Rectangle Box

Callout

Leader Line

Offset

---

# Shapes

Rectangle

Ellipse

Circle

Polygon

Line

Bezier

Freehand

---

# Selection

Mouse Click

Ctrl Click

Shift Click

Drag Selection

Group Selection

Ungroup

Align

Distribute

---

# Undo Redo

Command Pattern

Every action must inherit

```
Command
```

Interface

```
execute()

undo()

redo()
```

---

# Serialization

Project Format

JSON

Must save

Figure

Axes

Plots

Shapes

Annotations

Properties

Layers

Templates

---

# Export

PNG

PDF

SVG

EPS

JPG

TIFF

Python Script

JSON

Pickle Figure

---

# Python Export

Generated code must reproduce the figure exactly.

---

# Plugin System

Plugins stored under

plugins/

Each plugin registers

```
Plot

Toolbar Action

Menu Action

Dock Widget
```

---

# Themes

Light

Dark

Scientific

Nature

IEEE

Presentation

---

# Keyboard Shortcuts

Ctrl+N

Ctrl+O

Ctrl+S

Ctrl+Z

Ctrl+Y

Delete

Ctrl+C

Ctrl+V

Ctrl+D

Space = Pan

---

# Coding Standards

PEP8

Type hints

Dataclasses

No global state

Dependency injection

MVC architecture

No duplicated code

Functions under 50 lines where practical

Classes under 300 lines where practical

Document every public method.

---

# Testing

pytest

Minimum coverage

80%

Test

Canvas

Serialization

Commands

Widgets

Toolbar

Property Editor

Export

---

# Documentation

Every module requires

Module Docstring

Every class requires

Class Docstring

Every public function requires

Google Style Docstring

---

# Performance

Support figures containing

50 axes

1000 annotations

10000 plotted points

without UI freezing.

---

# Milestones

V2.0

Project Skeleton

V2.1

Canvas

V2.2

Selection

V2.3

Text Tools

V2.4

Shapes

V2.5

Annotations

V2.6

Property Inspector

V2.7

Multiple Subplots

V2.8

Undo/Redo

V2.9

Serialization

V3.0

Plugin System

V3.1

Themes

V3.2

Performance Optimization

---

# Acceptance Criteria

The application shall

✓ Start successfully

✓ Open and save projects

✓ Export all supported formats

✓ Edit all text visually

✓ Move objects with mouse

✓ Resize objects interactively

✓ Support unlimited undo/redo

✓ Generate reproducible Python code

✓ Support multiple subplot layouts

✓ Be extensible through plugins

✓ Be fully documented

✓ Pass all tests

End of SKILLS.md
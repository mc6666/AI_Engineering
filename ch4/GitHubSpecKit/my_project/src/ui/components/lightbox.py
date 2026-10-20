from nicegui import ui


def lightbox(photo_url: str, alt_text: str) -> None:
    """Show an enlarged photo overlay with backdrop click and Escape-key dismissal."""
    with ui.dialog().props("maximized") as dialog:
        with ui.element("div").classes(
            "fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center"
        ).on("click", dialog.close):
            ui.image(photo_url).classes(
                "max-w-[90vw] max-h-[90vh] object-contain"
            ).props(f'alt="{alt_text}"').on(
                "click.stop", lambda: None  # Prevent click-through to backdrop
            )
            ui.button(icon="close", on_click=dialog.close).classes(
                "absolute top-4 right-4 text-white z-10"
            ).props("flat round")
        ui.keyboard(on_key=lambda e: dialog.close() if e.key == "Escape" else None)
    dialog.open()

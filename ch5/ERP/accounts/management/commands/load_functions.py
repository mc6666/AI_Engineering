import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from accounts.models import Function


class Command(BaseCommand):
    help = "Load leaf nodes from static/data/frontend_menu.json into accounts_function"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            default=str(Path(settings.BASE_DIR) / "static" / "data" / "frontend_menu.json"),
        )

    def handle(self, *args, **options):
        with open(options["file"], encoding="utf-8") as f:
            menu = json.load(f)

        Function.objects.all().delete()
        created, updated, skipped = 0, 0, 0

        def walk(nodes):
            nonlocal created, updated, skipped
            for node in nodes:
                children = node.get("children") or []
                if children:
                    walk(children)
                    continue
                code = node.get("function_code")
                url_name = node.get("url_name")
                title = node.get("title")
                if not code:
                    skipped += 1
                    continue
                # obj, was_created = Function.objects.get_or_create(
                # obj, was_created = Function.objects.create(
                    # code=code,
                    # name=title, description=url_name,
                # )
                # if was_created:
                    # created += 1
                # else:
                    # updated += 1
                obj = Function.objects.create(
                    code=code,
                    name=title, description=url_name,
                )
                created += 1

        walk(menu)
        self.stdout.write(
            self.style.SUCCESS(
                f"Done. created={created}, already_existed={updated}, skipped_no_code={skipped}"
            )
        )

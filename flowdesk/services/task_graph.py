from collections import deque

from django.db.models import QuerySet
from django.urls import reverse

from flowdesk.models import Task


def build_task_graph(task: Task, queryset: QuerySet, workspace_pk: int, board_pk: int) -> dict:
    visited = set()
    queue = deque([task])
    related_ids = set([task.pk])

    while queue:
        current = queue.popleft()
        if current.pk in visited:
            continue
        visited.add(current.pk)

        for blocker in current.blocking_tasks.all():
            if blocker.pk not in related_ids:
                related_ids.add(blocker.pk)
                queue.append(blocker)

        for blocked in current.tasks.all():
            if blocked.pk not in related_ids:
                related_ids.add(blocked.pk)
                queue.append(blocked)

    tasks = queryset.filter(pk__in=related_ids)

    nodes = []
    edges = []

    for t in tasks:
        if t.pk == task.pk:
            group = "current"
        elif t in task.blocking_tasks.all():
            group = "blockers"
        elif t in task.tasks.all():
            group = "blocked"
        else:
            group = "related"

        nodes.append({
            "id": t.pk,
            "label": t.title,
            "title": f"from list: {t.list.name}",
            "group": group,
            "url": reverse("flowdesk:task-detail", args=(workspace_pk, board_pk, t.list.pk, t.pk, )) 
        })

        for blocker in t.blocking_tasks.all():
            if blocker.pk in related_ids:
                edges.append({
                    "from": blocker.pk,
                    "to": t.pk,
                    "title": f"{blocker.title} → {t.title}"
                })

    return {"nodes": nodes, "edges": edges}

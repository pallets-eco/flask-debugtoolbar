from __future__ import annotations

import collections
import functools
import os.path
import sys
import threading
import time
import typing as t
import zlib
from dataclasses import dataclass
from dataclasses import field
from types import FrameType

from flask import current_app
from flask import Flask
from jinja2 import Environment
from werkzeug import Request

from . import DebugPanel

_GRAPH_WIDTH = 1200.0
_FRAME_HEIGHT = 20


@dataclass(frozen=True)
class FlamegraphFrame:
    """A stable description of a Python frame in a sampled stack."""

    name: str
    module: str
    filename: str
    lineno: int

    @property
    def label(self) -> str:
        return f"{self.name} ({self.module})"

    @property
    def location(self) -> str:
        return f"{self.filename}:{self.lineno}"


@dataclass
class _FlamegraphNode:
    frame: FlamegraphFrame | None
    samples: int = 0
    children: dict[FlamegraphFrame, _FlamegraphNode] = field(default_factory=dict)


@dataclass(frozen=True)
class FlamegraphBlock:
    """A positioned block ready to be rendered in the flamegraph SVG."""

    name: str
    location: str
    samples: int
    percentage: float
    x: float
    y: int
    width: float
    color: str


class FlamegraphSampler:
    """Periodically sample the Python stack of one request thread."""

    def __init__(self, interval: float = 0.001) -> None:
        self.interval = interval
        self.stack_counts: collections.Counter[tuple[FlamegraphFrame, ...]] = (
            collections.Counter()
        )
        self.duration: float = 0.0
        self._started_at = 0.0
        self._last_sample_at = 0.0
        self._root_frame: FrameType | None = None
        self._target_thread_id: int | None = None
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    @property
    def sample_count(self) -> int:
        return sum(self.stack_counts.values())

    def start(self, root_frame: FrameType | None = None) -> None:
        self._target_thread_id = threading.get_ident()
        self._started_at = time.perf_counter()
        self._last_sample_at = self._started_at
        self._root_frame = root_frame
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._sample,
            name="flask-debugtoolbar-flamegraph",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        self.duration = time.perf_counter() - self._started_at
        self._stop_event.set()

        if self._thread is not None:
            self._thread.join()

        self._root_frame = None

    def _sample(self) -> None:
        while not self._stop_event.wait(self.interval):
            target_thread_id = self._target_thread_id

            if target_thread_id is None:
                continue

            frame = sys._current_frames().get(target_thread_id)

            if frame is None:
                continue

            stack: list[FlamegraphFrame] = []
            root_frame = self._root_frame

            while frame is not None and frame is not root_frame:
                code = frame.f_code
                stack.append(
                    FlamegraphFrame(
                        name=code.co_name,
                        module=str(frame.f_globals.get("__name__", "<unknown>")),
                        filename=code.co_filename,
                        lineno=code.co_firstlineno,
                    )
                )
                frame = frame.f_back

            if not stack or (root_frame is not None and frame is None):
                continue

            sampled_at = time.perf_counter()
            sample_weight = max(
                1, round((sampled_at - self._last_sample_at) / self.interval)
            )
            self._last_sample_at = sampled_at
            self.stack_counts[tuple(reversed(stack))] += sample_weight


def _frame_color(frame: FlamegraphFrame | None) -> str:
    if frame is None:
        return "hsl(8 75% 56%)"

    color_key = zlib.crc32(frame.label.encode())
    hue = 8 + color_key % 38
    lightness = 58 + (color_key // 38) % 14
    return f"hsl({hue} 82% {lightness}%)"


def _short_location(frame: FlamegraphFrame) -> str:
    try:
        filename = os.path.relpath(frame.filename, current_app.root_path)
    except ValueError:
        filename = frame.filename

    if filename.startswith(os.path.pardir):
        filename = frame.filename

    return f"{filename}:{frame.lineno}"


def build_flamegraph(
    stack_counts: t.Mapping[tuple[FlamegraphFrame, ...], int],
) -> tuple[list[FlamegraphBlock], int]:
    """Merge sampled stacks and lay them out as flamegraph blocks."""
    root = _FlamegraphNode(frame=None)

    for stack, samples in stack_counts.items():
        if samples <= 0:
            continue

        node = root
        node.samples += samples

        for frame in stack:
            node = node.children.setdefault(frame, _FlamegraphNode(frame=frame))
            node.samples += samples

    if not root.samples:
        return [], 0

    def node_depth(node: _FlamegraphNode) -> int:
        if not node.children:
            return 0

        return 1 + max(node_depth(child) for child in node.children.values())

    max_depth = node_depth(root)
    blocks: list[FlamegraphBlock] = []

    def add_blocks(node: _FlamegraphNode, depth: int, x: float) -> None:
        width = node.samples / root.samples * _GRAPH_WIDTH
        frame = node.frame
        blocks.append(
            FlamegraphBlock(
                name=frame.label if frame is not None else "all samples",
                location=_short_location(frame) if frame is not None else "",
                samples=node.samples,
                percentage=node.samples / root.samples * 100,
                x=x,
                y=(max_depth - depth) * _FRAME_HEIGHT,
                width=width,
                color=_frame_color(frame),
            )
        )

        child_x = x

        for child in sorted(
            node.children.values(),
            key=lambda item: (
                item.frame.label if item.frame is not None else "",
                item.frame.location if item.frame is not None else "",
            ),
        ):
            add_blocks(child, depth + 1, child_x)
            child_x += child.samples / root.samples * _GRAPH_WIDTH

    add_blocks(root, 0, 0.0)
    return blocks, (max_depth + 1) * _FRAME_HEIGHT


class FlamegraphDebugPanel(DebugPanel):
    """Panel that displays a sampled flamegraph for the current request."""

    name = "Flamegraph"
    user_activate = True
    is_active: bool = False

    def __init__(
        self, jinja_env: Environment, context: dict[str, t.Any] | None = None
    ) -> None:
        super().__init__(jinja_env, context=context)
        self.sampler: FlamegraphSampler | None = None
        self.interval: float = float(current_app.config["DEBUG_TB_FLAMEGRAPH_INTERVAL"])

        if current_app.config["DEBUG_TB_FLAMEGRAPH_ENABLED"]:
            self.is_active = True

    @classmethod
    def init_app(cls, app: Flask) -> None:
        interval = app.config["DEBUG_TB_FLAMEGRAPH_INTERVAL"]

        if isinstance(interval, bool) or not isinstance(interval, (int, float)):
            raise ValueError("DEBUG_TB_FLAMEGRAPH_INTERVAL must be a number")

        if interval <= 0:
            raise ValueError("DEBUG_TB_FLAMEGRAPH_INTERVAL must be greater than zero")

    @property
    def has_content(self) -> bool:  # type: ignore[override]
        return self.sampler is not None

    def process_view(
        self,
        request: Request,
        view_func: t.Callable[..., t.Any],
        view_kwargs: dict[str, t.Any],
    ) -> t.Callable[..., t.Any] | None:
        if not self.is_active:
            return None

        @functools.wraps(view_func)
        def wrapped_view(*args: t.Any, **kwargs: t.Any) -> t.Any:
            self.sampler = FlamegraphSampler(self.interval)
            self.sampler.start(root_frame=sys._getframe())

            try:
                return view_func(*args, **kwargs)
            finally:
                self.sampler.stop()

        return wrapped_view

    def nav_title(self) -> str:
        return "Flamegraph"

    def nav_subtitle(self) -> str:
        if not self.is_active:
            return "inactive"

        if self.sampler is None:
            return "active"

        return f"{self.sampler.sample_count} samples"

    def title(self) -> str:
        if not self.is_active:
            return "Flamegraph not active"

        if self.sampler is None:
            return "Flamegraph"

        return f"View: {self.sampler.duration * 1000:.2f}ms"

    def url(self) -> str:
        return ""

    def content(self) -> str:
        if self.sampler is None:
            return "The flamegraph is not activated. Activate it and reload the page."

        blocks, graph_height = build_flamegraph(self.sampler.stack_counts)
        return self.render(
            "panels/flamegraph.html",
            {
                "blocks": blocks,
                "duration": self.sampler.duration,
                "graph_height": graph_height,
                "graph_width": _GRAPH_WIDTH,
                "interval": self.interval,
                "sample_count": self.sampler.sample_count,
            },
        )

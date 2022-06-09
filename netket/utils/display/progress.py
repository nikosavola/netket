# Copyright 2022 The NetKet Authors - All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import timedelta

import rich
from rich.console import Console
from rich.markdown import Text
from rich.style import Style
from rich.color import Color

from rich.progress import ProgressColumn, BarColumn

import colorsys
from .repr import color_good_bad, color_curve


class TimerColumn(ProgressColumn):
    """Renders estimated time remaining."""

    # Only refresh twice a second to prevent jitter
    max_refresh = 0.5

    def render(self, task: "Task") -> Text:
        """Show time elapsed and remaining."""
        elapsed = task.finished_time if task.finished else task.elapsed
        remaining = task.time_remaining

        if elapsed is None:
            elapsed = 0
        delta = timedelta(seconds=int(elapsed))

        if remaining is None:
            remaining_delta = "?"
        else:
            remaining_delta = timedelta(seconds=int(remaining))

        elapsed_txt = Text(str(delta), style="progress.elapsed")
        reimaining_txt = Text(str(remaining_delta), style="progress.remaining")

        if not task.finished:
            elapsed_txt.append(">")
            elapsed_txt.append(reimaining_txt)

        return elapsed_txt


class ProgressSpeedColumn(ProgressColumn):
    """Renders human readable transfer speed."""

    def render(self, task: "Task") -> Text:
        """Show data transfer speed."""
        speed = task.finished_speed or task.speed
        if speed is None:
            return Text("?", style="progress.data.speed")

        if speed >= 10:
            return Text(f"{speed:>3.1f}it/s", style="progress.data.speed")
        speedm1 = speed ** -1
        return Text(f"{speedm1:>3.1f}s/it", style="progress.data.speed")


class StatsDisplayColumn(ProgressColumn):
    """Renders human readable transfer speed."""

    def render(self, task: "Task") -> Text:
        """Show data transfer speed."""
        loss_name = task.fields.get("loss_name", "")
        loss_stats = task.fields.get("loss_stats", "")

        if loss_stats is not None:
            res = Text(f"{loss_name} = ")
            if hasattr(loss_stats, "__rich__"):
                loss_data_text = loss_stats.__rich__()
            else:
                loss_data_text = loss_stats.__repr__()
            res.append(loss_data_text)
            return res
        return Text()


class ColorBarColumn(BarColumn):
    """Colored progress bar.
    
    Gets coloring by the `color_by` argument which fetches an attribute from task returned by Rich.
    """

    def __init__(self, *args, color_by='percentage', **kwargs) -> None:
        self.color_by = color_by
        # self.bar_width = None
        super().__init__(*args, **kwargs)

    def render(self, task: "Task") -> Text:
        r"""Gets a progress bar colored using :math:`\hat{R}` for a task."""
        self.complete_style = Style(
            color=color_good_bad(color_curve(getattr(task, self.color_by)))
        )
        return super().render(task)
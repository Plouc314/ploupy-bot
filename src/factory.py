from __future__ import annotations

from functools import wraps
import random
from typing import Callable

import ploupy as pp

from . import utils


class FactoryMixin:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.ongoing_factory_actions: list[str] = []

        self._wrap_action("build_expansion_factory")
        self._wrap_action("build_economy_factory")

    def _wrap_action(self, name: str):
        func = getattr(self, name)

        @wraps(func)
        async def inner(*args, **kwargs):
            self.ongoing_factory_actions.append(func.__name__)
            await func(*args, **kwargs)
            if func.__name__ in self.ongoing_factory_actions:
                self.ongoing_factory_actions.remove(func.__name__)

        setattr(self, name, inner)

    def _get_build_expansion_factory_target(
        self: pp.Behaviour | "FactoryMixin",
    ) -> pp.Tile:
        tiles = self.map.get_unoccupied_tiles()
        n_center = len(tiles) // 25
        centers = pp.geometry.centers((tile.coord for tile in tiles), n_center)

        idx = random.randint(0, n_center - 1)
        return self.map.get_tile(centers[idx])

    async def build_expansion_factory(
        self: pp.Behaviour | "FactoryMixin",
        target: pp.Tile | None = None,
        probes: list[pp.Probe] | None = None,
    ) -> None:

        if target is None:
            target = self._get_build_expansion_factory_target()

        if probes is None:
            probes = utils.get_closest_probes(self.player, target.coord, n_probes=7)

        await self.move_probes(probes, target.coord)

        await self.place_order(
            pp.BuildFactoryOrder(
                target,
                name="build_expansion_factory",
            ),
        )

    async def build_economy_factory(
        self: pp.Behaviour | "FactoryMixin",
        condition: Callable[[], bool] | None = None,
    ) -> None:
        poss_tiles = self.map.get_buildable_tiles(self.player)
        tile = random.choice(list(poss_tiles))

        if condition is None:
            condition = lambda: True

        await self.place_order(
            pp.BuildFactoryOrder(
                tile,
                on=condition,
                name="build_economy_factory",
                with_timeout=30,
            )
        )

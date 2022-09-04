from __future__ import annotations


from functools import wraps
import random
from typing import Callable

import ploupy as pp


class TurretMixin:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.ongoing_turret_actions: list[str] = []

        self._wrap_action("build_aggressive_turret")
        self._wrap_action("build_defensive_turret")

    def _wrap_action(self, name: str):
        func = getattr(self, name)

        @wraps(func)
        async def inner(*args, **kwargs):
            self.ongoing_turret_actions.append(func.__name__)
            await func(*args, **kwargs)
            if func.__name__ in self.ongoing_turret_actions:
                self.ongoing_turret_actions.remove(func.__name__)

        setattr(self, name, inner)

    async def build_aggressive_turret(
        self: pp.Behaviour | "TurretMixin",
        condition: Callable[[], bool] | None = None,
    ) -> None:
        opps = self.game.get_opponents(self.player)
        opp = random.choice(tuple(opps))
        opp_tiles = self.map.get_player_tiles(opp)
        opp_border = self.map.get_tiles_border(opp_tiles)
        target = random.choice(tuple(opp_border))

        for neighbour in self.map.get_tile_neighbours(target):
            if neighbour.owner in (None, self.player.username):
                break
        else:
            return

        probes = random.sample(
            tuple(self.player.probes), min(6, len(self.player.probes))
        )

        await self.move_probes(probes, neighbour.coord)

        if condition is None:
            condition = lambda: True

        await self.place_order(
            pp.BuildTurretOrder(
                neighbour,
                on=condition,
                with_timeout=20,
                name="build_aggressive_turret",
            )
        )

    async def build_defensive_turret(
        self: pp.Behaviour | "TurretMixin", attacking_probes: list[pp.Probe]
    ) -> None:

        if len(attacking_probes) < 5:
            return

        target = pp.geometry.center([probe.target for probe in attacking_probes])

        tiles = self.map.get_buildable_tiles(self.player)

        if len(tiles) == 0:
            return

        tile = pp.geometry.closest_tile(tiles, target)

        await self.place_order(
            pp.BuildTurretOrder(
                tile,
                with_timeout=2.0,
                with_retry=False,
                name="build_defensive_turret",
            )
        )

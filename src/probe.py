from __future__ import annotations


from functools import wraps
import random
import math

import ploupy as pp
import numpy as np

from . import utils


class ProbeMixin:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.ongoing_probe_actions: list[str] = []

        self._wrap_action("spread_probes")
        self._wrap_action("perform_localised_attack")

    def _wrap_action(self, name: str):
        func = getattr(self, name)

        @wraps(func)
        async def inner(*args, **kwargs):
            self.ongoing_probe_actions.append(func.__name__)
            await func(*args, **kwargs)
            if func.__name__ in self.ongoing_probe_actions:
                self.ongoing_probe_actions.remove(func.__name__)

        setattr(self, name, inner)

    async def send_exploratory_group(
        self: pp.Behaviour | "ProbeMixin", n_probes: int = 5
    ):
        tiles = self.map.get_unoccupied_tiles()

        if len(tiles) <= 10:
            return  # there is to few tiles for it to be useful

        own_tiles = self.map.get_player_tiles(self.player)

        # estimate chunk size with average factory territory size
        chunk_size = len(own_tiles) / len(self.player.factories)

        # estimate number of chunks of neutral tiles to split into
        n_chunk = math.ceil(len(tiles) / chunk_size)

        # get potential exploratory targets
        centers = pp.geometry.centers([tile.coord for tile in tiles], n_center=n_chunk)
        random.shuffle(centers)

        # get target
        target = None
        for center in centers:
            tile = self.map.get_tile(center)
            if tile.owner is None:
                target = tile
                break

        if target is None:
            return  # no suitable target where found

        probes = utils.get_closest_probes(self.player, target.coord, n_probes)

        try:
            await self.move_probes(probes, target.coord)
        except pp.ActionFailedException:
            pass

    async def spread_probes(self: pp.Behaviour | "ProbeMixin"):
        tiles = self.map.get_unoccupied_tiles()

        orders: dict[np.ndarray, list[pp.Probe]] = {}
        for probe in self.player.probes:
            target = pp.geometry.closest_tile(tiles, probe.pos)
            if target is None:
                continue
            target = tuple(target.coord)  # tuples are hashable
            if not target in orders.keys():
                orders[target] = []
            orders[target].append(probe)

        for target, probes in orders.items():
            await self.move_probes(probes, target)

    async def perform_localised_attack(self: pp.Behaviour, probe_ratio: float = 0.5):

        opps = self.game.get_opponents(self.player)
        opp = random.choice(tuple(opps))

        own_tiles = self.map.get_player_tiles(self.player)

        # get closest factory
        min_idx = -1
        min_dist = 1e9
        min_tile = None
        for i, factory in enumerate(opp.factories):
            tile = pp.geometry.closest_tile(own_tiles, factory.coord)
            dist = pp.geometry.distance(tile.coord, factory.coord)
            if dist < min_dist:
                min_idx = i
                min_dist = dist
                min_tile = tile

        factory = opp.factories[min_idx]

        # select attacking probes
        n_probes = int(len(self.player.probes) * probe_ratio)
        attack_probes = utils.get_closest_probes(self.player, factory.coord, n_probes)

        for i in range(3):  # regroup probes 3 times maximum

            # get rid of dead probes
            attack_probes = [p for p in attack_probes if p.alive]

            if len(attack_probes) == 0:
                return  # abort

            # wait that all probes fits in a small rectangle
            rect = pp.geometry.wrapping_rectangle((p.pos for p in attack_probes))
            if rect.width < 3 and rect.height < 3:
                break

            try:
                await self.move_probes(attack_probes, min_tile.coord)
            except pp.ActionFailedException:
                return  # abort

            cp = pp.geometry.center((p.pos for p in attack_probes))
            dist = pp.geometry.distance(cp, min_tile.coord)

            await pp.sleep(dist / self.config.probe_speed)

        target_tile = pp.geometry.closest_tile(
            own_tiles | self.map.get_unoccupied_tiles(), factory.coord
        )

        dist = pp.geometry.distance(min_tile.coord, target_tile.coord)

        if dist > 3:
            try:
                await self.move_probes(attack_probes, target_tile.coord)
            except pp.ActionFailedException:
                return  # abort

            await pp.sleep(dist / self.config.probe_speed)

        await self.probes_attack(attack_probes)

        # sleep a little to give time to attack
        await pp.sleep(2)

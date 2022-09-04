import random

import ploupy as pp
import numpy as np


async def spread_probes(bhv: pp.Behaviour):

    tiles = bhv.map.get_unoccupied_tiles()

    orders: dict[np.ndarray, list[pp.Probe]] = {}
    for probe in bhv.player.probes:
        target = pp.geometry.closest_tile(tiles, probe.pos)
        if target is None:
            continue
        target = tuple(target.coord)  # tuples are hashable
        if not target in orders.keys():
            orders[target] = []
        orders[target].append(probe)

    for target, probes in orders.items():
        await bhv.move_probes(probes, target)


async def perform_localised_attack(bhv: pp.Behaviour, probe_ratio: float = 0.5):
    opps = bhv.game.get_opponents(bhv.player)
    opp = random.choice(tuple(opps))

    own_tiles = bhv.map.get_player_tiles(bhv.player)

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
    sorted_probes = sorted(
        bhv.player.probes,
        key=lambda p: pp.geometry.distance(p.pos, factory.coord),
    )
    n_probes = int(len(sorted_probes) * probe_ratio)
    attack_probes = sorted_probes[:n_probes]

    while True:
        try:
            await bhv.move_probes(attack_probes, min_tile.coord)
        except pp.ActionFailedException:
            return  # abort

        cp = pp.geometry.center((p.pos for p in attack_probes))
        dist = pp.geometry.distance(cp, min_tile.coord)

        await pp.sleep(dist / bhv.config.probe_speed)

        if dist < 3:
            break

    target_tile = pp.geometry.closest_tile(
        own_tiles | bhv.map.get_unoccupied_tiles(), factory.coord
    )

    dist = pp.geometry.distance(min_tile.coord, target_tile.coord)

    if dist > 3:
        try:
            await bhv.move_probes(attack_probes, target_tile.coord)
        except pp.ActionFailedException:
            return  # abort

        await pp.sleep(dist / bhv.config.probe_speed)

    await bhv.probes_attack(attack_probes)

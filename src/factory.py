import random
from typing import Callable

import ploupy as pp


def _get_build_expansion_factory_target(bhv: pp.Behaviour) -> pp.Tile:
    tiles = bhv.map.get_unoccupied_tiles()
    n_center = len(tiles) // 25
    centers = pp.geometry.centers((tile.coord for tile in tiles), n_center)

    idx = random.randint(0, n_center - 1)
    return bhv.map.get_tile(centers[idx])


async def build_expansion_factory(
    bhv: pp.Behaviour,
    target: pp.Tile | None = None,
) -> None:

    if target is None:
        target = _get_build_expansion_factory_target(bhv)

    sorted_probes = sorted(
        bhv.player.probes,
        key=lambda p: pp.geometry.distance(p.pos, target.coord),
    )
    probes = sorted_probes[:7]

    await bhv.move_probes(probes, target.coord)

    await bhv.place_order(
        pp.BuildFactoryOrder(
            target,
            name="build_expansion_factory",
        ),
    )


async def build_economy_factory(
    bhv: pp.Behaviour,
    condition: Callable[[], bool] | None = None,
) -> None:
    poss_tiles = bhv.map.get_buildable_tiles(bhv.player)
    center = pp.geometry.center([f.coord for f in bhv.player.factories])
    build_tile = pp.geometry.furthest_tile(poss_tiles, center)

    if condition is None:
        condition = lambda: True

    await bhv.place_order(
        pp.BuildFactoryOrder(
            build_tile,
            on=condition,
            name="build_economy_factory",
        )
    )

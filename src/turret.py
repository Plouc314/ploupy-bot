import random
from typing import Callable

import ploupy as pp


async def build_aggressive_turret(
    bhv: pp.Behaviour,
    condition: Callable[[], bool] | None = None,
) -> None:
    opps = bhv.game.get_opponents(bhv.player)
    opp = random.choice(tuple(opps))
    opp_tiles = bhv.map.get_player_tiles(opp)
    opp_border = bhv.map.get_tiles_border(opp_tiles)
    target = random.choice(tuple(opp_border))

    for neighbour in bhv.map.get_tile_neighbours(target):
        if neighbour.owner in (None, bhv.player.username):
            break
    else:
        return

    probes = random.sample(tuple(bhv.player.probes), min(6, len(bhv.player.probes)))

    await bhv.move_probes(probes, neighbour.coord)

    if condition is None:
        condition = lambda: True

    await bhv.place_order(
        pp.BuildTurretOrder(
            neighbour,
            on=condition,
            with_timeout=20,
            name="build_aggressive_turret",
        )
    )


async def build_defensive_turret(
    bhv: pp.Behaviour, attacking_probes: list[pp.Probe]
) -> None:

    if len(attacking_probes) < 5:
        return

    target = pp.geometry.center([probe.target for probe in attacking_probes])

    tiles = bhv.map.get_buildable_tiles(bhv.player)

    if len(tiles) == 0:
        return

    tile = pp.geometry.closest_tile(tiles, target)

    await bhv.place_order(
        pp.BuildTurretOrder(
            tile,
            with_timeout=2.0,
            with_retry=False,
            name="build_defensive_turret",
        )
    )

import asyncio
import ploupy as pp
import numpy as np


class BotBehaviour(pp.Behaviour):
    def __init__(self, uid: str, game: pp.Game) -> None:
        super().__init__(uid, game)
        self._target = None

    async def select_target(self):
        while True:
            coord = np.random.randint(0, np.min(self.config.dim.coord), 2)
            tile = self.map.get_tile(coord)
            if tile.owner in (None, self.player.username):
                break

        self._target = tile

        probes = self.player.probes
        np.random.shuffle(probes)
        probes = probes[:5]

        await self.move_probes(probes, tile.coord)

        cond = (
            lambda: len(self.player.factories) <= 2
            or self.player.money >= self.config.factory_price + self.config.turret_price
        )

        await self.place_order(
            pp.BuildFactoryOrder(self.player, tile, on=cond, with_retry=True)
        )

    async def on_start(self) -> None:
        await self.select_target()

    async def on_factory_build(self, factory: pp.Factory, player: pp.Player) -> None:
        if player is not self.player:
            return

        await self.select_target()

    async def on_probe_build(self, probe: pp.Probe, player: pp.Player) -> None:
        if player is not self.player:
            return

        probes = player.probes
        n_probes = len(probes)

        if (
            n_probes > 10
            and n_probes
            >= 4 / 5 * len(player.factories) * self.config.factory_max_probe
        ):
            np.random.shuffle(probes)
            probes = probes[: n_probes // 2]
            await self.probes_attack(probes)

    async def on_probes_attack(
        self,
        probes: list[pp.Probe],
        attacked_player: pp.Player,
        attacking_player: pp.Player,
    ) -> None:

        if attacked_player is not self.player:
            return

        target = pp.geometry.get_center([probe.target for probe in probes])

        tiles = self.map.get_buildable_tiles(self.player)

        if len(tiles) == 0:
            return

        tile = pp.geometry.get_closest_tile(tiles, target)

        await self.place_order(
            pp.BuildTurretOrder(
                self.player,
                tile,
                with_timeout=2.0,
                with_retry=False,
            )
        )

import ploupy as pp

from ..probe import spread_probes, perform_localised_attack
from ..turret import build_aggressive_turret, build_defensive_turret
from ..factory import build_economy_factory


class MidStage(pp.BehaviourStage):
    def __init__(self, dispatcher: pp.BehaviourDispatcher) -> None:
        super().__init__(dispatcher, "mid")

    def _build_condition(self) -> bool:
        min_money = self.config.factory_price + 2 * self.config.turret_price
        return self.player.money >= min_money and self.player.income > 0

    async def on_stage(self) -> None:
        await spread_probes(self)
        await build_economy_factory(self, condition=self._build_condition)

    async def on_factory_build(self, factory: pp.Factory, player: pp.Player) -> None:
        if player is not self.player:
            return

        await build_aggressive_turret(self, condition=self._build_condition)

    async def on_turret_build(self, turret: pp.Turret, player: pp.Player) -> None:
        if player is not self.player:
            return

        await self.place_order(pp.AcquireTechOrder(pp.Techs.TURRET_SCOPE))

        await build_economy_factory(self, condition=self._build_condition)

    async def on_probes_attack(
        self,
        probes: list[pp.Probe],
        attacked_player: pp.Player,
        attacking_player: pp.Player,
    ) -> None:
        if attacked_player is not self.player:
            return

        await build_defensive_turret(self, probes)

    async def on_probe_build(self, probe: pp.Probe, player: pp.Player) -> None:
        if player is not self.player:
            return

        eco_cond = self.player.money > 200 or self.player.income < 0

        if eco_cond and (
            len(self.player.probes)
            >= 0.8 * len(self.player.factories) * self.player.factories[0].capacity
        ):
            pp.start_background_task(perform_localised_attack, self, probe_ratio=0.7)

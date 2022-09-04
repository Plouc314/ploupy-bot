import ploupy as pp

from ..probe import ProbeMixin
from ..turret import TurretMixin
from ..factory import FactoryMixin


class MidStage(ProbeMixin, FactoryMixin, TurretMixin, pp.BehaviourStage):
    def __init__(self, dispatcher: pp.BehaviourDispatcher) -> None:
        super().__init__(dispatcher, "mid")

    def _build_condition(self) -> bool:
        min_money = self.config.factory_price + 2 * self.config.turret_price
        return self.player.money >= min_money and self.player.income > 0

    async def on_stage(self) -> None:
        await self.spread_probes()
        await self.build_economy_factory(condition=self._build_condition)

    async def on_factory_build(self, factory: pp.Factory, player: pp.Player) -> None:
        if player is not self.player:
            return

        await self.build_aggressive_turret(condition=self._build_condition)

    async def on_turret_build(self, turret: pp.Turret, player: pp.Player) -> None:
        if player is not self.player:
            return

        await self.build_economy_factory(condition=self._build_condition)

    async def on_order_fail(self, order: pp.Order) -> None:
        if order.name == "build_aggressive_turret":
            await self.build_aggressive_turret(condition=self._build_condition)
        if order.name == "build_economy_factory":
            await self.build_economy_factory(condition=self._build_condition)

    async def on_probes_attack(
        self,
        probes: list[pp.Probe],
        attacked_player: pp.Player,
        attacking_player: pp.Player,
    ) -> None:
        if attacked_player is not self.player:
            return

        await self.build_defensive_turret(probes)

    async def on_probe_build(self, probe: pp.Probe, player: pp.Player) -> None:
        if player is not self.player:
            return

        eco_cond = self.player.money > 200 or self.player.income < 0
        action_cond = "perform_localised_attack" not in self.ongoing_probe_actions

        if (
            eco_cond
            and action_cond
            and (
                len(self.player.probes)
                >= 0.8 * len(self.player.factories) * self.player.factories[0].capacity
            )
        ):
            pp.start_background_task(self.perform_localised_attack, probe_ratio=0.7)

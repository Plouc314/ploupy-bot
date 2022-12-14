import random
import ploupy as pp

from ..probe import ProbeMixin
from ..turret import TurretMixin
from ..factory import FactoryMixin


class MidStage(ProbeMixin, FactoryMixin, TurretMixin, pp.BehaviourStage):
    def __init__(self, dispatcher: pp.BehaviourDispatcher) -> None:
        super().__init__(dispatcher, "mid")

    def _neutral_income(self) -> float:
        return len(self.player.factories) * 5

    def _build_factory_condition(self) -> bool:
        min_money = self.config.factory_price + 2 * self.config.turret_price
        min_income = self._neutral_income()
        return self.player.money >= min_money and self.player.income > min_income

    def _build_turret_condition(self) -> bool:
        min_money = self.config.turret_price + 2 * self.config.turret_price
        min_income = self._neutral_income()
        return self.player.money >= min_money and self.player.income > min_income

    def _is_still_enough_neutral_tiles(self) -> bool:
        area = self.metadata.dim.x + self.metadata.dim.y
        return len(self.map.get_unoccupied_tiles()) > 0.2 * area

    def _get_random_acquirable_tech(self) -> pp.Techs | None:
        types = ["factory", "turret", "probe"]
        for tech in self.player.techs:
            tech_type = tech.name.lower().split("_")[0]
            if tech_type in types:
                types.remove(tech_type)

        techs = [t for t in pp.Techs]
        random.shuffle(techs)
        for tech in techs:
            if tech.name.lower().split("_")[0] in types:
                return tech
        return None

    async def on_income(self, money: int) -> None:
        if self.player.money < 1000 or len(self.player.techs) == 3:
            return

        tech = self._get_random_acquirable_tech()
        if tech is not None:
            await self.place_order(pp.AcquireTechOrder(tech))

    async def on_stage(self) -> None:
        await self.spread_probes()
        await self.build_economy_factory(condition=self._build_factory_condition)

    async def on_factory_build(self, factory: pp.Factory, player: pp.Player) -> None:
        if player is not self.player:
            return

        if self._is_still_enough_neutral_tiles():
            await self.send_exploratory_group(
                n_probes=int(0.2 * len(self.player.probes))
            )

        await self.build_aggressive_turret(condition=self._build_turret_condition)

    async def on_turret_build(self, turret: pp.Turret, player: pp.Player) -> None:
        if player is not self.player:
            return

        await self.build_economy_factory(condition=self._build_factory_condition)

    async def on_order_fail(self, order: pp.Order) -> None:
        if order.name == "build_aggressive_turret":
            await self.build_economy_factory(condition=self._build_factory_condition)
        if order.name == "build_economy_factory":
            await self.build_aggressive_turret(condition=self._build_turret_condition)

    async def on_probes_attack(
        self,
        probes: list[pp.Probe],
        attacked_player: pp.Player,
        attacking_player: pp.Player,
    ) -> None:
        if attacked_player is not self.player:
            return

        await self.build_defensive_turrets(probes)

    async def on_probe_build(self, probe: pp.Probe, player: pp.Player) -> None:
        if player is not self.player:
            return

        eco_cond = (
            self.player.money > 200 or self.player.income < self._neutral_income()
        )
        action_cond = "perform_localised_attack" not in self.ongoing_probe_actions
        probe_cond = (
            len(self.player.probes)
            >= 0.8 * len(self.player.factories) * self.player.factories[0].capacity
        )

        if eco_cond and action_cond and (self.player.money > 1000 or probe_cond):
            pp.start_background_task(self.perform_localised_attack, probe_ratio=0.8)

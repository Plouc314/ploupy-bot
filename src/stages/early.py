from typing import TYPE_CHECKING

import ploupy as pp

from ..probe import ProbeMixin
from .. import utils

if TYPE_CHECKING:
    from .start import StartStage


class EarlyStage(ProbeMixin, pp.BehaviourStage):
    def __init__(
        self, dispatcher: pp.BehaviourDispatcher, start_stage: "StartStage"
    ) -> None:
        super().__init__(dispatcher, "early")

        self._start_stage = start_stage

    def _get_tech(self) -> pp.Techs:
        if self.metadata.dim.x <= 17:
            return pp.Techs.TURRET_SCOPE
        return pp.Techs.PROBE_CLAIM_INTENSITY

    async def on_stage(self) -> None:

        # move probes back to second target
        # -> make sure to be able to build the factory
        if self._start_stage._second_target is not None:
            target = self._start_stage._second_target.coord
            probes = utils.get_closest_probes(self.player, target, n_probes=3)

            try:
                await self.move_probes(probes, target)
            except pp.ActionFailedException:
                pass

        await self.place_order(pp.AcquireTechOrder(tech=self._get_tech()))

    async def on_probe_build(self, probe: pp.Probe, player: pp.Player) -> None:
        if player is not self.player:
            return

        if len(self.player.probes) in (8, 12):
            await self.send_exploratory_group(7)

    async def on_acquire_tech(self, tech: pp.Techs, player: pp.Player) -> None:
        if player is not self.player:
            return

        await self.set_current_stage("mid")

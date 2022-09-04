import ploupy as pp

from ..probe import ProbeMixin


class EarlyStage(ProbeMixin, pp.BehaviourStage):
    def __init__(self, dispatcher: pp.BehaviourDispatcher) -> None:
        super().__init__(dispatcher, "early")

    async def on_factory_build(self, factory: pp.Factory, player: pp.Player) -> None:
        pp.start_background_task(self.spread_probes)
        await self.place_order(pp.AcquireTechOrder(tech=pp.Techs.PROBE_CLAIM_INTENSITY))

    async def on_acquire_tech(self, tech: pp.Techs, player: pp.Player) -> None:
        if player is not self.player:
            return

        await self.set_current_stage("mid")

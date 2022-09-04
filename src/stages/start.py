import ploupy as pp

from ..factory import FactoryMixin


class StartStage(FactoryMixin, pp.BehaviourStage):
    def __init__(self, dispatcher: pp.BehaviourDispatcher) -> None:
        super().__init__(dispatcher, "start")

        self._first_target = None
        self._second_target = None
        self._st_recall = False

    async def on_start(self) -> None:
        self._first_target = self._get_build_expansion_factory_target()
        self._second_target = self._get_build_expansion_factory_target()

        await self.build_expansion_factory(target=self._first_target)

    async def on_factory_build(self, factory: pp.Factory, player: pp.Player) -> None:
        if player is not self.player:
            return

        await self.build_expansion_factory(target=self._second_target)

        await self.set_current_stage("early")

    async def on_probe_build(self, probe: pp.Probe, player: pp.Player) -> None:
        if player is not self.player:
            return

        if not self._st_recall:
            self._st_recall = True
            await self.move_probes(self.player.probes[:3], self._first_target.coord)

        await self.move_probes([probe], self._second_target.coord)

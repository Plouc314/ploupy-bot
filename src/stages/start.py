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

        await self.build_expansion_factory(target=self._first_target)

    async def on_factory_build(self, factory: pp.Factory, player: pp.Player) -> None:
        if player is not self.player:
            return

        await self.set_current_stage("early")

    async def on_probe_build(self, probe: pp.Probe, player: pp.Player) -> None:
        if player is not self.player:
            return

        if not self._st_recall:
            self._st_recall = True

            # recall first probes to first factory target
            # -> make sure to have enough occupation
            try:
                await self.move_probes(self.player.probes[:3], self._first_target.coord)
            except pp.ActionFailedException:
                # if first target isn't available anymore -> pick new target
                await self.build_expansion_factory(probes=self.player.probes[:3])

            # select second target, and give order to build factory
            # as the second factory could potentially be built before the first one
            self._second_target = self._get_build_expansion_factory_target()
            await self.build_expansion_factory(target=self._second_target, probes=[])

        # move all newly built probes to the second target
        try:
            await self.move_probes([probe], self._second_target.coord)
        except pp.ActionFailedException:
            # if second target isn't available anymore -> pick new target
            await self.build_expansion_factory(probes=self.player.probes[:4])

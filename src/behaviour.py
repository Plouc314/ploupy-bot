import ploupy as pp

from .stages.start import StartStage
from .stages.early import EarlyStage
from .stages.mid import MidStage


class BotBehaviour(pp.BehaviourDispatcher):
    def __init__(self, uid: str, game: pp.Game) -> None:
        super().__init__(uid, game)

        start_stage = StartStage(self)
        early_stage = EarlyStage(self, start_stage=start_stage)
        mid_stage = MidStage(self)

        self.add_stage(start_stage)
        self.add_stage(early_stage)
        self.add_stage(mid_stage)

        # select initial state
        if len(self.player.techs) >= 1:
            current_stage = "mid"
        elif len(self.player.factories) >= 2:
            current_stage = "early"
        else:
            current_stage = "start"

        self._current_stage = current_stage

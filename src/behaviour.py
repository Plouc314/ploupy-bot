import ploupy as pp

from .stages.start import StartStage
from .stages.early import EarlyStage
from .stages.mid import MidStage


class BotBehaviour(pp.BehaviourDispatcher):
    def __init__(self, uid: str, game: pp.Game) -> None:
        super().__init__(uid, game)

        self.add_stage(StartStage(self))
        self.add_stage(EarlyStage(self))
        self.add_stage(MidStage(self))

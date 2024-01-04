from abc import ABC


class TrackStatus(ABC):

    def __init__(self, status: str) -> None:
        self.status = status


class TrackRemoved(TrackStatus):

    def __init__(self):
        super().__init__('removed')


class TrackWaited(TrackStatus):

    def __init__(self):
        super().__init__('waited')


class TrackPlaying(TrackStatus):

    def __init__(self):
        super().__init__('playing')


class TrackPlayed(TrackStatus):

    def __init__(self):
        super().__init__('played')

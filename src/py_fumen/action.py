# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Tuple

from .constants import FieldConstants
from .operation import Mino, Rotation, Operation

@dataclass
class Action():
    operation: Operation
    rise: bool
    mirror: bool
    colorize: bool
    comment: bool
    lock: bool

class ActionDecoder() :
    PIECE_OFFSET = {
        Mino.I: {
            Rotation.REVERSE: (1, 0),
            Rotation.LEFT: (0, -1),
        },
        Mino.O: {
            Rotation.SPAWN: (0, -1),
            Rotation.REVERSE: (1, 0),
            Rotation.LEFT: (1, -1),
        },
        Mino.Z: {
            Rotation.SPAWN: (0, -1),
            Rotation.LEFT: (1, 0),
        },
        Mino.S: {
            Rotation.SPAWN: (0, -1),
            Rotation.RIGHT: (-1, 0),
        },
    }

    _consts: FieldConstants

    def __init__(self, consts: FieldConstants):
        self._consts = consts

    def decode_coords(self, encoded_coords: int,
            mino: Mino, rotation: Rotation) -> Tuple[int, int]:
        dx, dy = self.PIECE_OFFSET.get(mino, {}).get(rotation, (0, 0))
        return (dx + encoded_coords % self._consts.WIDTH,
                dy + self._consts.HEIGHT - n // self._consts.WIDTH - 1)

    def decode(self, encoded_action: int) -> Action:
        q, r = divmod(encoded_action, 8)
        mino = Mino(r)
        q, r = divmod(q, 4)
        rotation = Rotation(r)
        q, r = divmod(q, self.consts.TOTAL_BLOCK_COUNT)
        x, y = self.decode_coords(r, mino, rotation)
        q, r = divmod(q, 2)
        rise = bool(r)
        q, r = divmod(q, 2)
        mirror = bool(r)
        q, r = divmod(q, 2)
        colorize = bool(r)
        q, r = divmod(q, 2)
        comment = bool(r)
        q, r = divmod(q, 2)
        lock = not bool(r)

        return Action(operation=Operation(mino=mino, rotation=rotation,
                                          x=x, y=y),
                      rise=rise, mirror=mirror, colorize=colorize,
                      comment=comment, lock=lock)

class ActionEncoder():
    PIECE_OFFSET = {
        Mino.I: {
            Rotation.REVERSE: (-1, 0),
            Rotation.LEFT: (0, 1),
        },
        Mino.O: {
            Rotation.SPAWN: (0, 1),
            Rotation.REVERSE: (-1, 0),
            Rotation.LEFT: (-1, 1),
        },
        Mino.Z: {
            Rotation.SPAWN: (0, 1),
            Rotation.LEFT: (-1, 0),
        },
        Mino.S: {
            Rotation.SPAWN: (0, 1),
            Rotation.RIGHT: (1, 0),
        },
    }
    _consts: FieldConstants

    @staticmethod
    def encode_rotation(operation: Operation) -> int:
        if operation.mino.is_colored():
            return operation.rotation.value
        else:
            return 0

    def __init__(self, consts: FieldConstants):
        self.consts = consts

    def encode_position(self, operation: Operation) -> int:
        dx, dy = self.PIECE_OFFSET.get(
            operation.mino, {}
        ).get(operation.rotation, (0, 0))
        x, y = ((dx + operation.x, dy + operation.y)
                if operation.mino.is_colored() else (0, 22))
        return (self.consts.HEIGHT - y - 1) * self.consts.WIDTH + x

    def encode(self, action: Action) -> int:
        encoded_action = int(not action.lock)
        encoded_action *= 2
        encoded_action += int(action.comment)
        encoded_action *= 2
        encoded_action += int(action.colorize)
        encoded_action *= 2
        encoded_action += int(action.mirror)
        encoded_action *= 2
        encoded_action += int(action.rise)
        encoded_action *= self.consts.TOTAL_BLOCK_COUNT
        encoded_action += self.encode_position(action.operation)
        encoded_action *= 4
        encoded_action += self.encode_rotation(action.operation)
        encoded_action *= 8
        encoded_action += action.operation.mino

        return encoded_action

# Copyright (C) 2024 Andrew Wason
# SPDX-License-Identifier: GPL-3.0-or-later
 
class SequencerError(Exception):
    pass


class InvalidSequenceError(SequencerError):
    pass


class OpsError(SequencerError):
    def __init__(self, message: str, result: set[str]):
        super().__init__(message)
        self.add_note(f"bpy.ops returned {result}")

    @classmethod
    def check(cls, result: set, message: str):
        if result != {"FINISHED"}:
            raise cls(message, result)
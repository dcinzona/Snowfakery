from enum import Enum, auto

import yaml

IdManager = "snowfakery.data_generator_runtime.IdManager"


class ObjectRow(yaml.YAMLObject):
    """Represents a single row

    Uses __getattr__ so that the template evaluator can use dot-notation."""

    yaml_loader = yaml.SafeLoader
    yaml_dumper = yaml.SafeDumper
    yaml_tag = "!snowfakery_objectrow"

    __slots__ = ["_tablename", "_values", "_child_index"]

    def __init__(self, tablename, values=(), index=0):
        self._tablename = tablename
        self._values = values
        self._child_index = index

    def __getattr__(self, name):
        try:
            return self._values[name]
        except KeyError:
            raise AttributeError(name)

    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return f"<ObjectRow {self._tablename} {self.id}>"

    def __getstate__(self):
        return {"_tablename": self._tablename, "_values": self._values}

    def __setstate__(self, state):
        for slot, value in state.items():
            setattr(self, slot, value)

    @property
    def _name(self):
        return self._values.get("name")


class ObjectReference(yaml.YAMLObject):
    def __init__(self, tablename, id):
        self._tablename = tablename
        self.id = id


class SlotState(Enum):
    """The current state of a NicknameSlot.

    UNUSED=empty, ALLOCATED=referenced, CONSUMED=object generated"""

    UNUSED = auto()
    ALLOCATED = auto()
    CONSUMED = auto()


class NicknameSlot(ObjectReference):
    """A slot that represents a Nickname or Tablename"""

    _tablename: str
    id_manager: IdManager
    allocated_id: int = None

    def __init__(self, tablename, id_manager):
        self._tablename = tablename
        self.id_manager = id_manager

    @property
    def id(self):
        "Get an id corresponding to this slot. Generate one if necessary."
        if self.allocated_id is None:
            self.allocated_id = self.id_manager.generate_id(self._tablename)
        return self.allocated_id

    def consume_slot(self):
        "Mark a slot as filled by an object and return its id for use by the object."
        rc = self.allocated_id
        self.allocated_id = SlotState.CONSUMED
        return rc

    @property
    def status(self):
        "Is the slot empty/unreferenced, allocated/referenced or consumed/used"
        if self.allocated_id is None:
            return SlotState.UNUSED
        elif isinstance(self.allocated_id, int):
            return SlotState.ALLOCATED
        elif self.allocated_id == SlotState.CONSUMED:
            return SlotState.CONSUMED

    def __repr__(self):
        return f"<NicknameSlot {self._tablename} {self.status} {self.allocated_id}>"

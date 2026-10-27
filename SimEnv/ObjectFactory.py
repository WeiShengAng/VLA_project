
from typing import Any

class ObjectFactory:
    # Initialize the object registry.
    def __init__(self):
        self.objects: dict[str, dict[str, Any]] = {}
        self._next_id = 1

    # Generate a new unique internal object ID.
    def _generate_object_id(self) -> str:
        object_id = f"obj_{self._next_id}"
        self._next_id += 1
        return object_id

    # Create a new tracked object and return the factory-assigned object ID.
    def create_object(
        self,
        body_id: Any,
        object_type: str,
        color: str | None = None,
        position: dict[str, float] | None = None
    ) -> str:
        object_id = self._generate_object_id()
        object_data: dict[str, Any] = {
            "object_id": object_id,
            "id": body_id,
            "type": object_type,
            "color": color,
            "position": position if position is not None else {"x": 0.0, "y": 0.0, "z": 0.0}
        }
        self.objects[object_id] = object_data
        return object_id

    # Retrieve object data by internal object ID.
    def get_object(self, object_id: str):
        return self.objects.get(object_id)

    # Retrieve the first tracked object whose color attribute matches.
    def get_object_by_color(self, color: str):
        for obj in self.objects.values():
            if obj.get("color") == color:
                return obj
        return None

    # Return all object records currently managed by the factory.
    def get_all_objects(self):
        return self.objects


factory = ObjectFactory()
OBJECTS = factory.objects

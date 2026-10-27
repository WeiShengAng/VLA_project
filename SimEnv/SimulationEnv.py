import pybullet as p
import pybullet_data
import time

from SimEnv.ObjectFactory import factory

class SimEnv:
    # Initialize the simulation environment and object factory.
    def __init__(self):
        self.client = p.connect(p.GUI)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -9.8)

        self.plane = p.loadURDF("plane.urdf")
        self.object_factory = factory

        self._spawn_objects()

    # Spawn initial objects into the simulation and register them with the factory.
    def _spawn_objects(self):
        # red block
        red_block = p.loadURDF(
            "cube_small.urdf",
            basePosition=[0.2, 0, 0.05],
            globalScaling=1
        )
        p.changeVisualShape(red_block, -1, rgbaColor=[1, 0, 0, 1])
        self.object_factory.create_object(
            body_id=red_block,
            object_type="block",
            color="red",
            position={"x": 0.2, "y": 0, "z": 0.05}
        )

        # blue block
        blue_block = p.loadURDF(
            "cube_small.urdf",
            basePosition=[-0.2, 0, 0.05],
            globalScaling=1
        )
        p.changeVisualShape(blue_block, -1, rgbaColor=[0, 0, 1, 1])
        self.object_factory.create_object(
            body_id=blue_block,
            object_type="block",
            color="blue",
            position={"x": -0.2, "y": 0, "z": 0.05}
        )

    # Return the current list of tracked objects with updated positions.
    def get_objects(self):
        result = []
        for obj in self.object_factory.get_all_objects().values():
            if obj["id"] is None:
                continue

            pos, _ = p.getBasePositionAndOrientation(obj["id"])
            obj["position"] = {"x": pos[0], "y": pos[1], "z": pos[2]}
            result.append({
                "id": obj["id"],
                "type": obj["type"],
                "color": obj["color"],
                "position": obj["position"]
            })
        return result

    # Move a tracked body to a new position in the simulation,
    # preserving its current orientation.
    def set_object_position(self, body_id, position):
        _, orn = p.getBasePositionAndOrientation(body_id)
        p.resetBasePositionAndOrientation(
            body_id,
            [position["x"], position["y"], position["z"]],
            orn
        )

    # Advance the physics simulation by one step.
    def step(self):
        p.stepSimulation()
        time.sleep(1/240)

    # Run the simulation loop continuously.
    def run(self):
        while True:
            self.step()
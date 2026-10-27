import os
import time

import mujoco

from SimEnv.ObjectFactory import factory

_SCENE = os.path.join(os.path.dirname(__file__), "scenes", "vla_scene.xml")

# (body name in the scene, color attribute for the world model)
_BLOCKS = [("red", "red"), ("blue", "blue")]


class MujocoEnv:
    # MuJoCo-backed simulation env. Same interface as the PyBullet SimEnv
    # (get_objects / set_object_position / step) so the pipeline is unchanged.
    #
    # The scene contains a Franka Emika Panda arm, held at its home pose
    # (the robot does nothing), plus two colored blocks. The blocks are mocap
    # bodies, so they are moved kinematically via mocap_pos.

    def __init__(self, scene_path: str = _SCENE):
        self.model = mujoco.MjModel.from_xml_path(scene_path)
        self.data = mujoco.MjData(self.model)
        self.object_factory = factory
        self.viewer = None

        # Load the arm's home pose; its position actuators then hold it there.
        key_id = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_KEY, "home")
        if key_id >= 0:
            mujoco.mj_resetDataKeyframe(self.model, self.data, key_id)

        mujoco.mj_forward(self.model, self.data)
        self._register_objects()

    # Register the scene's colored blocks with the shared world model.
    def _register_objects(self):
        for body_name, color in _BLOCKS:
            body_id = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_BODY, body_name)
            if body_id < 0:
                continue
            pos = self.data.xpos[body_id]
            self.object_factory.create_object(
                body_id=int(body_id),
                object_type="block",
                color=color,
                position={"x": float(pos[0]), "y": float(pos[1]), "z": float(pos[2])},
            )

    # Return the current list of tracked objects with updated positions.
    def get_objects(self):
        result = []
        for obj in self.object_factory.get_all_objects().values():
            if obj["id"] is None:
                continue
            pos = self.data.xpos[obj["id"]]
            obj["position"] = {"x": float(pos[0]), "y": float(pos[1]), "z": float(pos[2])}
            result.append({
                "id": obj["id"],
                "type": obj["type"],
                "color": obj["color"],
                "position": obj["position"],
            })
        return result

    # Move a tracked (mocap) body to a new position (instant).
    def set_object_position(self, body_id, position):
        mocap_id = self.model.body_mocapid[body_id]
        if mocap_id < 0:
            return  # not a movable mocap body
        self.data.mocap_pos[mocap_id] = [position["x"], position["y"], position["z"]]
        mujoco.mj_forward(self.model, self.data)

    # Move a tracked (mocap) body to a position smoothly at a fixed speed
    # (m/s), stepping and rendering so the motion is visible. Used for a gentle
    # drop. Blocks on the main thread for the duration of the move.
    def glide_to(self, body_id, position, speed=0.2):
        mocap_id = self.model.body_mocapid[body_id]
        if mocap_id < 0:
            return
        start = list(self.data.mocap_pos[mocap_id])
        target = [position["x"], position["y"], position["z"]]
        dist = sum((t - s) ** 2 for s, t in zip(start, target)) ** 0.5
        if dist == 0:
            return
        steps = max(1, int(dist / (speed * self.model.opt.timestep)))
        for i in range(1, steps + 1):
            frac = i / steps
            self.data.mocap_pos[mocap_id] = [s + (t - s) * frac for s, t in zip(start, target)]
            self.step()
            self.render()

    # Advance the physics by one timestep (roughly real-time).
    def step(self):
        mujoco.mj_step(self.model, self.data)
        time.sleep(self.model.opt.timestep)

    # --- Interactive viewer (optional; main thread only) ---

    def start_viewer(self):
        import mujoco.viewer
        self.viewer = mujoco.viewer.launch_passive(self.model, self.data)

    def viewer_running(self) -> bool:
        return self.viewer is None or self.viewer.is_running()

    def render(self):
        if self.viewer is not None:
            self.viewer.sync()

    def close(self):
        if self.viewer is not None:
            self.viewer.close()
            self.viewer = None

# Resting height of a block on the floor (matches the box half-size in the
# MuJoCo scene, so the block sits exactly on the ground).
FLOOR_Z = 0.025

# How far "pick" raises a block above its current position.
PICK_HEIGHT = 0.2


class Skill:
    # Abstract action layer (Phase 1): operates on world-model object records
    # and, when a simulation is attached, reflects changes into it via SimEnv.
    # No grasp physics, no IK.

    def __init__(self, env=None):
        self.env = env

    # Abstractly "pick up" an object: mark it held and raise it in z (instant).
    def pick(self, obj):
        obj["held"] = True
        new_pos = dict(obj["position"])
        new_pos["z"] = new_pos["z"] + PICK_HEIGHT
        obj["position"] = new_pos
        self._apply(obj)

    # "Drop" an object: release it and let it descend gently to the floor.
    def drop(self, obj):
        obj["held"] = False
        target = dict(obj["position"])
        target["z"] = FLOOR_Z
        obj["position"] = target
        if self.env is not None and obj.get("id") is not None:
            # Slow animated descent (mocap bodies ignore gravity).
            self.env.glide_to(obj["id"], target)

    # Exchange the positions of two objects in the world state and the sim.
    def swap(self, obj_a, obj_b):
        pos_a = dict(obj_a["position"])
        pos_b = dict(obj_b["position"])
        obj_a["position"] = pos_b
        obj_b["position"] = pos_a
        self._apply(obj_a)
        self._apply(obj_b)

    # Reflect an object's current world-state position into the simulation.
    def _apply(self, obj):
        if self.env is not None and obj.get("id") is not None:
            self.env.set_object_position(obj["id"], obj["position"])

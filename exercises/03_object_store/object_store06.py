# I AM NOT DONE
"""Chapter 3: Plasma Object Store & Zero-Copy - Exercise 6: Custom Serializers with ray.util.

Ray serializes Python objects into the Plasma store using optimized PyArrow and CloudPickle engines.
However, for custom data structures, high-performance C-struct wrappers, or objects that cannot
be cleanly pickled by default, Ray provides `ray.util.register_serializer`.

Key Concepts:
1. `ray.util.register_serializer(cls, serializer=..., deserializer=...)`:
   - `serializer(obj) -> serialized_data`: Converts a custom object into serializable primitives (e.g. bytes, tuple).
   - `deserializer(serialized_data) -> obj`: Reconstructs the original object from the primitives.
2. Speed & Compression: Custom serializers can strip unnecessary overhead or compress data before
   writing to shared memory.

Your Task:
- Define a custom class `Vector3D` representing 3D spatial coordinates `(x, y, z)`.
- Implement `serialize_vector(vec: Vector3D) -> tuple[float, float, float]` and
  `deserialize_vector(data: tuple[float, float, float]) -> Vector3D`.
- Register them using `ray.util.register_serializer`.
- Pass a `Vector3D` instance to a remote task `@ray.remote def compute_magnitude(v: Vector3D) -> float`
  which calculates `math.sqrt(v.x**2 + v.y**2 + v.z**2)`.
- Verify the returned magnitude.
"""

import math
import ray


class Vector3D:
    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector3D):
            return False
        return (self.x, self.y, self.z) == (other.x, other.y, other.z)


def serialize_vector(vec: Vector3D) -> tuple[float, float, float]:
    # TODO: Return tuple (vec.x, vec.y, vec.z)
    return (0.0, 0.0, 0.0)


def deserialize_vector(data: tuple[float, float, float]) -> Vector3D:
    # TODO: Reconstruct Vector3D from data tuple
    return Vector3D(0.0, 0.0, 0.0)


# TODO: Define compute_magnitude remote function
def compute_magnitude(v: Vector3D) -> float:
    return math.sqrt(v.x**2 + v.y**2 + v.z**2)


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # TODO: Register custom serializer
    # ray.util.register_serializer(
    #     Vector3D,
    #     serializer=serialize_vector,
    #     deserializer=deserialize_vector,
    # )

    vec = Vector3D(3.0, 4.0, 12.0)
    _ = vec

    # TODO: Put vec into object store and compute magnitude via compute_magnitude.remote(vec)
    # mag_ref = compute_magnitude.remote(vec)
    # mag = ray.get(mag_ref)
    mag = 0.0

    # sqrt(3^2 + 4^2 + 12^2) = sqrt(9 + 16 + 144) = sqrt(169) = 13.0
    assert math.isclose(mag, 13.0), f"Expected magnitude 13.0, got {mag}"
    print(f"✓ object_store06 verified: Custom serializer registered and executed magnitude={mag}!")


if __name__ == "__main__":
    verify()

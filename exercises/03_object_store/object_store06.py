"""
Exercise: exercises/03_object_store/object_store06.py
Topic: Custom Object Serializers with ray.util

Context & Why:
Ray uses PyArrow and Cloudpickle to serialize objects. For complex domain objects, custom C++ types,
or network handles, default pickling can be slow or unsupported.

`ray.util.register_serializer` allows defining custom, highly optimized serialization and deserialization
hooks, ensuring fast transfers and compact memory footprints.

Instructions:
1. Register a custom serializer and deserializer for a domain data class.
2. Pass instances through Ray tasks and verify exact reconstruction.
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
    # WHY: Custom serializers bypass generic pickle overhead for domain-specific data structures.
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

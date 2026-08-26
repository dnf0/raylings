"""Chapter 3: Plasma Object Store & Zero-Copy - Solution 6: Custom Serializers with ray.util.

Reference Solution for object_store06.
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
    return (vec.x, vec.y, vec.z)


def deserialize_vector(data: tuple[float, float, float]) -> Vector3D:
    return Vector3D(*data)


@ray.remote
def compute_magnitude(v: Vector3D) -> float:
    return math.sqrt(v.x**2 + v.y**2 + v.z**2)


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    ray.util.register_serializer(
        Vector3D,
        serializer=serialize_vector,
        deserializer=deserialize_vector,
    )

    vec = Vector3D(3.0, 4.0, 12.0)

    mag_ref = compute_magnitude.remote(vec)
    mag = ray.get(mag_ref)

    assert math.isclose(mag, 13.0), f"Expected magnitude 13.0, got {mag}"
    print(f"✓ object_store06 verified: Custom serializer registered and executed magnitude={mag}!")


if __name__ == "__main__":
    verify()

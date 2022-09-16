import ploupy as pp


def get_closest_probes(
    player: pp.Player, position: pp.Pos, n_probes: int
) -> list[pp.Probe]:
    """
    Return the closest probes to the given
    position.
    """
    sorted_probes = sorted(
        player.probes,
        key=lambda p: pp.geometry.distance(p.pos, position),
    )
    return sorted_probes[:n_probes]

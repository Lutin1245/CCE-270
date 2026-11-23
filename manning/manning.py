def manning_flow(n, A, R, S):
    """Flow (cfs) from Manning's n, area A (ft^2), hydraulic radius R (ft), and slope S (ft/ft)."""
    return 1.49 / n * A * R ** (2 / 3) * S ** 0.5
    
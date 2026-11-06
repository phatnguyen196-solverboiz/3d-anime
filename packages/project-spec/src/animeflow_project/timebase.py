"""Frame/sample math without floating point drift."""


def frames_to_samples(
    frame: int, fps_numerator: int, fps_denominator: int, sample_rate: int
) -> int:
    """Convert an absolute frame position to samples, rounding halves upward."""
    if frame < 0 or min(fps_numerator, fps_denominator, sample_rate) <= 0:
        raise ValueError("Frame must be non-negative; FPS and sample rate must be positive.")
    numerator = frame * fps_denominator * sample_rate
    return (2 * numerator + fps_numerator) // (2 * fps_numerator)

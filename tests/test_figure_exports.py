from __future__ import annotations

from pathlib import Path


def test_save_writes_png_svg_pdf(tmp_path: Path) -> None:
    from puckworks.figures import _plt, _save

    plt = _plt()
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    try:
        returned = Path(_save(fig, str(tmp_path), "smoke.png"))
    finally:
        plt.close(fig)

    assert returned == tmp_path / "smoke.png"
    for suffix in (".png", ".svg", ".pdf"):
        path = tmp_path / f"smoke{suffix}"
        assert path.is_file()
        assert path.stat().st_size > 0


def test_vector_outputs_are_byte_reproducible(tmp_path: Path) -> None:
    from puckworks.figures import _plt, _save

    plt = _plt()

    def render(destination: Path) -> None:
        fig, ax = plt.subplots()
        ax.plot([0, 1], [1, 0], label="series")
        ax.legend()
        try:
            _save(fig, str(destination), "stable.png")
        finally:
            plt.close(fig)

    first = tmp_path / "first"
    second = tmp_path / "second"
    render(first)
    render(second)

    assert (first / "stable.svg").read_bytes() == (second / "stable.svg").read_bytes()
    assert (first / "stable.pdf").read_bytes() == (second / "stable.pdf").read_bytes()

"""
CLI entry point for the Musical Harmony Visualization tool.

Generates chord progressions in various styles, renders audio (MIDI + WAV),
and creates matplotlib visualizations.
"""

import argparse
import os
import sys

from theory import ProgressionStyle, create_chord, get_style_progression
from synthesis import create_audio_files, SynthConfig
from visualization import create_rich_visualization


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate chord progressions with audio and visualizations.",
    )
    parser.add_argument(
        "--style",
        type=str,
        choices=[s.value for s in ProgressionStyle],
        default=None,
        help="Progression style to generate. If omitted, generates all styles.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=".",
        help="Directory for output files (default: current directory).",
    )
    parser.add_argument(
        "--tempo",
        type=int,
        default=120,
        help="Tempo in BPM (default: 120).",
    )
    return parser.parse_args()


def generate_for_style(
    style: ProgressionStyle,
    output_dir: str,
    config: SynthConfig,
) -> None:
    """Generate all output files for a single progression style.

    Args:
        style: The ProgressionStyle to generate.
        output_dir: Directory to write output files.
        config: Synthesis configuration.
    """
    print(f"\nGenerating {style.value} progression...")

    progression_data = get_style_progression(style)
    chords = [
        create_chord(root, chord_type, duration)
        for root, chord_type, duration in progression_data
    ]

    output_base = os.path.join(output_dir, f"harmony_{style.value}")

    create_audio_files(chords, output_base, config)
    create_rich_visualization(chords, output_base, style)

    print(f"Generated files for {style.value}:")
    print(f"  - {output_base}.mid (MIDI file)")
    print(f"  - {output_base}.wav (Audio file)")
    print(f"  - {output_base}_motion.png (Motion visualization)")
    print(f"  - {output_base}_advanced_analysis.png (Advanced analysis)")


def main() -> None:
    """Main entry point."""
    args = parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    config = SynthConfig(tempo_bpm=args.tempo)

    if args.style:
        style = ProgressionStyle(args.style)
        generate_for_style(style, args.output_dir, config)
    else:
        for style in ProgressionStyle:
            generate_for_style(style, args.output_dir, config)


if __name__ == "__main__":
    main()

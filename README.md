# Musical Harmony Visualization System

A sophisticated Python-based system that generates, visualizes, and synthesizes musical harmonies across different styles. This system combines music theory, audio synthesis, and creative visualization techniques to create a rich, multi-sensory representation of harmonic progressions.

## Features

### Musical Styles
- Jazz (extended harmonies and complex progressions)
- Impressionist (colorful and unconventional harmonies)
- Modal (sustained harmonies with modal characteristics)
- Classical (traditional harmonic progressions)

### Chord Types
- Major/Minor triads
- Dominant 7th chords
- Major/Minor 7th chords
- Extended chords (9th, 11th, 13th)
- Diminished and half-diminished
- Suspended chords
- Augmented chords

### Visualization Types
1. Motion Visualization
   - Circular representation with motion trails
   - Dynamic chord relationships
   - Color-coded harmony patterns

2. Advanced Analysis
   - Harmonic rhythm visualization
   - Note density plots
   - Complexity analysis
   - Style-specific patterns

### Audio Output
- MIDI file generation
- WAV file synthesis with:
  - Rich overtone structure
  - ADSR envelope shaping
  - Frequency modulation
  - Dynamic velocity control

## Installation

1. Clone this repository:
```bash
git clone [your-repo-url]
cd musical-harmony-visualizer
```

2. Install required dependencies:
```bash
pip install numpy matplotlib scipy midiutil
```

## Usage

### Basic Usage

Generate a single style progression:

```python
from harmony_visualizer import EnhancedHarmonyVisualizer, ProgressionStyle

# Create visualizer
visualizer = EnhancedHarmonyVisualizer()

# Generate jazz progression
style = ProgressionStyle.JAZZ
progression_data = visualizer.get_style_progression(style)
chords = [visualizer.create_advanced_chord(root, chord_type, duration) 
          for root, chord_type, duration in progression_data]
visualizer.create_rich_visualization(chords, f"harmony_{style.value}", style)
```

### Generate All Styles

```python
# Generate all available styles
styles = [
    ProgressionStyle.JAZZ,
    ProgressionStyle.IMPRESSIONIST,
    ProgressionStyle.MODAL,
    ProgressionStyle.CLASSICAL
]

for style in styles:
    progression_data = visualizer.get_style_progression(style)
    chords = [visualizer.create_advanced_chord(root, chord_type, duration) 
              for root, chord_type, duration in progression_data]
    visualizer.create_rich_visualization(chords, f"harmony_{style.value}", style)
```

## Output Files

For each generated progression, the system creates:

1. `harmony_[style].mid`
   - MIDI file for playback in any DAW or media player
   - Contains full chord progression with velocity information

2. `harmony_[style].wav`
   - Synthesized audio file
   - Rich harmonic content with overtones
   - Professional-quality ADSR envelope shaping

3. `harmony_[style]_motion.png`
   - Circular visualization of harmonic motion
   - Shows chord relationships and transitions
   - Includes motion trails for progression analysis

4. `harmony_[style]_advanced_analysis.png`
   - Multi-panel analysis visualization
   - Harmonic rhythm display
   - Note density analysis
   - Style-specific pattern analysis

## Customization

### Creating Custom Progressions

```python
# Define custom progression
custom_progression = [
    ('C4', 'major7', 2.0),    # (root, chord_type, duration)
    ('A4', 'minor7', 2.0),
    ('D4', 'dominant7', 2.0),
    ('G4', 'major7', 2.0)
]

# Generate visualization
chords = [visualizer.create_advanced_chord(root, chord_type, duration) 
          for root, chord_type, duration in custom_progression]
visualizer.create_rich_visualization(chords, "custom_progression")
```

### Modifying Synthesis Parameters

The synthesis engine can be customized by modifying:
- Number of overtones
- ADSR envelope parameters
- Modulation depth and frequency
- Overall duration and tempo

## Musical Theory

### Chord Construction
- Triads: Root, Third, Fifth
- Seventh Chords: Root, Third, Fifth, Seventh
- Extended Chords: Additional ninths, elevenths, thirteenths
- Altered Chords: Modified fifths or ninths

### Style Characteristics
- Jazz: Complex harmonies, extended chords, ii-V-I progressions
- Impressionist: Colorful harmonies, non-traditional progressions
- Modal: Sustained harmonies, modal interchange
- Classical: Traditional harmony, functional progressions

## Technical Details

### Audio Synthesis
- Sample rate: 44100 Hz
- Bit depth: 16-bit
- Synthesis method: Additive with FM
- Envelope: ADSR with customizable parameters

### Visualization
- High-resolution output (300 DPI)
- Multiple visualization layers
- Real-time animation capabilities
- Advanced color mapping

## Contributing

Areas for potential enhancement:
- Additional musical styles
- More visualization types
- Enhanced synthesis methods
- Real-time MIDI input
- Additional analysis tools
- GUI interface

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built using numpy and matplotlib
- Music theory principles from various traditions
- Synthesis techniques inspired by classic synthesizers
- Visualization concepts from music theory analysis

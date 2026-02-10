# TypeRacer

A terminal-based typing speed game. Test your WPM right from the command line.

## Install

```bash
pip install git+https://github.com/jw642459986/typeracer.git
```

Or clone and install locally:

```bash
git clone https://github.com/jw642459986/typeracer.git
cd typeracer
pip install .
```

Or install directly from a local path:

```bash
pip3 install --user /path/to/typeracer
```

## Usage

```bash
typeracer
```

## How to Play

- A random passage is displayed — type it as fast and accurately as you can
- Characters turn **green** when correct, **red** when wrong
- **WPM**, **accuracy**, and a **progress bar** update in real time
- Press **Backspace** to correct mistakes
- Press **Escape** to quit
- After finishing, press any key to race again or **Escape** to exit

## Troubleshooting

If `typeracer` isn't found after installing, your Python user bin directory may not be on your PATH:

- **macOS**: `export PATH="$HOME/Library/Python/3.X/bin:$PATH"` (replace `3.X` with your Python version)
- **Linux**: `export PATH="$HOME/.local/bin:$PATH"`

Add the appropriate line to your `~/.zshrc` or `~/.bashrc` to make it permanent.

## Uninstall

```bash
pip uninstall typeracer
```

### Chess AI

A powerful Chess AI leveraging TensorFlow and Stockfish to play and improve at chess through self-play and reinforcement learning.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
  - [Python Installation](#python-installation)
  - [C++ Installation](#c-installation)
- [Usage](#usage)
  - [Python Usage](#python-usage)
  - [C++ Usage](#c-usage)
- [Training](#training)
  - [Python Training](#python-training)
  - [C++ Training](#c-training)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Introduction

This Chess AI project integrates TensorFlow for machine learning and Stockfish, one of the strongest open-source chess engines, to create robust AIs capable of playing and learning chess. Each version uses a different programming language: Python for rapid prototyping and C++ for performance-critical applications.

## Features

- **Neural Network**: Utilizes TensorFlow for Python and a custom-built neural network for C++.
- **Stockfish Integration**: Integrated for both versions to assist in move selection and validation.
- **Self-Play**: AI improves through self-play in both Python and C++ implementations.
- **Attention Mechanism**: Python version incorporates Bahdanau attention mechanism; C++ version focuses on performance enhancements.
- **Hyperparameter Tuning**: Employs Keras Tuner for Python and manual tuning for C++.
- **Data Management**: Python version automatically saves game data; C++ version manages data for analysis and retraining.

## Installation

### Python Installation

#### Prerequisites

- Python 3.6+
- TensorFlow 2.x
- Stockfish engine
- Other dependencies listed in `requirements.txt`

#### Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/germanProgq/Chess_Bot
   cd Chess_Bot
   cd V-Python
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download and set up Stockfish:**
   - Download Stockfish from [official site](https://stockfishchess.org/download/)
   - Place the executable in the `stockfish` folder or specify the path in your code.

### C++ Installation

#### Prerequisites

- C++ compiler supporting C++11
- TensorFlow C++ API
- Stockfish engine
- Additional libraries as listed in `requirements.txt`

#### Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/germanProgq/Chess_Bot
   cd Chess_Bot
   cd V-Cpp
   ```

2. **Build the project:**
   ```bash
   mkdir build
   cd build
   cmake ..
   make
   ```

3. **Download and set up Stockfish:**
   - Download Stockfish from [official site](https://stockfishchess.org/download/)
   - Place the executable in the appropriate folder or specify the path in your code.

## Usage

### Python Usage

#### Playing a Game

To play a game against the AI, run:
```bash
in progress
```

#### Training the AI

To train the AI using self-play and Stockfish, run:
```bash
python bot/chess_bot.py
```

### C++ Usage

#### Playing a Game

To play a game against the AI, run:
```bash
./Chess_Bot_cpp
```

#### Training the AI

Currently in progress...

## Training

### Python Training

The Python training process involves playing multiple games between the AI and Stockfish, collecting data, and using that data to improve the neural network. Key steps include:

1. **Self-Play**: AI plays games against itself or Stockfish to generate training data.
2. **Data Collection**: States, actions, and rewards are saved for each game.
3. **Model Training**: The neural network is trained using the collected data.
4. **Evaluation**: The model is evaluated and improved iteratively.

### C++ Training

Training involves iterative improvement using self-play and reinforcement learning techniques.

## Contributing

We welcome contributions! Here’s how you can help:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature-branch-name`.
3. Make your changes and commit them: `git commit -m 'Add some feature'`.
4. Push to the branch: `git push origin feature-branch-name`.
5. Open a pull request.

Please make sure your contributions adhere to our [code of conduct](CODE_OF_CONDUCT.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Stockfish Chess Engine](https://stockfishchess.org/)
- [TensorFlow](https://www.tensorflow.org/)
- [Keras Tuner](https://keras.io/keras_tuner/)
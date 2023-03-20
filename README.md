# Chess AI
Library of Chess and different custom AIs including neural networks.

## Installation

1. Install pyenv:
   * [Windows](https://github.com/pyenv-win/pyenv-win)
   * [Linux](https://github.com/pyenv/pyenv#automatic-installer)
   * [macOS](https://github.com/pyenv/pyenv#homebrew-in-macos)

2. Install Python using pyenv 

    ```bash
    $ pyenv install 3.11.1
    ```

3. Clone the repositories using git. Make sure to check out the develop branch of both repositories to get the most recent changes.

    ```bash
    $ git clone https://github.com/PeytonMAnderson/ChessAI.git
    ```

4. Create/Activate a Python Virtual Environment

    ```bash
    $ python -m venv .venv

    # windows
    $ ./venv/Scripts/activate

    # unix
    $ ./venv/bin/activate

    # your prompt should change
    (.venv) $
    ```

5. Update pip and install Poetry 

    ```bash
    $ python -m pip install -U pip poetry
    $ poetry install
    ```
    
 6. Add repository as dependency
 
     ```bash
    $ pip install -e .
    ```
 7. Run chess_ai.py in main folder

     ```bash
    $ python chess_ai.py
    ```

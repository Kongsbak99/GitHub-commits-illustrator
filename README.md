# GitHub-commits-illustrator

This tool generates visualizations of GitHub repository commit graphs. It uses the GitHub GraphQL API to fetch commit data and Graphviz to generate the visual graph.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.7 or higher
- Git installed on your machine
- A GitHub account and a personal access token to use with the GitHub API
- Graphviz installed on your system for generating graph images
        https://graphviz.org/download/
    ! ! ! Choose "add graphviz to PATH" when installing ! ! !


## Installation

Before running the GitHub Graph Illustrator, install the requirements.txt file as such:

    pip install -r requirements.txt

Or

    pip install --user -r requirements.txt

## Usage

The script should now be able to run on it's own. If you do not specify an access token in your environment variables, you will be prompted to enter into the terminal.


## Testing
To run tests, you would execute the following command in your terminal:

    python -m unittest _test.py

or configure your IDE to run them, pending on your specific IDE of choice. 
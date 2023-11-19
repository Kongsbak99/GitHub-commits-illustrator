import os
import sys
from dotenv import load_dotenv

load_dotenv()

from utils import Utils


def main(repo_name: str, owner: str, token: str):
    client = Utils.setup_graphql_client(token)
    commits = Utils.fetch_commits(client, repo_name, owner)
    graph, nodes = Utils.build_graph(commits)

    if Utils.verify_acyclic(graph, nodes):
        graph.write_dot('commit_graph.dot')
        graph.write_png('commit_graph.png')
        print("Graph generated successfully.")
    else:
        print("Error: The commit graph is not acyclic.")



if __name__ == "__main__":
    # 7-solitaire
    # Kongsbak99

    test = os.getenv('TEST')
    token = os.getenv('ACCESS_TOKEN')

    print('Welcome to the commit graph generator!')
    repo_name = input('Please enter the name of the repository: ')
    owner = input('Please enter the owner of the repository: ')

    if token == None:
        q = input('No token found in environment. Do you want to enter it manually? (y/n)')
        if q == 'y':
            token = input('Please enter your GitHub Personal Access Token: ')
        else:
            print('Exiting...')
            sys.exit()

    
    

    main(repo_name, owner, token)

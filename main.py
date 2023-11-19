import os
import sys
from dotenv import load_dotenv

from service import Service


load_dotenv()



def main(repo_name: str, owner: str, token: str, truncation: str):
    truncation_bool = True if truncation == 'y' else False
    s = Service(token, repo_name, owner, truncation_bool)
    client = s.getClient()
    commits = s.fetchCommits(client)
    graph, nodes = s.buildGraph(commits)

    if s.verifyAcyclic(graph, nodes):
        graph.write_dot('images/commit_graph.dot')
        graph.write_png('images/commit_graph.png')
        print("Graph generated successfully.")
    else:
        print("Error: The commit graph is not acyclic.")



if __name__ == "__main__":
    
    print('Welcome to the commit graph generator!')
    token = os.getenv('ACCESS_TOKEN')
    repo_name = input('Please enter the name of the repository: ')
    owner = input('Please enter the owner of the repository: ')

    if token == None:
        q = input('No token found in environment. Do you want to enter it manually? (y/n)')
        if q == 'y':
            print('Please enter your GitHub Personal Access Token: ')
            token = input()
        else:
            print('Exiting...')
            sys.exit()
    else:
        print('Token found in environment. Using it...')

    #trucation = input('Do you want to truncate the commit messages of the graph? (y/n)')
    
    

    main(repo_name, owner, token, truncation=True)


    print('Finished successfully.')

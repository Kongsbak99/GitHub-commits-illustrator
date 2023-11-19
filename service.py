from typing import List, Dict, Tuple
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import pydot
from gql.transport.exceptions import TransportServerError


class Service:
    def __init__(self, token: str, repo_name: str, owner: str, truncation: bool) -> None:
        self.token = token
        self.repo_name = repo_name
        self.owner = owner
        self.truncation = truncation


    def getClient(self) -> Client:
        try:
            headers = {
                "Authorization": f"Bearer {self.token}"
            }
            transport = RequestsHTTPTransport(url='https://api.github.com/graphql', use_json=True, headers=headers)
            return Client(transport=transport, fetch_schema_from_transport=True)
        
        except Exception as e:
            print("Error: ", e)
            raise e


    def fetchCommits(self, client: Client) -> List[Dict]:
        try:
            # Build the GraphQL query
            query = gql("""
                query GetCommits($repoName: String!, $owner: String!) {
                    repository(name: $repoName, owner: $owner) {
                        defaultBranchRef {
                            target {
                                ... on Commit {
                                    history(first: 100) {
                                        nodes {
                                            oid
                                            message
                                            parents(first: 10) {
                                                nodes {
                                                    oid
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            """)

            params = {
                "repoName": self.repo_name,
                "owner": self.owner
            }
            
            response = client.execute(query, variable_values=params)['repository']['defaultBranchRef']['target']['history']['nodes']
            return response
        
        except TransportServerError as e:
            exception = e
            test = e.code
            if e.code == 401:
                print("TransportServerError: Invalid token.")
                q = input('Do you want to retry with another token? (y/n)')
                if q == 'y':
                    self.token = input('Please re-enter your GitHub Personal Access Token to: ')
                    self.client = self.getClient()
                    response = self.fetchCommits(self.client)
                    return response
                else: 
                    print("Exiting...")
                    raise e
            else:
                print("TransportServerError: ", e)
                raise e
        except Exception as e:
            print("Error: ", e)
            raise e
        


    def buildGraph(self, commits: List[Dict]) -> Tuple[pydot.Dot, Dict[str, pydot.Node]]:
        
        # Create a new graph
        graph = pydot.Dot(graph_type='digraph')
        nodes = {}

        # First, create nodes for all commits
        for commit in commits:
            #message =  commit['oid'], label=commit['message'][:30] + '...'
            #message2 = commit['oid'], label=commit['message']
            # Truncation needs to be implemented, otherwise error will be thrown. 
            # TODO Add functionality for non-truncation results if possible.
            node = pydot.Node(commit['oid'], label=commit['message'][:30] + '...')
            nodes[commit['oid']] = node

        # Then, create edges between commits and their parents
        for commit in commits:
            node = nodes[commit['oid']]
            graph.add_node(node)
            for parent in commit.get('parents', {}).get('nodes', []):
                parent_oid = parent['oid']
                # Check if the parent commit has already been added to the graph
                if parent_oid not in nodes:
                    # If not, create a new node for it
                    parent_node = pydot.Node(parent_oid)
                    nodes[parent_oid] = parent_node
                    graph.add_node(parent_node)
                # Create an edge from the parent to the child
                graph.add_edge(pydot.Edge(nodes[parent_oid], node))

        return graph, nodes


    def verifyAcyclic(self, graph: pydot.Dot, nodes: Dict[str, pydot.Node]) -> bool:
        # Check if the graph is acyclic
        visited = set()
        stack = set()

        def dfs(node_id: str) -> bool:
            if node_id in stack:
                return False
            if node_id in visited:
                return True

            visited.add(node_id)
            stack.add(node_id)

            for edge in graph.get_edges():
                src, dst = edge.get_source(), edge.get_destination()
                if src == node_id and not dfs(dst):
                    return False

            stack.remove(node_id)
            return True

        return all(dfs(node.get_name()) for node in nodes.values())
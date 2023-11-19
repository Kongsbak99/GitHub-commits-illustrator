import os
import sys
from typing import List, Dict, Set, Tuple

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import pydot


class Utils:

    def setup_graphql_client(token: str) -> Client:
        """Set up the GraphQL client with authorization token."""
        headers = {
            "Authorization": f"Bearer {token}"
        }
        transport = RequestsHTTPTransport(url='https://api.github.com/graphql', use_json=True, headers=headers)
        return Client(transport=transport, fetch_schema_from_transport=True)



    def fetch_commits(client: Client, repo_name: str, owner: str) -> List[Dict]:
        """Fetch commit data from GitHub API."""
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
            "repoName": repo_name,
            "owner": owner
        }

        return client.execute(query, variable_values=params)['repository']['defaultBranchRef']['target']['history']['nodes']


    def build_graph(commits: List[Dict]) -> Tuple[pydot.Dot, Dict[str, pydot.Node]]:
        """Build a graph from commit data."""
        graph = pydot.Dot(graph_type='digraph')
        nodes = {}

        # First, create nodes for all commits
        for commit in commits:
            node = pydot.Node(commit['oid'], label=commit['message'][:30] + '...')  # Truncate long messages
            nodes[commit['oid']] = node

        # Then, add nodes to the graph and create edges for their parents
        for commit in commits:
            node = nodes[commit['oid']]
            graph.add_node(node)
            for parent in commit.get('parents', {}).get('nodes', []):
                parent_oid = parent['oid']
                # Ensure that a node for each parent commit exists before creating an edge
                if parent_oid not in nodes:
                    # Create a node for the parent commit if it doesn't exist
                    parent_node = pydot.Node(parent_oid)
                    nodes[parent_oid] = parent_node
                    graph.add_node(parent_node)
                # Now that we're sure the parent node exists, create the edge
                graph.add_edge(pydot.Edge(nodes[parent_oid], node))

        return graph, nodes


    def verify_acyclic(graph: pydot.Dot, nodes: Dict[str, pydot.Node]) -> bool:
        """Verify that the commit graph is acyclic."""
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
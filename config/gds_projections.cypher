// Neo4j Graph Data Science (GDS) Cypher Procedures

// 1. Drop existing in-memory GDS projection if present
CALL gds.graph.drop('fingraph-projection', false);

// 2. Project account transaction graph into GDS memory
CALL gds.graph.project(
  'fingraph-projection',
  'Account',
  {
    TRANSFERRED_TO: {
      type: 'TRANSFERRED_TO',
      orientation: 'NATURAL',
      properties: 'amount'
    }
  }
);

// 3. Run PageRank to calculate node centrality score
CALL gds.pageRank.write('fingraph-projection', {
  maxIterations: 20,
  dampingFactor: 0.85,
  writeProperty: 'pagerank'
});

// 4. Run Weakly Connected Components (WCC) to group disconnected subgraphs
CALL gds.wcc.write('fingraph-projection', {
  writeProperty: 'componentId'
});

// 5. Run Louvain Community Detection to discover tight financial communities
CALL gds.louvain.write('fingraph-projection', {
  includeIntermediateCommunities: false,
  writeProperty: 'communityId'
});

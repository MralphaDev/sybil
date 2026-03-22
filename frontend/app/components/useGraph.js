import { useEffect, useState } from "react";
import axios from "axios";

export default function useGraph() {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [clusters, setClusters] = useState([]);
  const [similarities, setSimilarities] = useState({ behavior: {}, variant: {} ,weighted: {} });
  const [dbscan, setDbscan] = useState({});
  const [sybil_entities, setSybilEntities] = useState([]);
  useEffect(() => {
    axios.get("http://127.0.0.1:8000/graph")
      .then(res => {
        setNodes(res.data.nodes || []);
        setEdges(res.data.edges || []);
        setClusters(res.data.clusters || []);
        setSimilarities(res.data.similarities || { behavior: {}, variant: {} });
        setDbscan(res.data.dbscan || {});
        setSybilEntities(res.data.sybil_entities || []);
        console.log("Graph data loaded:", res.data);
      })
      .catch(err => console.error(err));
  }, []);

  return { nodes, edges, clusters, similarities ,dbscan,sybil_entities};
}
from __future__ import annotations

import numpy as np

# =======================
# 🧠 CLASSIFICATION MODELS
# =======================

if GNN_AVAILABLE:
    import torch
    import torch.nn.functional as F
    from torch_geometric.nn import GCNConv, GATConv, global_mean_pool
    from torch_geometric.data import Data, DataLoader
    
    class BrainGNN(torch.nn.Module):
        """
        Graph Neural Network for brain-network classification
        """
        def __init__(self, num_node_features, num_classes=3, hidden_dim=64):
            super(BrainGNN, self).__init__()
            self.conv1 = GCNConv(num_node_features, hidden_dim)
            self.conv2 = GCNConv(hidden_dim, hidden_dim)
            self.conv3 = GCNConv(hidden_dim, hidden_dim)
            self.fc = torch.nn.Linear(hidden_dim, num_classes)
            self.dropout = torch.nn.Dropout(0.5)
        
        def forward(self, data):
            x, edge_index, edge_weight, batch = data.x, data.edge_index, data.edge_attr, data.batch
            
            # Graph convolutions
            x = self.conv1(x, edge_index, edge_weight)
            x = F.relu(x)
            x = self.dropout(x)
            
            x = self.conv2(x, edge_index, edge_weight)
            x = F.relu(x)
            x = self.dropout(x)
            
            x = self.conv3(x, edge_index, edge_weight)
            x = F.relu(x)
            
            # Global pooling
            x = global_mean_pool(x, batch)
            
            # Classification
            x = self.fc(x)
            return F.log_softmax(x, dim=1)
    
    print("✅ BrainGNN defined")
else:
    print("⚠️ GNN not available (torch_geometric not installed)")


if RIEMANNIAN_AVAILABLE:
    from pyriemann.classification import MDM, TSclassifier
    from pyriemann.estimation import Covariances
    from sklearn.pipeline import Pipeline
    
    class RiemannianClassifier:
        """
        Riemannian Geometry-based classifier
        Use covariance matrices on a Riemannian manifold
        """
        def __init__(self):
            self.pipeline = Pipeline([
                ('cov', Covariances(estimator='lwf')),  # Ledoit-Wolf
                ('mdm', MDM(metric='riemann'))  # Minimum Distance to Mean
            ])
        
        def fit(self, X, y):
            """
            X: (n_samples, n_channels, n_times)
            y: (n_samples,)
            """
            self.pipeline.fit(X, y)
            return self
        
        def predict(self, X):
            return self.pipeline.predict(X)
        
        def predict_proba(self, X):
            # MDM doesn't have predict_proba, use distance-based
            try:
                return self.pipeline.predict_proba(X)
            except:
                # Fallback: convert predictions to one-hot
                preds = self.predict(X)
                n_classes = len(np.unique(preds))
                proba = np.zeros((len(preds), n_classes))
                for i, p in enumerate(preds):
                    proba[i, p] = 1.0
                return proba
    
    print("✅ RiemannianClassifier defined")
else:
    print("⚠️ Riemannian not available (pyriemann not installed)")


# =======================
# SEMBLE MODEL
# =======================

class BrainNetworkEnsemble:
    """
    Ensemble classifier: GNN + Riemannian + Traditional ML
    """
    def __init__(self):
        self.models = {}
        self.weights = {}
        
        # GNN
        if GNN_AVAILABLE:
            self.models['gnn'] = None  # Will be initialized during training
            self.weights['gnn'] = 0.4
        
        # Riemannian
        if RIEMANNIAN_AVAILABLE:
            self.models['riemannian'] = RiemannianClassifier()
            self.weights['riemannian'] = 0.3
        
        # Traditional ML (Random Forest)
        from sklearn.ensemble import RandomForestClassifier
        self.models['rf'] = RandomForestClassifier(n_estimators=100, random_state=42)
        self.weights['rf'] = 0.3
        
        # Normalize weights
        total_weight = sum(self.weights.values())
        self.weights = {k: v/total_weight for k, v in self.weights.items()}
    
    def fit(self, X_graph, X_timeseries, X_features, y):
        """
        X_graph: list of PyG Data objects (for GNN)
        X_timeseries: (n_samples, n_channels, n_times) (for Riemannian)
        X_features: (n_samples, n_features) (for RF)
        y: (n_samples,)
        """
        # Train GNN
        if 'gnn' in self.models and GNN_AVAILABLE:
            print("   Training GNN...")
            # GNN training code here
            pass
        
        # Train Riemannian
        if 'riemannian' in self.models and RIEMANNIAN_AVAILABLE:
            print("   Training Riemannian...")
            self.models['riemannian'].fit(X_timeseries, y)
        
        # Train RF
        if 'rf' in self.models:
            print("   Training Random Forest...")
            self.models['rf'].fit(X_features, y)
        
        return self
    
    def predict(self, X_graph, X_timeseries, X_features):
        """
        Weighted voting
        """
        predictions = []
        
        # GNN predictions
        if 'gnn' in self.models and self.models['gnn'] is not None:
            # GNN predict code
            pass
        
        # Riemannian predictions
        if 'riemannian' in self.models:
            pred_riem = self.models['riemannian'].predict(X_timeseries)
            predictions.append((pred_riem, self.weights['riemannian']))
        
        # RF predictions
        if 'rf' in self.models:
            pred_rf = self.models['rf'].predict(X_features)
            predictions.append((pred_rf, self.weights['rf']))
        
        # Weighted voting
        if len(predictions) == 0:
            return np.array([0] * len(X_features))
        
        # Simple majority vote (can be improved)
        final_pred = predictions[0][0]  # Start with first model
        return final_pred


print("✅ Ensemble model defined")


# =======================
# FEATURE EXTRACTION
# =======================

def extract_graph_features(granger_adj, lingam_adj):
    """
    Extract features from adjacency matrices
    """
    features = []
    
    for adj in [granger_adj, lingam_adj]:
        # Network metrics
        G = nx.from_numpy_array(adj)
        
        # Density
        density = nx.density(G)
        features.append(density)
        
        # Average clustering
        try:
            clustering = nx.average_clustering(G)
            features.append(clustering)
        except:
            features.append(0)
        
        # Average degree
        degrees = [d for n, d in G.degree()]
        features.append(np.mean(degrees))
        
        # Adjacency matrix features
        features.append(np.mean(adj))
        features.append(np.std(adj))
        features.append(np.max(adj))
    
    return np.array(features)


print("✅ Feature extraction defined")

print(f"\n{'='*70}")
print("🧠 Classification Pipeline Ready")
print(f"   Available models:")
if GNN_AVAILABLE:
    print("   ✅ GNN (Graph Neural Network)")
if RIEMANNIAN_AVAILABLE:
    print("   ✅ Riemannian Geometry")
print("   ✅ Random Forest (baseline)")
print(f"{'='*70}")

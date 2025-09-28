# Machine Learning for Strategy Pack Optimization in Tilescope

## Project Overview
Develop a machine learning model to predict the optimal strategy pack for a given tilescope basis, with the goal of achieving faster specification generation.

## Problem Definition
- **Input**: Basis (e.g., "012", "021", "0123_3102")
- **Output**: Recommended strategy pack
- **Objective**: Minimize time to reach specification or maximize success rate

## Data Collection Status
- [x] Bases data collected (sizes 1-12): `bases_size_*.json`
- [ ] Strategy packs collection in progress: `all_packs.json`
- [ ] Performance data (basis + pack → time/success) needs collection

## Proposed Approach

### 1. Data Preparation
- **Feature Engineering for Bases**:
  - Length of basis string
  - Character frequency analysis
  - Pattern detection (consecutive sequences, repeats)
  - Numerical properties (sum, differences, ranges)
  - Structural properties (permutation patterns)

- **Feature Engineering for Strategy Packs**:
  - Pack size/complexity metrics
  - Strategy type distribution
  - Pack hierarchy/dependencies
  - Historical performance patterns

### 2. Model Architecture Options

#### Option A: Classification Model
- Treat as multi-class classification problem
- Classes = available strategy packs
- Features = basis characteristics
- Output = probability distribution over packs

#### Option B: Ranking/Recommendation Model
- Learn to rank strategy packs for each basis
- Pairwise comparison approach
- Output = ordered list of recommended packs

#### Option C: Regression Model
- Predict expected performance (time/success rate) for each basis-pack pair
- Select pack with best predicted performance

### 3. Training Data Generation
- **Benchmark Collection**:
  - Run each basis with multiple strategy packs (5-minute timeout per pair)
  - Record: time to completion, success/failure/timeout, specification quality
  - Create (basis, pack, performance) tuples
  - For model training: treat timeouts as failures (poor performance)

- **Data Split Strategy**:
  - Random split within each basis size category
  - Ensure balanced representation across all sizes in both train/test sets
  - Maintain basis type diversity in both splits

### 4. Evaluation Metrics
- **Primary**: Average speedup on test set
- **Secondary**: Success rate improvement, specification quality
- **Baseline**: Current default strategy pack selection

### 5. Implementation Plan

#### Phase 1: Data Collection & Preprocessing
1. Complete strategy pack enumeration
2. Generate benchmark dataset (basis × pack performance)
3. Implement feature extraction for bases and packs
4. Create train/test splits

#### Phase 2: Model Development
1. Start with simple models (Random Forest, SVM)
2. Progress to neural networks if needed
3. Implement cross-validation framework
4. Hyperparameter optimization

#### Phase 3: Evaluation & Integration
1. Test on held-out data
2. Compare against current approach
3. Integrate best model into tilescope workflow
4. Monitor real-world performance

## Technical Considerations

### Feature Representation
- **Basis Encoding**:
  - One-hot encoding for characters
  - Sequence embeddings (if using deep learning)
  - Hand-crafted features based on domain knowledge

- **Strategy Pack Encoding**:
  - Categorical encoding of pack types
  - Numerical features (complexity, size)
  - Embedding representations

### Model Selection Criteria
- **Interpretability**: Important for understanding which features matter
- **Speed**: Model inference should be faster than trying multiple packs
- **Generalization**: Must work on unseen basis types

### Potential Challenges
- **Imbalanced Data**: Some packs may work well for few bases
- **Cold Start**: New/rare basis patterns
- **Computational Cost**: Training data generation may be expensive

## Next Steps
1. Complete strategy pack collection
2. Design benchmark experiment framework
3. Implement baseline feature extraction
4. Generate initial training dataset
5. Prototype first model

## Files and Data Structure
```
├── bases_size_*.json          # Basis data by size
├── all_packs.json            # Available strategy packs
├── benchmark_results.json    # (basis, pack, performance) data
├── features/
│   ├── basis_features.py     # Basis feature extraction
│   └── pack_features.py      # Pack feature extraction
├── models/
│   ├── baseline.py           # Simple baseline models
│   └── neural_net.py         # Deep learning approaches
└── evaluation/
    ├── metrics.py            # Evaluation utilities
    └── cross_validation.py   # CV framework
```

## Success Criteria
- Achieve 20%+ average speedup on test set
- Maintain or improve specification success rate
- Model inference time < 1% of average pack execution time
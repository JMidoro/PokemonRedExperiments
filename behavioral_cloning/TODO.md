# Behavioral Cloning Implementation Plan

## Overview
This project aims to create a behavioral cloning system that mirrors the existing Deep RL environment for Pokemon Red. You can see the current  The goal is to enable training AI agents from human gameplay data while maintaining compatibility with the existing RL infrastructure.

## Key Requirements
- Maintain identical environment configuration with RL setup
- Use `extra_buttons=True` for both human and AI players
- Enable seamless weight transfer between BC and RL models (future work)

## Implementation Status

### 1. Environment Setup (DONE)
- [x] Create `RedGymEnvHuman` class extending base environment
- [x] Configure for human play (non-headless mode)
- [x] Add recording controls (R, P, E, Q)
- [x] Create data collection script

### 2. Data Collection System (DONE)
- [x] Implement episode recording functionality
- [x] Setup structured data storage format
- [x] Add metadata tracking
- [x] Create user interface for recording control

### 3. Training Pipeline (TODO)
- [ ] Create training script `train_behavioral_cloning.py`
- [ ] Implement data loading pipeline
  - [ ] Batch generation from recorded episodes
  - [ ] Data augmentation if needed
  - [ ] Train/validation split functionality
- [ ] Setup network architecture
  - [ ] Reuse architecture from RL agent
  - [ ] Modify for supervised learning
- [ ] Implement training loop
  - [ ] Cross-entropy loss for action prediction
  - [ ] Validation metrics
  - [ ] Early stopping
  - [ ] Model checkpointing
- [ ] Add TensorBoard logging
  - [ ] Loss curves
  - [ ] Accuracy metrics
  - [ ] Action distribution visualization

### 4. Evaluation Tools (TODO)
- [ ] Create evaluation script
- [ ] Implement metrics:
  - [ ] Action prediction accuracy
  - [ ] Reward comparison with RL agent
  - [ ] Behavioral similarity metrics
- [ ] Add visualization tools:
  - [ ] Action distribution comparison
  - [ ] State visitation heatmaps
  - [ ] Side-by-side gameplay videos

### 5. Weight Transfer Utilities (Future Work)
- [ ] Create weight extraction tools
- [ ] Implement weight merging functionality
- [ ] Add initialization options for RL from BC weights
- [ ] Support mixed training experiments

## Testing Status

### Environment & Data Collection
- [ ] Test basic environment functionality
- [ ] Verify data recording and storage
- [ ] Test keyboard controls
- [ ] Validate saved data format
- [ ] Check memory usage during long sessions

### Training Pipeline (TODO)
- [ ] Test data loading performance
- [ ] Verify loss computation
- [ ] Check training stability
- [ ] Validate model saving/loading
- [ ] Test TensorBoard integration

## Notes
- Current focus is on completing and testing the data collection system
- Training pipeline will reuse much of the existing RL infrastructure
- Need to ensure data format is efficient for training
- Consider adding data validation tools
- May need to implement frame skipping for human play comfort

## Dependencies
- Added: keyboard package for recording controls
- Existing: PyBoy, stable-baselines3, gym, etc.

## Directory Structure
```
behavioral_cloning/
├── red_gym_env_human.py    # Human-playable environment
├── collect_human_data.py   # Data collection script
├── TODO.md                 # This file
├── data/                   # Recorded gameplay data
│   └── ep_[NUMBER]_[UUID]/
│       ├── metadata.json   # Episode metadata
│       └── trajectory.npz  # State-action data
└── sessions/              # Session data (states, etc.)

import json
import numpy as np
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
import uuid
from datetime import datetime

# Add parent directory to Python path for imports
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / 'v2'))

from pyboy.utils import WindowEvent
from v2.red_gym_env_v2 import RedGymEnv

class RedGymEnvHuman(RedGymEnv):
    """
    Extension of RedGymEnv for human gameplay and data collection.
    Adds recording controls and configures for interactive (non-headless) mode.
    
    Recording Controls:
    - R: Start Recording
    - P: Pause Recording
    - E: End current episode
    - Q: Quit session
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        # Force non-headless mode for human play
        if config is None:
            config = {}
        config['headless'] = False
        
        # Add extra buttons for compatibility with RL setup
        self.extra_buttons = True
        
        # Initialize recording state
        self.is_recording = False
        self.recorded_data = []
        self.current_episode = []
        
        # Add recording control keys
        # We'll use STATE_SAVE for recording start (R)
        # STATE_LOAD for recording pause (P)
        # SCREEN_RECORDING_TOGGLE for episode end (E)
        # QUIT remains QUIT (Q)
        self.recording_controls = {
            WindowEvent.STATE_SAVE: self._start_recording,
            WindowEvent.STATE_LOAD: self._pause_recording,
            WindowEvent.SCREEN_RECORDING_TOGGLE: self._end_episode,
            WindowEvent.QUIT: self._quit_session
        }
        
        # Override events.json path to use v2 directory
        self._events_json_path = root_dir / 'v2' / 'events.json'
        
        # Initialize episode metadata
        self.episode_metadata = {
            'episode_id': None,
            'start_time': None,
            'end_time': None,
            'total_steps': 0,
            'total_rewards': 0,
            'game_stats': []
        }
        
        # Call parent init
        super().__init__(config)
        
        # Load event names after parent init (override the relative path load)
        with open(self._events_json_path) as f:
            self.event_names = json.load(f)
    
    def _start_recording(self):
        """Start or resume recording gameplay."""
        if not self.is_recording:
            self.is_recording = True
            # Initialize new episode if needed
            if not self.episode_metadata['episode_id']:
                self._init_new_episode()
            print("Recording started")
            
    def _init_new_episode(self):
        """Initialize a new episode with metadata."""
        self.episode_metadata = {
            'episode_id': str(uuid.uuid4())[:8],
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'total_steps': 0,
            'total_rewards': 0,
            'game_stats': []
        }
        self.current_episode = []
            
    def _pause_recording(self):
        """Pause recording gameplay."""
        if self.is_recording:
            self.is_recording = False
            print("Recording paused")
            
    def _end_episode(self):
        """End current episode and save recorded data."""
        if len(self.current_episode) > 0:
            # Update episode metadata
            self.episode_metadata['end_time'] = datetime.now().isoformat()
            self.episode_metadata['total_steps'] = len(self.current_episode)
            self.episode_metadata['total_rewards'] = sum(step['reward'] for step in self.current_episode)
            
            # Create episode data structure
            episode_data = {
                'metadata': self.episode_metadata,
                'trajectory': self.current_episode
            }
            
            # Save episode to file
            episode_path = self.s_path / 'episodes'
            episode_path.mkdir(exist_ok=True)
            episode_file = episode_path / f"episode_{self.episode_metadata['episode_id']}.json"
            
            with open(episode_file, 'w') as f:
                json.dump(episode_data, f, indent=2)
            
            print(f"Episode saved to {episode_file}")
            
            # Reset episode data
            self.recorded_data.append(episode_data)
            self.current_episode = []
            self.episode_metadata['episode_id'] = None
        
        self.is_recording = False
            
    def _quit_session(self):
        """End session and save all recorded data."""
        self._end_episode()  # Save current episode if any
        
        if len(self.recorded_data) > 0:
            # Save session summary
            session_summary = {
                'session_id': self.instance_id,
                'total_episodes': len(self.recorded_data),
                'total_steps': sum(ep['metadata']['total_steps'] for ep in self.recorded_data),
                'total_rewards': sum(ep['metadata']['total_rewards'] for ep in self.recorded_data),
                'episodes': self.recorded_data
            }
            
            summary_path = self.s_path / "session_summary.json"
            with open(summary_path, 'w') as f:
                json.dump(session_summary, f, indent=2)
            print(f"Session summary saved to {summary_path}")
        
        return True
        
    def step(self, action):
        """
        Override step to handle human input and record state-action pairs during gameplay.
        The action parameter is ignored as we'll get input directly from PyBoy.
        """
        # Get the observation before any action
        obs = self._get_obs()
        
        # Let PyBoy handle input and tick the emulator
        render_screen = self.save_video or not self.headless
        self.pyboy.tick(self.act_freq, render_screen)
        
        # Check for recording control inputs
        for event in [WindowEvent.STATE_SAVE, WindowEvent.STATE_LOAD, 
                     WindowEvent.SCREEN_RECORDING_TOGGLE, WindowEvent.QUIT]:
            try:
                if self.pyboy.send_input(event):
                    handler = self.recording_controls.get(event)
                    if handler and handler():  # If _quit_session returns True
                        return None, 0, True, False, {}
            except:
                # If send_input fails, just continue
                pass
        
        # Get the new observation and other info
        new_obs = self._get_obs()
        reward = self.update_reward()
        terminated = False
        truncated = self.check_if_done()
        
        if self.is_recording:
            # Get current game state
            x_pos, y_pos, map_n = self.get_game_coords()
            levels = [self.read_m(a) for a in [0xD18C, 0xD1B8, 0xD1E4, 0xD210, 0xD23C, 0xD268]]
            
            # Record detailed game state
            game_state = {
                'step': len(self.current_episode),
                'x': x_pos,
                'y': y_pos,
                'map': map_n,
                'max_map_progress': self.max_map_progress,
                'action': action,
                'pokemon_count': self.read_m(0xD163),
                'levels': levels,
                'levels_sum': sum(levels),
                'party_types': self.read_party(),
                'hp': self.read_hp_fraction(),
                'badges': self.get_badges(),
                'event_progress': self.progress_reward.get('event', 0)
            }
            
            # Update episode metadata
            self.episode_metadata['game_stats'].append(game_state)
            
            # Record state-action pair
            self.current_episode.append({
                'observation': obs,  # Record the observation BEFORE the action
                'action': action,
                'reward': reward,
                'terminated': terminated,
                'truncated': truncated,
                'info': {},
                'game_state': game_state,
                'next_observation': new_obs  # Also record the resulting observation
            })
        
        self.step_count += 1
        return new_obs, reward, terminated, truncated, {}
    
    def reset(self, seed=None, options=None):
        """
        Override reset to handle episode boundaries in recording.
        """
        if len(self.current_episode) > 0:
            self._end_episode()
        
        return super().reset(seed=seed, options=options)

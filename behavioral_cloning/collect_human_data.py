from pathlib import Path
import uuid

from red_gym_env_human import RedGymEnvHuman

def main():
    # Create session path
    sess_path = Path(f'human_session_{str(uuid.uuid4())[:8]}')
    
    # Configure environment
    env_config = {
        'save_final_state': True,
        'early_stop': False,
        'action_freq': 24,
        'init_state': '../has_pokedex_nballs.state',
        'max_steps': 2**23,  # Very large number for human play
        'print_rewards': True,
        'save_video': True,  # Save video for analysis
        'fast_video': False,  # Normal speed for human play
        'session_path': sess_path,
        'gb_path': '../PokemonRed.gb',
        'debug': True,  # Enable debug for better feedback
    }
    
    # Create and run environment
    env = RedGymEnvHuman(env_config)
    observation, info = env.reset()
    
    print("\nWelcome to Pokemon Red Human Data Collection!")
    print("\nGame Controls:")
    print("- Arrow Keys: Movement")
    print("- A/B/Start: Game controls")
    print("\nRecording Controls:")
    print("- F5: Start Recording (save state key)")
    print("- F6: Pause Recording (load state key)")
    print("- F10: End current episode (screen recording key)")
    print("- Esc: Quit session")
    
    terminated = truncated = False
    while not (terminated or truncated):
        # Let the environment handle input and recording
        observation, reward, terminated, truncated, info = env.step(None)
        
        if terminated or truncated:
            observation, info = env.reset()

if __name__ == "__main__":
    main()

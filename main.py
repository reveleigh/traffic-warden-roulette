import pygame
import sys
import datetime # For game calendar
from game_map import Map, LANDMARKS  # Import the Map class and Landmark definitions
from sprites import Player, Warden
import database  # Import database module to handle high scores
import random
import math

# --- Configuration ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 720 
FPS = 60

# Colour Definitions (R, G, B)
COLOUR_BG = (30, 30, 40)    # Dark slate grey background colour for empty areas
COLOUR_TEXT = (255, 255, 255) # Standard White text

def main():
    """
    Main entry point for the game.
    Initializes Pygame, states, and the core loop.
    """
    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
    except Exception as e:
        print(f"Directory Error: {e}")

    pygame.init()
    
    # Initialise Database
    database.init_db()
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Traffic Warden Roulette")
    clock = pygame.time.Clock()

    # Audio Init
    busted_sfx = None
    busted_channel = None # Track audio channel
    coin_sfx = None
    blip_sfx = None
    try:
        pygame.mixer.init()
        # Load Splash Music
        pygame.mixer.music.load("assets/sounds/You_cant_park_there.mp3")
        pygame.mixer.music.set_volume(0.5) 
        pygame.mixer.music.play(-1) 
        
        # Load SFX
        busted_sfx = pygame.mixer.Sound("assets/sounds/busted.mp3")
        busted_sfx.set_volume(1.0)
        
        coin_sfx = pygame.mixer.Sound("assets/sounds/coin.mp3")
        coin_sfx.set_volume(0.8)
        
        blip_sfx = pygame.mixer.Sound("assets/sounds/blip.mp3")
        blip_sfx.set_volume(0.8)
        
        pay_sfx = pygame.mixer.Sound("assets/sounds/pay.mp3")
        pay_sfx.set_volume(1.0)
        
        risk_sfx = pygame.mixer.Sound("assets/sounds/risk.mp3")
        risk_sfx.set_volume(1.0)
    except Exception as e:
        print(f"Audio Error: {e}")


    # Initialise Game Objects
    game_map = Map()
    player = Player(0, 0)
    warden = Warden(19, 14)
    
    # Load Splash Assets
    splash_bg = None
    splash_bg = None
    splash_sign = None
    try:
        splash_bg = pygame.image.load("assets/images/cotswold_splash_clear.png").convert()
        splash_bg = pygame.transform.scale(splash_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except (FileNotFoundError, pygame.error):
        print("Splash background not found.")

    instructions_bg = None
    try:
        instructions_bg = pygame.image.load("assets/images/ciren.png").convert()
        instructions_bg = pygame.transform.scale(instructions_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        instructions_bg.set_alpha(150) # Transparency
    except (FileNotFoundError, pygame.error):
        print("Instructions background not found.")

    # Cutscene Assets
    cutscene_bg = None
    cutscene_van = None
    cutscene_warden = None
    
    try:
        cutscene_bg = pygame.image.load("assets/images/cutscene_bg.png").convert()
        cutscene_bg = pygame.transform.scale(cutscene_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except (FileNotFoundError, pygame.error):
        print("Cutscene BG not found, using fallback.")

    try:
        cutscene_van = pygame.image.load("assets/images/rupert_car.png").convert_alpha()
        cutscene_van = pygame.transform.scale(cutscene_van, (750, 500)) 
    except (FileNotFoundError, pygame.error):
        print("Cutscene Van not found.")

    try:
        cutscene_warden = pygame.image.load("assets/images/cutscene_warden.png").convert_alpha()
        cutscene_warden = pygame.transform.scale(cutscene_warden, (150, 300))
    except (FileNotFoundError, pygame.error):
        print("Cutscene Warden not found.")
    
    # UI Settings
    MAP_OFFSET_Y = 90 

    # Game State Variables
    money = 0.00
    current_date = datetime.date(2024, 1, 1)
    end_date = datetime.date(2024, 12, 31)
    
    # Logic Levels (Integers)
    reward_level = 0 # 0-10+
    fine_level = 0   # 0-5+
    
    # Enum for States
    STATE_SPLASH = -2
    STATE_INSTRUCTIONS = -1
    STATE_RUNNING = 0
    STATE_MISSION_POPUP = 1
    STATE_ACTIVITY = 2
    STATE_GAME_OVER = 3
    STATE_NAME_INPUT = 4
    STATE_LEADERBOARD = 5
    STATE_BUSTED_CUTSCENE = 6
    STATE_WARDEN_RAGE = 7
    # STATE_GUILT_MODE = 8 # Removed, now a flag
    
    current_state = STATE_SPLASH # Start at Splash
    
    game_message = ""
    message_timer = 0
    
    # Feedback Animation Vars
    feedback_active = False
    feedback_timer = 0
    feedback_text = ""
    feedback_color = (255, 255, 255)
    
    # Cutscene Vars
    cutscene_timer = 0
    cutscene_van_x = -500
    cutscene_warden_x = 900
    
    # AI Behaviour
    warden_distraction_target = None
    
    # Name Input
    player_name = ""
    leaderboard_scroll_offset = 0
    instructions_scroll_y = 0
    
    # Splash Animation Vars
    splash_car_x = -600 # Start further off-screen left due to larger size
    splash_warden_y = SCREEN_HEIGHT # Start below screen
    splash_warden_x = random.randint(50, SCREEN_WIDTH - 200) # Random X start
    warden_pop_timer = 0
    warden_state = "waiting" # waiting, popping_up, holding, popping_down
    warden_pop_timer = 0
    warden_state = "waiting" # waiting, popping_up, holding, popping_down
    warden_hold_timer = 0
    
    # Ambush Logic
    ambush_active = False
    elite_wardens = [] # List of Warden objects

    # Guilt Mode Logic
    guilt_chance = 0.04 # Starts at 4%
    guilt_mode_active = False # Flag for overlay/mechanic
    pending_guilt_check = False # Deferred check flag

    
    # DEV MODE
    dev_force_st_michaels = False
    
    
    # Mission System
    available_spots = game_map.get_parking_spots()
    if not available_spots: available_spots = [(0,0)]
    
    current_mission_spot = random.choice(available_spots)
    
    # Mission Context
    # Define these variables
    mission_scenario_text = ""
    current_loc_name = ""
    current_task_name = ""
    mission_cost = 0.00
    potential_reward = 0.00 # Placeholder
    
    # Activity Timer
    activity_timer = 0
    activity_duration_max = 0

    def start_new_mission():
        """
        Generates a new random mission with dynamic costs and requirements.
        """
        nonlocal current_mission_spot, mission_cost, potential_reward, activity_duration_max
        nonlocal mission_scenario_text, current_loc_name, current_task_name, activity_timer
        nonlocal warden_distraction_target
        nonlocal dev_force_st_michaels
        
        warden_distraction_target = None
        
        # 1. Select Random Landmark and Spot
        landmark = random.choice(LANDMARKS)
        current_loc_name = landmark['name']
        
        # Get specific parking spot tied to this landmark
        current_mission_spot = game_map.get_landmark_mission_spot(current_loc_name)
        
        if not current_mission_spot:
             # Fallback if specific finding fails (should catch all via map generation guarantees)
             current_mission_spot = random.choice(available_spots)
        
        # --- DEV MODE OVERRIDE ---
        if dev_force_st_michaels:
            # For debugging: Force the destination to always be St Micheals
            for lm in LANDMARKS:
                if "st micheals" in lm['name'].lower():
                    current_loc_name = lm['name']
                    current_mission_spot = game_map.get_landmark_mission_spot(current_loc_name)
                    # Reset generic errand if overwritten
                    if 'tasks' in lm:
                         current_task_name = random.choice(lm['tasks'])
                    break
        
        # 2. Select generic task description
        if 'tasks' in landmark:
            current_task_name = random.choice(landmark['tasks'])
        else:
            current_task_name = "Errand Run"

        
        # Narrative Personalization
        FAMILY_NAMES = ["Ivor", "Fenella", "Clementine", "Rupert", "Uncle Monty", "Auntie Val"]
        
        # Check if task already has a name hardcoded (to avoid double naming)
        has_name = any(name in current_task_name for name in FAMILY_NAMES)
        
        if not has_name:
             target_name = random.choice(FAMILY_NAMES)
             # Chance to format differently: "Task for X" vs "Task (X)"
             if random.random() < 0.7:
                 current_task_name += f" for {target_name}"
             else:
                 current_task_name += f" ({target_name})"

        
        # 4. Calculate Financials
        mission_cost = random.randint(100, 300) / 100.0 # Random Parking Cost between £1.00 - £3.00
        potential_reward = random.uniform(5.00, 15.00) # Potential 'Audacity' saving £5.00 - £15.00
        
        extra_note = ""
        
        # Construct mission briefing
        # Feature: If it is the Weekend (Saturday=5, Sunday=6), Parking is FREE.
        if "st micheals" in current_loc_name.lower():
             if current_date.weekday() >= 5:
                 mission_cost = 0.00
                 extra_note = "\n(FREE PARKING courtesy of Hoard Mgmt)"
        
        
        # 5. Weighted Duration Logic (Difficulty)
        # Missions have different lengths. Longer missions are riskier.
        # Probabilities: Quick (low risk) ~23%, Medium (normal) ~61%, Long (high risk) ~15%
        duration_type = random.choices(['quick', 'medium', 'long'], weights=[3, 8, 2], k=1)[0]
        
        if duration_type == 'quick':
             # 0.5s to 1.25s (at 60 FPS)
             activity_duration_max = random.randint(30, 75)
        elif duration_type == 'medium':
             # 1.5s to 2.5s
             activity_duration_max = random.randint(90, 150)
        else: 
             # 3s to 4.5s
             activity_duration_max = random.randint(180, 270)

        activity_timer = activity_duration_max
        
        # Construct the Mission Briefing String for UI
        mission_scenario_text = f"Errand: {current_task_name}\nLocation: {current_loc_name}\nDuration: {activity_duration_max} mins\nParking Fee: £{mission_cost:.2f}\nAudacity Bonus: £{potential_reward:.2f}{extra_note}"
    
    # Timers
    WARDEN_MOVE_EVENT = pygame.USEREVENT + 1
    warden_move_interval = 400 #ms (20% faster start)
    pygame.time.set_timer(WARDEN_MOVE_EVENT, warden_move_interval) 
    
    DATE_EVENT = pygame.USEREVENT + 2
    pygame.time.set_timer(DATE_EVENT, 250) # Faster days (was 500)
    
    MUSIC_END_EVENT = pygame.USEREVENT + 3

    def reset_game():
        nonlocal money, current_date, current_state, game_message, message_timer
        nonlocal reward_level, fine_level
        nonlocal ambush_active, elite_wardens
        nonlocal warden_move_interval, guilt_chance, guilt_mode_active
        nonlocal feedback_active, feedback_timer, feedback_text, feedback_color
        
        ambush_active = False
        elite_wardens = []
        
        feedback_active = False
        feedback_timer = 0
        
        # Reset Guilt Chance
        guilt_chance = 0.04
        guilt_mode_active = False
        
        money = 1000.00
        current_date = datetime.date(2024, 1, 1)
        player.reset()
        warden.reset()
        game_message = ""
        message_timer = 0
        
        start_new_mission()
        
        # Reset Logic
        reward_level = 0
        fine_level = 0
        
        # Reset Timers/Music just in case
        warden_move_interval = 400
        pygame.time.set_timer(WARDEN_MOVE_EVENT, warden_move_interval)
        pygame.mixer.music.set_endevent(pygame.NOEVENT)


    running = True
    while running:
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # --- DATE UPDATE ---
            elif event.type == DATE_EVENT:
                if current_state in [STATE_RUNNING]:
                     current_date += datetime.timedelta(days=1)
                     if current_date > end_date:
                        current_state = STATE_GAME_OVER
                        game_message = f"YEAR END! Final: £{money:.2f}"
                        try:
                            pygame.mixer.music.load("assets/sounds/i-see-you.mp3")
                            pygame.mixer.music.play(-1)
                        except Exception as e: print(f"Music Error: {e}")

            # --- INPUT HANDLING ---
            elif event.type == pygame.KEYDOWN:
                if current_state == STATE_SPLASH:
                    if event.key == pygame.K_RETURN:
                        current_state = STATE_INSTRUCTIONS
                        instructions_scroll_y = 0 # Reset scroll
                    elif event.key == pygame.K_l:
                        current_state = STATE_LEADERBOARD
                        leaderboard_scroll_offset = 0
                        
                    elif event.key == pygame.K_t: # DEV MODE TOGGLE
                        dev_force_st_michaels = not dev_force_st_michaels
                        print(f"DEV MODE: Force St Michaels = {dev_force_st_michaels}")
                        # Optional visual cue?
                        # splash_bg = None # Force reload to show? No. Just log it.

                        
                elif current_state == STATE_INSTRUCTIONS:
                    if event.key == pygame.K_RETURN:
                        reset_game()
                        current_state = STATE_RUNNING
                        # Switch to Game Music
                        try:
                            pygame.mixer.music.load("assets/sounds/background_music.mp3")
                            pygame.mixer.music.play(-1)
                        except Exception as e: print(f"Music Error: {e}")
                    
                    elif event.key == pygame.K_UP:
                         instructions_scroll_y = max(0, instructions_scroll_y - 20)
                    elif event.key == pygame.K_DOWN:
                         instructions_scroll_y += 20
                        
                    elif event.key == pygame.K_ESCAPE:
                        reset_game()
                        current_state = STATE_SPLASH
                        # Switch back to Splash Music
                        try:
                            pygame.mixer.music.load("assets/You_cant_park_there.mp3")
                            pygame.mixer.music.play(-1)
                        except Exception as e: print(f"Music Error: {e}")
                        
                elif current_state in [STATE_RUNNING, STATE_WARDEN_RAGE]:
                    # Movement
                    dx, dy = 0, 0
                    if event.key == pygame.K_UP: dy = -1
                    elif event.key == pygame.K_DOWN: dy = 1
                    elif event.key == pygame.K_LEFT: dx = -1
                    elif event.key == pygame.K_RIGHT: dx = 1
                    
                    if dx != 0 or dy != 0:
                        player.move(dx, dy, game_map)
                    
                    if event.key == pygame.K_z: player.undo() # Should be elif, but kept separate for logic flow
                    
                    # Check Arrival at Mission
                    if (player.x, player.y) == current_mission_spot:
                        if blip_sfx: blip_sfx.play()
                        # Trigger Pop-up (Phase 2)
                        current_state = STATE_MISSION_POPUP
                        
                    elif event.key == pygame.K_ESCAPE:
                        reset_game()
                        current_state = STATE_SPLASH

                elif current_state == STATE_MISSION_POPUP:
                    # Choice: Pay or Risk
                    if event.key == pygame.K_p or (guilt_mode_active and event.key == pygame.K_RETURN):
                        # Logic Applied Immediately
                        money -= mission_cost
                        # game_message = f"Paid £{mission_cost:.2f}. Safe." # Moved to Feedback
                        # message_timer = 60
                        player.is_safe = True # IMMUNITY granted
                        
                        # Audio
                        if pay_sfx: pay_sfx.play()

                        # Check if this Payment ends a Rage Mode
                        if reward_level >= 6:
                             # Speed Up Warden by 25% (Post-Rage Difficulty)
                             warden_move_interval = int(warden_move_interval * 0.8) 
                             if warden_move_interval < 50: warden_move_interval = 50
                             pygame.time.set_timer(WARDEN_MOVE_EVENT, warden_move_interval)
                             print(f"RAGE ENDED: Warden Interval now {warden_move_interval}ms (Speed Increased)")

                        # RESET REWARD STREAK
                        reward_level = 0

                        # Trigger Feedback (DELAY STATE SWITCH)
                        feedback_active = True
                        feedback_timer = 60 # 1 Second pulse
                        feedback_text = "PAID - SAFE"
                        feedback_color = (0, 130, 0) # Even Darker Green
                        
                    elif event.key == pygame.K_SPACE: # RISK
                        if guilt_mode_active:
                             game_message = "Too guilty to risk it!"
                             message_timer = 60
                        else:
                            # Audio
                            if risk_sfx: risk_sfx.play()
                        
                            # game_message = "Risking it!"
                            # message_timer = 60
                            player.is_safe = False # Vulnerable
                            
                            # Trigger Feedback (DELAY STATE SWITCH)
                            feedback_active = True
                            feedback_timer = 60 # 1 Second pulse
                            feedback_text = "RISKING IT!"
                            feedback_color = (255, 0, 0) # Red
                            
                            # current_state = STATE_ACTIVITY # Start Waiting (HANDLED IN UPDATE NOW)
                            
                            # Ambush Check
                            if "st micheals" in current_loc_name.lower() and current_date.weekday() < 5:
                                 ambush_active = True
                                 # Spawn 4 Elite Wardens in corners
                                 # Assuming Map is 20x15. Corners: (0,0), (19,0), (0,14), (19,14)
                                 elite_wardens = [
                                     Warden(0, 0),
                                     Warden(19, 0),
                                     Warden(0, 14),
                                     Warden(19, 14)
                                 ]
                                 game_message = "AMBUSH! RUN!"

                    elif event.key == pygame.K_ESCAPE:
                        reset_game()
                        current_state = STATE_SPLASH

                elif current_state == STATE_ACTIVITY:
                    if event.key == pygame.K_ESCAPE:
                        reset_game()
                        current_state = STATE_SPLASH

                elif current_state == STATE_GAME_OVER:
                    # Transition to Name Input automatically or on key press
                    if event.key == pygame.K_RETURN:
                         current_state = STATE_NAME_INPUT
                    elif event.key == pygame.K_ESCAPE:
                        reset_game()
                        current_state = STATE_SPLASH
                        try:
                            pygame.mixer.music.load("assets/You_cant_park_there.mp3")
                            pygame.mixer.music.play(-1)
                        except Exception as e: print(f"Music Error: {e}")

                
                elif current_state == STATE_NAME_INPUT:
                    if event.key == pygame.K_RETURN:
                        if player_name.strip() == "": player_name = "Anon"
                        database.save_score(player_name, int(money))
                        current_state = STATE_LEADERBOARD
                        leaderboard_scroll_offset = 0
                    elif event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        reset_game()
                        current_state = STATE_SPLASH
                        try:
                            pygame.mixer.music.load("assets/You_cant_park_there.mp3")
                            pygame.mixer.music.play(-1)
                        except Exception as e: print(f"Music Error: {e}")
                    else:
                        if len(player_name) < 25: # Max 25 chars
                            player_name += event.unicode
                            
                elif current_state == STATE_LEADERBOARD:
                    if event.key == pygame.K_UP:
                         leaderboard_scroll_offset = max(0, leaderboard_scroll_offset - 1)
                    elif event.key == pygame.K_DOWN:
                         leaderboard_scroll_offset += 1
                    elif event.key == pygame.K_r: # Restart
                         reset_game()
                         current_state = STATE_RUNNING
                         try:
                            pygame.mixer.music.load("assets/sounds/background_music.mp3")
                            pygame.mixer.music.play(-1)
                         except Exception as e: print(f"Music Error: {e}")

                    elif event.key == pygame.K_ESCAPE:
                        reset_game()
                        current_state = STATE_SPLASH
                        try:
                            pygame.mixer.music.load("assets/You_cant_park_there.mp3")
                            pygame.mixer.music.play(-1)
                        except Exception as e: print(f"Music Error: {e}")
            
            elif event.type == pygame.MOUSEWHEEL:
                if current_state == STATE_LEADERBOARD:
                    leaderboard_scroll_offset -= event.y
                    if leaderboard_scroll_offset < 0: leaderboard_scroll_offset = 0
                elif current_state == STATE_INSTRUCTIONS:
                    instructions_scroll_y -= event.y * 20
                    if instructions_scroll_y < 0: instructions_scroll_y = 0
            



            # Music End Events
            elif event.type == MUSIC_END_EVENT:
                if guilt_mode_active:
                    # Guilt Mode Ends
                    guilt_mode_active = False
                    game_message = "Moral Panic Subsided"
                    message_timer = 60
                     # Resume BG Music
                    pygame.mixer.music.set_endevent(pygame.NOEVENT)
                    try:
                        pygame.mixer.music.load("assets/sounds/background_music.mp3")
                        pygame.mixer.music.play(-1)
                    except Exception as e: print(f"Music Error: {e}")

                elif reward_level >= 6:
                    # Rage Over
                    reward_level = 0
                    if current_state != STATE_BUSTED_CUTSCENE: # Don't interrupt cutscene
                        current_state = STATE_RUNNING
                    
                    # Speed Up Warden by 25% (Post-Rage Difficulty)
                    warden_move_interval = int(warden_move_interval * 0.8)
                    if warden_move_interval < 50: warden_move_interval = 50
                    print(f"RAGE ENDED (Music): Warden Interval now {warden_move_interval}ms")
                    
                    pygame.time.set_timer(WARDEN_MOVE_EVENT, warden_move_interval) # Restore speed
                    pygame.mixer.music.set_endevent(pygame.NOEVENT)
                    
                    try:
                        pygame.mixer.music.load("assets/sounds/background_music.mp3")
                        pygame.mixer.music.play(-1)
                    except Exception as e: print(f"Music Error: {e}")
                    
                    game_message = "Warden calmed down."
                    message_timer = 60

            # AI Movement
            elif event.type == WARDEN_MOVE_EVENT:
                # Unified Warden Movement Logic
                can_move = False
                use_rage_logic = False
                
                if current_state in [STATE_RUNNING, STATE_ACTIVITY, STATE_WARDEN_RAGE]:
                    can_move = True
                    if reward_level >= 6:
                        use_rage_logic = True
                
                if can_move:
                    # 1. Update Position
                    if use_rage_logic:
                         # RAGE MODE: Moves clockwise around edges or hunts edges
                         warden.update_rage(game_map)
                    else:
                        # Standard Pathfinding
                        target_pos = (player.x, player.y)
                        # Distraction Logic: If user interacted safely, Warden walks away temporarily
                        if current_state == STATE_ACTIVITY and warden_distraction_target:
                             target_pos = warden_distraction_target
                        warden.update(game_map, target_pos)

                    # 2. Unified Collision Check
                    if warden.x == player.x and warden.y == player.y:
                        if current_state == STATE_ACTIVITY:
                            if not player.is_safe:
                                # ONLY fine if parked and risky
                                # TRIGGER CUTSCENE
                                pygame.mixer.music.pause()
                                current_state = STATE_BUSTED_CUTSCENE
    
                                # Load Large Landmark Backdrop
                                for lm in LANDMARKS:
                                    if lm['name'] == current_loc_name:
                                        try:
                                            raw_img = pygame.image.load(lm['image']).convert()
                                            cutscene_bg = pygame.transform.scale(raw_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
                                            tint = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                                            tint.fill((0, 0, 0))
                                            tint.set_alpha(150)
                                            cutscene_bg.blit(tint, (0,0))
                                        except Exception as e: pass
                                        break
    
                                cutscene_timer = 0
                                cutscene_van_x = -600 
                                cutscene_warden_x = SCREEN_WIDTH + 100
                                if busted_sfx: busted_channel = busted_sfx.play()
                            else:
                                # Safe Interaction - Send Warden Away
                                # Find nearest edge
                                dx_left = warden.x
                                dx_right = 19 - warden.x
                                dy_top = warden.y
                                dy_bottom = 14 - warden.y
                                
                                min_dist = min(dx_left, dx_right, dy_top, dy_bottom)
                                if min_dist == dx_left: warden_distraction_target = (0, warden.y)
                                elif min_dist == dx_right: warden_distraction_target = (19, warden.y)
                                elif min_dist == dy_top: warden_distraction_target = (warden.x, 0)
                                else: warden_distraction_target = (warden.x, 14)
                                
                                game_message = "Phew! Interaction Safe."
                                message_timer = 60
        
        if message_timer > 0: message_timer -= 1
        
        if current_state == STATE_RUNNING and pending_guilt_check:
             pending_guilt_check = False 
             
             # Guilt Mode Mechanic
             print(f"Guilt Check: Chance is {guilt_chance:.4f}")
             if random.random() < guilt_chance:
                 print("GUILT MODE TRIGGERED!")
                 guilt_mode_active = True
                 
                 # Play Guilt Music
                 try:
                     pygame.mixer.music.load("assets/sounds/guilt.mp3")
                     pygame.mixer.music.play(0) # Play once
                     pygame.mixer.music.set_endevent(MUSIC_END_EVENT)
                 except Exception as e: print(f"Guilt Audio Error: {e}")
             else:
                 # Normal Music Resume
                 try:
                     pygame.mixer.music.load("assets/sounds/background_music.mp3")
                     pygame.mixer.music.play(-1)
                 except: pass
             
             # Double the chance for next time
             guilt_chance *= 2
        
        if current_state == STATE_SPLASH:
            # Animate Car (Left -> Right) - Larger Car, Slower/Interval
            splash_car_x += 8 # Speed
            if splash_car_x > SCREEN_WIDTH + 200:
                splash_car_x = -2000  # Reset loop far back for frequency delay (approx 3-4s gap)
            
            # Animate Warden (Pop Up Logic)
            if warden_state == "waiting":
                warden_pop_timer += 1
                if warden_pop_timer > 180: # Wait 3 seconds
                     warden_state = "popping_up"
                     warden_pop_timer = 0
            
            elif warden_state == "popping_up":
                if splash_warden_y > SCREEN_HEIGHT - 250:
                    splash_warden_y -= 5
                else:
                    warden_state = "holding"
                    warden_hold_timer = 120 # Hold 2 seconds
            
            elif warden_state == "holding":
                warden_hold_timer -= 1
                if warden_hold_timer <= 0:
                    warden_state = "popping_down"
            
            elif warden_state == "popping_down":
                if splash_warden_y < SCREEN_HEIGHT:
                    splash_warden_y += 5
                else:
                    warden_state = "waiting"
                    warden_pop_timer = random.randint(0, 120) # Randomize next wait slightly
                    splash_warden_x = random.randint(50, SCREEN_WIDTH - 200) # Randomize Location

        # --- FEEDBACK TIMER LOGIC ---
        if current_state == STATE_MISSION_POPUP and feedback_active:
            feedback_timer -= 1
            if feedback_timer <= 0:
                feedback_active = False
                current_state = STATE_ACTIVITY
        
        if current_state == STATE_ACTIVITY:
            
            # --- AMBUSH LOGIC ---
            if ambush_active and elite_wardens:
                 # Move Elite Wardens (Fast - every 15 frames roughly, or just random chance)
                 # Let's make them move every frame for "Rapid" or every few frames.
                 # Since this is the main loop (60 FPS), moving every frame is insanely fast.
                 # Let's use a timer or modulo.
                 if activity_timer % 20 == 0: # Move 3 times a second
                     for ew in elite_wardens:
                         target = (player.x, player.y)
                         ew.update(game_map, target)
                         
                         # Check Collision
                         if ew.x == player.x and ew.y == player.y:
                             # BUSTED BY ELITE SQUAD
                             pygame.mixer.music.pause()
                             current_state = STATE_BUSTED_CUTSCENE
                             
                             # Load Large Landmark Backdrop (Same logic as standard bust)
                             for lm in LANDMARKS:
                                if lm['name'] == current_loc_name:
                                    try:
                                        raw_img = pygame.image.load(lm['image']).convert()
                                        cutscene_bg = pygame.transform.scale(raw_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
                                        tint = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                                        tint.fill((0, 0, 0))
                                        tint.set_alpha(150)
                                        cutscene_bg.blit(tint, (0,0))
                                    except Exception as e: pass
                                    break
                             
                             cutscene_timer = 0
                             cutscene_van_x = -600 
                             cutscene_warden_x = SCREEN_WIDTH + 100
                             if busted_sfx: busted_channel = busted_sfx.play()
                             
                             # Reset Ambush
                             ambush_active = False
                             elite_wardens = []
                             game_message = "CAUGHT BY ELITE SQUAD!"
                             break # Exit warden loop

            if current_state == STATE_ACTIVITY:
                activity_timer -= 1
            if activity_timer <= 0:
                if coin_sfx: coin_sfx.play()
                # Mission Complete
                
                # Reset Ambush if survived
                if ambush_active:
                    ambush_active = False
                    elite_wardens = []
                    game_message = "Escaped the Squad!"
                
                final_reward = potential_reward
                
                if player.is_safe:
                    # Safe delivery
                    money += final_reward
                    game_message = f"Done: {current_task_name}! +£{final_reward:.2f}"
                else:
                    # Risky delivery succeeded
                    # Calculate Multiplier
                    mult = 1.1 ** reward_level
                    final_reward = potential_reward * mult
                    money += final_reward
                    game_message = f"Risk Paid Off: {current_task_name}! +£{final_reward:.2f}"
                    
                    # Increase Reward Level (Only if NOT RAGING)
                    if current_state != STATE_WARDEN_RAGE:
                        reward_level += 1
                
                message_timer = 90 # Slower clear to read
                player.is_safe = False # Reset safety for driving
                
                # Check for RAGE
                if reward_level >= 6:
                    current_state = STATE_WARDEN_RAGE
                    pygame.time.set_timer(WARDEN_MOVE_EVENT, 125) # 4x Speed (500 -> 125)

                    if reward_level == 6:
                        try:
                             # Start Rage Music (Only on first trigger)
                             pygame.mixer.music.load("assets/sounds/yellow.mp3")
                             pygame.mixer.music.play(0) 
                             pygame.mixer.music.set_endevent(MUSIC_END_EVENT)
                        except Exception as e: print(f"Music Error: {e}")
                    
                    start_new_mission()
                else:
                    current_state = STATE_RUNNING
                    start_new_mission()

        # Cutscene Update
        if current_state == STATE_BUSTED_CUTSCENE:
            cutscene_timer += 1
            
            # Animation: Slide in
            target_van_x = -50 
            target_warden_x = 600
            
            # Simple Lerp or just constant speed
            if cutscene_van_x < target_van_x: cutscene_van_x += 15
            if cutscene_warden_x > target_warden_x: cutscene_warden_x -= 15
            
            # End Check (2 seconds = 120 frames) 
            # User Request: Fixed duration, ignore audio length check
            if cutscene_timer > 120:
                # FINALIZE PUNISHMENT
                fine_mult = 1.5 ** fine_level
                fine_amount = 50 * fine_mult
                money -= fine_amount
                game_message = f"BUSTED! FINED £{fine_amount:.2f}!"
                message_timer = 120
                
                # Logic Updates
                fine_level += 1 # Fine gets worse
                reward_level = 0 # Streak lost
                
                # Progressive Difficulty: Faster Warden
                warden_move_interval = int(warden_move_interval * 0.9)
                if warden_move_interval < 50: warden_move_interval = 50 # Cap at 50ms
                pygame.time.set_timer(WARDEN_MOVE_EVENT, warden_move_interval)
                print(f"DIFFICULTY UP: Warden Interval now {warden_move_interval}ms")
                
                # Respawn / Reset
                player.x, player.y = 0, 0
                warden.x, warden.y = 19, 14
                warden.path = []
                
                # Clear Ambush
                ambush_active = False
                elite_wardens = []
                
                
                elite_wardens = []
                
                # Defer Guilt Check to STATE_RUNNING
                pending_guilt_check = True
                current_state = STATE_RUNNING
                
                current_mission_spot = random.choice(available_spots)

        # Draw logic follows...


        # 3. Draw
        # 3. Draw
        if current_state != STATE_INSTRUCTIONS and current_state != STATE_SPLASH and current_state != STATE_BUSTED_CUTSCENE:
             screen.fill(COLOUR_BG)
        
        
        if current_state == STATE_BUSTED_CUTSCENE:
            if cutscene_bg: screen.blit(cutscene_bg, (0,0))
            else: screen.fill((50, 0, 0)) # Red fallback
            
            # Van (Left)
            # Aligned to ground level (Bottom ~720)
            if cutscene_van: screen.blit(cutscene_van, (cutscene_van_x, SCREEN_HEIGHT - 500)) 
            else: pygame.draw.rect(screen, (0,0,255), (cutscene_van_x, SCREEN_HEIGHT - 500, 400, 200))
            
            # Warden (Right)
            if cutscene_warden: screen.blit(cutscene_warden, (cutscene_warden_x, SCREEN_HEIGHT - 350))
            else: pygame.draw.rect(screen, (255,255,0), (cutscene_warden_x, SCREEN_HEIGHT - 450, 100, 200))
            
            # Overlay Text?
            font_big = pygame.font.Font(None, 100)
            txt = font_big.render("BUSTED!", True, (255, 0, 0))
            screen.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, 100))
            
            # Stats Overlay
            font_sub = pygame.font.Font(None, 50)
            fine_est = 50 * (1.5 ** fine_level) # Current fine
            sub_txt = font_sub.render(f"FINE: £{fine_est:.2f}", True, (255, 255, 0))
            screen.blit(sub_txt, (SCREEN_WIDTH//2 - sub_txt.get_width()//2, 200))
            
            pygame.display.flip()
            clock.tick(FPS)
            pygame.display.flip()
            clock.tick(FPS)
            continue # Skip rest of draw loop

        # Replaces old STATE_GUILT_MODE block
        
        if current_state == STATE_SPLASH:
            if splash_bg:
                screen.blit(splash_bg, (0, 0))
            else:
                 screen.fill((20, 20, 40)) # Dark Blue-Grey fallback
            
            # Draw Animation Elements
            
            # Rupert's Car (Foreground or Midground?) - Let's say Midground
            # Use cutscene_van asset (which is Rupert's car scaled)
            # We might want to scale it down slightly for the street scene if it's huge
            # The loaded 'cutscene_van' is (750, 500) which is HUGE. Let's rescale on the fly or load a smaller one?
            # Creating a smaller temp surface for splash might be better for performance, but blit transform is okay for now.
            # Rupert's Car (Foreground)
            if cutscene_van:
                # Car Removed as per user request
                pass 
            
            # Warden (Pop Up)
            if cutscene_warden:
                # Warden is (150, 300).
                # Draw at fixed X (Right Side), Animated Y
                warden_splash = pygame.transform.scale(cutscene_warden, (150, 300))
                screen.blit(warden_splash, (splash_warden_x, splash_warden_y))

            # Title: Clean Text Top
            # User requested "more pixelated" font. 
            # Pygame default font (None) is usually a simple bitmap-like font.
            # Or we can use 'consolas' for a fixed-width look. 
            # Let's try the default font first as it fits the "retro" vibe better than Georgia.
            try:
                # None uses the default pygame font which is often 'freesansbold'
                font_title = pygame.font.Font(None, 80) 
            except:
                 font_title = pygame.font.SysFont("consolas", 60, bold=True)
            
            # Instructions: Moved to Top
            font_instr = pygame.font.Font(None, 40)
            
            instr_1 = "Press ENTER to Begin"
            instr_2 = "Press 'L' for Leaderboard"
            
            # Render White text with Black thick outline/shadow for readability on complex BG
            def render_text_with_outline(text, font, color=(255, 255, 255), outline_color=(0, 0, 0)):
                base = font.render(text, True, color)
                outline = font.render(text, True, outline_color)
                # varying positions for outline
                surf = pygame.Surface((base.get_width() + 4, base.get_height() + 4), pygame.SRCALPHA)
                for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2), (-2, 0), (2, 0), (0, -2), (0, 2)]:
                    surf.blit(outline, (dx+2, dy+2))
                surf.blit(base, (2, 2))
                return surf

            i1_surf = render_text_with_outline(instr_1, font_instr)
            i2_surf = render_text_with_outline(instr_2, font_instr)
            
            # Position Instructions at Just Below Half Way
            screen.blit(i1_surf, (SCREEN_WIDTH//2 - i1_surf.get_width()//2, 400))
            screen.blit(i2_surf, (SCREEN_WIDTH//2 - i2_surf.get_width()//2, 450))

            # Title: Animated Pulse at BOTTOM
            title_text = "Traffic Warden Roulette"
            
            # Create a composite surface for the title to ensure outline scales correctly
            # render base
            base_black = font_title.render(title_text, True, (50, 50, 50)) # Dark Grey
            base_yellow = font_title.render(title_text, True, (255, 255, 0)) # Traffic Yellow
            
            # Create container
            w = base_black.get_width() + 10
            h = base_black.get_height() + 10
            logo_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            
            # Draw Thick Yellow Outline (Simulating Double Yellow Lines)
            # We draw at multiple offsets
            offsets = [(-3,0), (3,0), (0,-3), (0,3), (-2,-2), (2,-2), (-2,2), (2,2)]
            for dx, dy in offsets:
                logo_surf.blit(base_yellow, (5+dx, 5+dy))
                
            # Draw Black Main Text
            logo_surf.blit(base_black, (5, 5))
            
            # Pulse Animation
            pulse = math.sin(pygame.time.get_ticks() * 0.005) # -1 to 1
            scale_fac = 1.0 + (pulse * 0.05) # 0.95 to 1.05
            
            final_w = int(logo_surf.get_width() * scale_fac)
            final_h = int(logo_surf.get_height() * scale_fac)
            
            anim_title = pygame.transform.scale(logo_surf, (final_w, final_h))
            
            title_x = SCREEN_WIDTH//2 - final_w//2
            title_y = SCREEN_HEIGHT - 150 # Bottom area
            
            # Draw Title
            screen.blit(anim_title, (title_x, title_y))

            
        elif current_state == STATE_INSTRUCTIONS:
            screen.fill(COLOUR_BG) # Ensure background for transparency
            if instructions_bg:
                screen.blit(instructions_bg, (0, 0))

            font_head = pygame.font.Font(None, 50)
            font_body = pygame.font.Font(None, 34) # Slightly larger for readability
            
            paragraphs = [
                "CIRENCESTER'S BUSIEST DAD",
                "You are Rupert, the ultimate busy dad of Cirencester. Your schedule is packed tighter than the Fleece on a Friday night. Your wife Clementine has an endless list of 'essential' errands, from picking up her specific vintage of wine to dropping off dry cleaning. Your daughter Fenella needs taxiing to ballet, and your teenage son Ivor has rugby practice, drum lessons, and a social life better than yours.",
                "But there's a problem. Parking in Cirencester costs a small fortune, and the Council have deployed their elite squad of Traffic Wardens to squeeze every penny out of motorists. You have a choice: play it safe and pay the extortionate parking fees, seeing your family's holiday fund dwindle away, or be audacious.",
                "Risking a fine by not paying builds your 'Audacity'. The more audacious you are, the more money you save for the big family adventure next year. But be warned: if you get caught, the fines are hefty, and your hard-earned audacity is reset.",
                "HOW TO PLAY:",
                "1. Drive to the YELLOW ZONES to complete errands.",
                "2. 'Pay' to be safe, or 'Risk it' to build Audacity.",
                "3. High Audacity multiplies your savings.",
                "4. If a Warden catches you while risking it, you get FINED.",
                "5. Survive the year with the biggest Holiday Fund possible.",
                "[PRESS ENTER TO START]"
            ]
            
            # Text Wrapping Logic
            margin_x = 100
            max_width = SCREEN_WIDTH - (margin_x * 2)
            current_y = 100 - instructions_scroll_y
            
            for para in paragraphs:
                if "CIRENCESTER" in para:
                    fnt = font_head
                    col = (255, 215, 0)
                elif "HOW TO PLAY" in para or "[PRESS" in para:
                    fnt = font_head
                    col = (255, 255, 255)
                    current_y += 20 # Extra space before headers
                else:
                    fnt = font_body
                    col = (255, 255, 200) # Creamy white for body
                
                # Split words
                words = para.split(' ')
                lines_to_render = []
                current_line_words = []
                
                for word in words:
                    test_line = ' '.join(current_line_words + [word])
                    if fnt.size(test_line)[0] <= max_width:
                        current_line_words.append(word)
                    else:
                        lines_to_render.append(' '.join(current_line_words))
                        current_line_words = [word]
                lines_to_render.append(' '.join(current_line_words))
                
                # Render Lines
                for txt_line in lines_to_render:
                    if current_y > -50 and current_y < SCREEN_HEIGHT + 50: # Only render visible
                        # Stroke
                        base = fnt.render(txt_line, True, (0, 0, 0))
                        offsets = [(-2, -2), (-2, 2), (2, -2), (2, 2)]
                        for dx, dy in offsets:
                            screen.blit(base, (SCREEN_WIDTH//2 - base.get_width()//2 + dx, current_y + dy))
                            
                        surf = fnt.render(txt_line, True, col)
                        screen.blit(surf, (SCREEN_WIDTH//2 - surf.get_width()//2, current_y))
                    
                    current_y += fnt.get_height() + 5
                
                current_y += 20 # Paragraph gap
                
                current_y += 20 # Paragraph gap
                
        elif current_state in [STATE_RUNNING, STATE_MISSION_POPUP, STATE_ACTIVITY, STATE_GAME_OVER, STATE_WARDEN_RAGE]:
            # --- COMMON GAMEPLAY RENDERING ---
            
            # 1. Draw Map & Entities
            game_map.draw(screen, offset_y=MAP_OFFSET_Y)
            
            # Highlight Mission Target
            mx, my = current_mission_spot
            pygame.draw.rect(screen, (255, 215, 0), (mx*40, my*40 + MAP_OFFSET_Y, 40, 40), 3)

            player.draw(screen, offset_y=MAP_OFFSET_Y)
            warden.draw(screen, offset_y=MAP_OFFSET_Y)
            
            # Draw Elite Wardens
            if ambush_active and elite_wardens:
                for ew in elite_wardens:
                    ew.draw(screen, offset_y=MAP_OFFSET_Y)

            # 2. Draw Common HUD (Top Bar)
            pygame.draw.rect(screen, (0,0,0), (0,0, SCREEN_WIDTH, 40))
            
            font = pygame.font.Font(None, 36)
            font_small = pygame.font.Font(None, 24)
            font_hud = pygame.font.Font(None, 28)

            # Money & Date
            ui_text = f"£{money:.2f}   Date: {current_date.strftime('%d %b')}"
            ui_surf = font.render(ui_text, True, (255, 255, 255))
            screen.blit(ui_surf, (20, 10))

            # Reward Bar (Audacity)
            bar_start_x = 420
            bar_y = 10
            seg_w = 15
            seg_h = 20
            gap = 2
            
            rw_label = font_small.render("Audacity:", True, (200, 200, 200))
            screen.blit(rw_label, (bar_start_x - rw_label.get_width() - 10, bar_y + 2))
            
            for i in range(6):
                col = (50, 50, 50) 
                if i < reward_level:
                    col = (0, 255, 100) 
                    if reward_level > 6 and i == 5: col = (255, 215, 0)
                pygame.draw.rect(screen, col, (bar_start_x + i*(seg_w+gap), bar_y, seg_w, seg_h))
                
            # Fine Bar
            fine_start_x = 650
            fn_label = font_small.render("Fine:", True, (200, 200, 200))
            screen.blit(fn_label, (fine_start_x - fn_label.get_width() - 10, bar_y + 2))
            
            for i in range(6):
                col = (50, 0, 0)
                if i < fine_level:
                    col = (255, 0, 0)
                pygame.draw.rect(screen, col, (fine_start_x + i*(seg_w+gap), bar_y, seg_w, seg_h))

            # --- STATE SPECIFIC OVERLAYS ---
            
            if current_state == STATE_RUNNING:
                # Active Goal HUD Overlay
                txt = f"GOAL: {current_task_name} @ {current_loc_name}"
                
                # Dynamic Resizing
                txt_w, txt_h = font_hud.size(txt)
                box_w = max(500, txt_w + 40) # Min 500, or text + padding
                
                panel_hud = pygame.Rect(SCREEN_WIDTH//2 - box_w//2, 45, box_w, 30) # Below top bar
                pygame.draw.rect(screen, (0, 0, 0), panel_hud)
                pygame.draw.rect(screen, (255, 215, 0), panel_hud, 2)
                
                surf = font_hud.render(txt, True, (255, 255, 255))
                screen.blit(surf, (SCREEN_WIDTH//2 - surf.get_width()//2, 50))
            


            if current_state == STATE_WARDEN_RAGE:
                # Green Rage Overlay (Map Area Only)
                rage_overlay = pygame.Surface((SCREEN_WIDTH, 600)) # Height of map (15 * 40)
                rage_overlay.fill((0, 255, 0)) # Green
                rage_overlay.set_alpha(50) # Subtle green tint
                screen.blit(rage_overlay, (0, MAP_OFFSET_Y))

                rage_font = pygame.font.Font(None, 40)
                rage_txt = rage_font.render("WARDEN DESPAIR RAGE", True, (255, 0, 0))
                screen.blit(rage_txt, (SCREEN_WIDTH//2 - rage_txt.get_width()//2, 55))


                
            # Draw Activity Progress
            if current_state == STATE_ACTIVITY:
                # Bar at bottom
                bar_width = 400
                bar_height = 30
                bar_rect = pygame.Rect((SCREEN_WIDTH - bar_width)//2, SCREEN_HEIGHT - 60, bar_width, bar_height)
                progress = activity_timer / activity_duration_max
                
                pygame.draw.rect(screen, (50, 50, 50), bar_rect)
                fill_width = int(bar_width * (1.0 - progress)) 
                fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, int(bar_width * progress), bar_height)
                col = (0, 255, 0) if player.is_safe else (255, 165, 0) # Green if safe, Orange if risky
                pygame.draw.rect(screen, col, fill_rect)
                pygame.draw.rect(screen, (255, 255, 255), bar_rect, 2)
                
                label = "Paid" if player.is_safe else "Risking IT"
                txt_surf = font.render(label, True, (255, 255, 255))
                screen.blit(txt_surf, (bar_rect.centerx - txt_surf.get_width()//2, bar_rect.y - 30))

            # Game Over Screen
            if current_state == STATE_GAME_OVER:
                panel = pygame.Rect(100, 100, 600, 400)
                pygame.draw.rect(screen, (0, 0, 0), panel)
                end_surf = font.render("YEAR COMPLETE", True, (255, 255, 255))
                final_surf = font.render(f"Final Money: £{money:.2f}", True, (255, 255, 0))
                save_surf = font.render("Press ENTER to Save Score", True, (200, 200, 200))
                screen.blit(end_surf, (300, 200))
                screen.blit(final_surf, (300, 250))
                screen.blit(save_surf, (300, 300))
        
            # --- GUILT MODE OVERLAY (Rendered LAST) ---
            if guilt_mode_active:
                 # Red Overlay (Map Area Only)
                 overlay = pygame.Surface((SCREEN_WIDTH, 600)) # Height of map (15 * 40)
                 overlay.fill((255, 0, 0))
                 overlay.set_alpha(100) # ~40% opacity
                 screen.blit(overlay, (0, MAP_OFFSET_Y))
                 
                 # Flashing Text
                 if pygame.time.get_ticks() % 1000 < 500: # Flash every 0.5s
                     font_panic = pygame.font.Font(None, 60)
                     txt_panic = font_panic.render("Moral Panic: Guilt Mode Enabled", True, (255, 255, 255))
                     # Shadow
                     txt_shadow = font_panic.render("Moral Panic: Guilt Mode Enabled", True, (0, 0, 0))
                     
                     screen.blit(txt_shadow, (SCREEN_WIDTH//2 - txt_panic.get_width()//2 + 2, 100 + 2))
                     screen.blit(txt_panic, (SCREEN_WIDTH//2 - txt_panic.get_width()//2, 100))

            # --- RENDER MISSION POPUP (TOP LAYER) ---
            if current_state == STATE_MISSION_POPUP:
                # Scenario Popup
                # Increased size for accessibility and long text
                panel_rect = pygame.Rect(50, 50, 700, 550) 
                pygame.draw.rect(screen, (20, 20, 30), panel_rect)
                pygame.draw.rect(screen, (255, 255, 255), panel_rect, 2)
                
                # Dev Indicator
                if dev_force_st_michaels:
                    dev_txt = font_small.render("DEV MODE: ST MICHAELS FORCED", True, (255, 0, 0))
                    screen.blit(dev_txt, (70, 60))
                
                # Mission Text
                y_tex = 130
                for line in mission_scenario_text.split('\n'):
                     surf = font.render(line, True, (255, 255, 255))
                     screen.blit(surf, (150, y_tex))
                     y_tex += 40
                     
                # Calculations
                current_mult = 1.1 ** reward_level
                safe_profit = 0.00
                risk_profit = potential_reward * current_mult
                
                # Options
                opt1 = font.render(f"[P] PAY £{mission_cost:.2f} (Profit: £{safe_profit:.2f})", True, (100, 255, 100))
                
                if guilt_mode_active:
                     opt2 = font.render("You are feeling too guilty to risk it", True, (255, 50, 50))
                     # Add Enter Hint
                     opt3 = font_small.render("[ENTER] Accept Fate (Pay)", True, (200, 200, 200))
                     screen.blit(opt3, (150, 430))
                else:
                     opt2 = font.render(f"[SPACE] RISK IT (Profit: £{risk_profit:.2f})", True, (255, 100, 100))
                
                screen.blit(opt1, (150, 350))
                screen.blit(opt2, (150, 400))
                
                # --- VISUAL FEEDBACK (PULSING) ---
                if feedback_active:
                    # Calculate Pulse
                    # Simple sin wave: freq 0.2
                    pulse = 1.0 + 0.2 * math.sin(pygame.time.get_ticks() * 0.01)
                    
                    # Use existing huge font or create one globally?
                    # Better: Render at base size and scale
                    base_font = pygame.font.Font(None, 100)
                    
                    # Render Main and Stroke
                    fb_surf_main = base_font.render(feedback_text, True, feedback_color)
                    fb_surf_stroke = base_font.render(feedback_text, True, (255, 255, 255))
                    
                    # Scale logic
                    cur_w = int(fb_surf_main.get_width() * pulse)
                    cur_h = int(fb_surf_main.get_height() * pulse)
                    
                    fb_surf_main = pygame.transform.scale(fb_surf_main, (cur_w, cur_h))
                    fb_surf_stroke = pygame.transform.scale(fb_surf_stroke, (cur_w, cur_h))
                    
                    cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
                    
                    # Draw Stroke (Offsets)
                    for ox, oy in [(-3, -3), (-3, 3), (3, -3), (3, 3), (-3, 0), (3, 0), (0, -3), (0, 3)]:
                        rect = fb_surf_stroke.get_rect(center=(cx + ox, cy + oy))
                        screen.blit(fb_surf_stroke, rect)
                    
                    # Draw Main Text
                    fb_rect = fb_surf_main.get_rect(center=(cx, cy))
                    screen.blit(fb_surf_main, fb_rect)
                
        elif current_state == STATE_NAME_INPUT:
             screen.fill((0, 0, 0))
             font_head = pygame.font.Font(None, 50)
             font_inp = pygame.font.Font(None, 60)
             
             head = font_head.render("ENTER YOUR NAME:", True, (255, 255, 255))
             inp_surf = font_inp.render(player_name + "_", True, (0, 255, 0))
             
             screen.blit(head, (SCREEN_WIDTH//2 - head.get_width()//2, 200))
             screen.blit(inp_surf, (SCREEN_WIDTH//2 - inp_surf.get_width()//2, 300))
             
        elif current_state == STATE_LEADERBOARD:
            screen.fill((20, 20, 30))
            font_head = pygame.font.Font(None, 50)
            font_row = pygame.font.Font(None, 36)
            
            head = font_head.render("LEADERBOARD", True, (255, 215, 0))
            screen.blit(head, (SCREEN_WIDTH//2 - head.get_width()//2, 50))
            
            scores = database.get_top_scores(50)
            
            # Simple clamping
            if leaderboard_scroll_offset > len(scores) - 8:
                leaderboard_scroll_offset = max(0, len(scores) - 8)
                
            visible_scores = scores[leaderboard_scroll_offset : leaderboard_scroll_offset + 8]
            
            y_off = 150
            for row in visible_scores:
                # (name, score, date)
                name, scr, date = row
                row_str = f"{name}: £{scr}"
                surf = font_row.render(row_str, True, (255, 255, 255))
                screen.blit(surf, (SCREEN_WIDTH//2 - surf.get_width()//2, y_off))
                y_off += 50
                
            rst = font_row.render("Press 'R' to Restart Year", True, (100, 100, 100))
            home = font_row.render("Press 'ESC' for Home", True, (100, 100, 100))
            screen.blit(rst, (SCREEN_WIDTH//2 - rst.get_width()//2, 560))
            screen.blit(home, (SCREEN_WIDTH//2 - home.get_width()//2, 600))


        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

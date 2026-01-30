# Traffic Warden Roulette 🚔

A high-stakes, 2D grid-based arcade game where you play as **Rupert**, a busy dad in Cirencester, balancing an endless list of family errands with a tactical battle against the town's elite Traffic Warden squad.

## 🕹️ The Concept
Being a dad isn't easy, especially when your wife Clementine has "essential" errands and the kids need taxiing across town. But in Cirencester, every minute you spend parked is a minute you could be fined. 

The game forces a constant choice: 
- **Play it safe:** Pay the parking fee and protect your holiday fund.
- **Risk it:** Be audacious, save your money, and build your **Audacity** meter to multiply your savings.

But watch out! The Warden is guided by a relentless A* pathfinding brain. If you're "Risking It" and they catch you, the fines will hurt.

## 🚀 Key Features
- **Smart AI Warden:** Uses graph-based A* pathfinding to hunt you down.
- **Dynamic Mission System:** Errand locations and types change based on real landmarks like the Roman Amphitheatre and Corinium Museum.
- **Calendar & Special Events:** From weekend free parking at St Michaels to weekday 5-carat ambushes.
- **Persistence:** High scores are stored in a local SQLite database.
- **Tactical Gameplay:** Use the 'Undo' feature (Z key) to rewind your steps and outmaneuver the authorities.

## 🧠 My Learning Journey
I built this project to explore **Pygame** and challenge myself to implement fundamental Computer Science concepts in a practical, interactive way. It served as a sandbox for me to move beyond basic scripts and into structured game architecture.

Key areas I focused on include:
- **Custom Data Structures:** I implemented my own **Graphs** (for navigation), **Linked Lists** (for the undo feature/history), and **2D Arrays** (for the world grid).
- **Relentless AI:** I wanted to see if I could create an enemy that felt "smart," which led me to implement the **A* (A-Star)** pathfinding algorithm.
- **Data Persistence:** Using **SQLite** taught me how to bridge a real-time game loop with a persistent database to save progress and high scores.
- **Modular Design:** Moving from a single file to a multi-module architecture (`sprites`, `map`, `database`) helped me understand how to organize larger Python projects.

## 🛠️ How to Run
1. Ensure you have **Python 3.x** and **Pygame** installed (`pip install pygame`).
2. Clone this repository.
3. Run `python main.py`.

---
*Built with ❤️ for Cirencester's busiest dads.*

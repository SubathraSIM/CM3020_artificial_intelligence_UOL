# CM3020 Artificial Intelligence - University of London

Coursework for **CM3020 Artificial Intelligence** (BSc Computer Science, University of London). The coursework has two parts: a research essay on game-playing AI, and a genetic algorithm that evolves simulated creatures to climb a mountain in PyBullet.

| Part | Project | Key topics |
|---|---|---|
| Part A | Research essay: Game-Playing AI | AI research history, applications, ethics, neural networks vs search |
| Part B | Evolving mountain-climbing creatures | Genetic algorithms, physics simulation, fitness design, experiments |

**Tech:** Python · PyBullet · NumPy · Matplotlib / Excel (results)

---

## Part B - Genetic Algorithm: Evolving Mountain Climbers

Simulated creatures in **PyBullet** are evolved with a **genetic algorithm** to climb a Gaussian pyramid mountain. Each creature's body shape and joint motors are encoded in its genome.

### What I built

**Environment integration**
- Replaced the flat floor with a mountain arena for training and for CSV replays
- Spawned creatures near the mountain base so fitness comes from climbing, not an initial drop

**Anti-cheat rules**
- **Arena boundary:** runs where the creature leaves the sandbox are flagged as cheated and stopped
- **Airborne detection:** contact points are checked every step, and a run is flagged if the creature stays in the air for more than 480 consecutive steps

**Custom fitness function**

The starter fitness (straight-line distance) rewarded launching or wandering away. I replaced it with a weighted climbing score:

| Component | Rewards | Weight |
|---|---|---|
| Best height near mountain | Actual climbing on the slope | 100 |
| Closeness | Reaching the mountain area | 25 |
| Final height | Height held at the end of the run | 20 |
| Uphill score | Sum of positive height gains near the slope | 15 |
| Progress | Moving toward the mountain centre | 8 |

### Experiments (3 runs per setting)

| Parameter | Tested values | Finding |
|---|---|---|
| Population size | 10 → 100 | Average best fitness rose from **83.5 → 1386.7**; bigger populations were better on every metric |
| Genome size | 3 → 12 genes | 12 genes performed best (avg best **688.9** vs 83.5) |
| Simulation rate | 2400 → 6000 | 3600 gave the strongest climbers; 6000 gave the best mean but weaker top performers |

### Encoding scheme experiments
- **Baseline:** evolves both body and motors
- **Motor-only:** body frozen from an elite genome, only motor genes mutate
- **Motor-blended:** motor output blends pulse and sine waves instead of choosing one

➡️ Baseline won clearly (avg best **83.5** vs ~25 for both motor-only variants). **Body structure matters more than control tuning** for climbing.

### Extension: different landscapes
The same GA settings were tested on **Hills** and **Valleys** terrains to check generalisation:
- Hills: avg best **94.2** (better than the mountain)
- Valleys: avg best **43.2** (much worse)

The evolved behaviour partly generalises to similar slopes but struggles with different terrain geometry, so training across several terrains would be needed.

**Key files:** `simulation.py`, `creature.py`, `genome.py`, `ga.py`, `realtime_from_csv.py`, `cw-envt.py`

---

## Part A - Research Essay: Game-Playing AI

A literature-based essay (~1,500 words) covering:
- **Why researchers build game-playing AI:** controlled, repeatable environments (Shannon), exposing the limits of search (Berliner), hard learning problems (Mnih et al., DQN on Atari)
- **Application areas:** strategic decision-making (Libratus poker), robotics and autonomous control, entertainment and game design
- **Ethical issues:** black-box behaviour (OpenAI Five), reward hacking, creativity and player manipulation
- **Are neural networks always best?** No. Chinook and Libratus succeeded with search and game theory, and hybrid systems tend to be the most reliable.

---

## How to run (Part B)

```bash
pip install pybullet numpy
python ga.py                  # run the genetic algorithm
python realtime_from_csv.py   # replay an evolved creature from its CSV
```

# file: story_game.py
import json
import os
from typing import Callable, Dict, List, Optional

SAVE_FILE = "savegame.json"

class Choice:
    def __init__(self, key: str, text: str, next_scene: str, effect: Optional[Callable[['GameState'], None]] = None, requires: Optional[Callable[['GameState'], bool]] = None):
        self.key = key
        self.text = text
        self.next_scene = next_scene
        self.effect = effect
        self.requires = requires

class Scene:
    def __init__(self, key: str, title: str, body: str, choices: List[Choice], on_enter: Optional[Callable[['GameState'], None]] = None):
        self.key = key
        self.title = title
        self.body = body
        self.choices = choices
        self.on_enter = on_enter

class GameState:
    def __init__(self):
        self.flags: Dict[str, bool] = {}
        self.meter: Dict[str, int] = {"comfort": 5}  # 0–10
        self.scene_key: str = "intro"
        self.player_name: str = "You"

    def to_dict(self):
        return {
            "flags": self.flags,
            "meter": self.meter,
            "scene_key": self.scene_key,
            "player_name": self.player_name
        }

    @staticmethod
    def from_dict(d):
        gs = GameState()
        gs.flags = d.get("flags", {})
        gs.meter = d.get("meter", {"comfort": 5})
        gs.scene_key = d.get("scene_key", "intro")
        gs.player_name = d.get("player_name", "You")
        return gs

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def save(state: GameState):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(state.to_dict(), f, indent=2)

def load() -> Optional[GameState]:
    if not os.path.exists(SAVE_FILE):
        return None
    with open(SAVE_FILE, "r", encoding="utf-8") as f:
        return GameState.from_dict(json.load(f))

# ----- Effects & Conditions -----
def set_flag(flag: str, value: bool = True):
    def _fx(state: GameState):
        state.flags[flag] = value
    return _fx

def adjust_comfort(delta: int):
    def _fx(state: GameState):
        state.meter["comfort"] = max(0, min(10, state.meter["comfort"] + delta))
    return _fx

def requires_flag(flag: str, value: bool = True):
    return lambda s: s.flags.get(flag, False) == value

def requires_comfort_at_least(n: int):
    return lambda s: s.meter.get("comfort", 0) >= n

# ----- Scenes -----
def build_scenes() -> Dict[str, Scene]:
    scenes: Dict[str, Scene] = {}

    scenes["intro"] = Scene(
        key="intro",
        title="Café Overture",
        body=(
            "A rainy evening hums outside. Inside the café, warm light and soft jazz. "
            "A friend waves you over to a corner table. Tonight’s plan: talk, vibe, and keep things chill.\n"
        ),
        choices=[
            Choice("a", "Sit and ask about their day.", "talk", adjust_comfort(+1)),
            Choice("b", "Crack a playful joke.", "joke", adjust_comfort(+0)),
            Choice("c", "Grab tea for both of you first.", "tea", adjust_comfort(+1)),
        ],
    )

    scenes["talk"] = Scene(
        key="talk",
        title="Small Talk, Big Smiles",
        body=(
            "They appreciate the gentle start. You trade stories about music and late-night coding experiments.\n"
            "They mention they love considerate people."
        ),
        choices=[
            Choice("a", "Suggest a low-key walk after tea (only if comfort ≥ 6).", "walk", adjust_comfort(+1), requires_comfort_at_least(6)),
            Choice("b", "Keep chatting about playlists.", "playlist"),
            Choice("m", "Open the menu.", "menu")
        ],
    )

    scenes["joke"] = Scene(
        key="joke",
        title="A Light Laugh",
        body=(
            "Your joke lands—sort of. They smile, then glance at the window. "
            "Maybe slow and thoughtful would work better."
        ),
        choices=[
            Choice("a", "Apologize lightly and pivot to music talk.", "playlist", adjust_comfort(+1)),
            Choice("m", "Open the menu.", "menu")
        ],
    )

    scenes["tea"] = Scene(
        key="tea",
        title="Warm Cups",
        body=(
            "You return with tea. The steam curls between you like a ribbon. "
            "They thank you, visibly relaxing."
        ),
        choices=[
            Choice("a", "Ask their favorite artists.", "playlist", adjust_comfort(+1)),
            Choice("m", "Open the menu.", "menu")
        ],
    )

    scenes["playlist"] = Scene(
        key="playlist",
        title="Soft Soundtrack",
        body=(
            "You trade recs—Clairo, Laufey, Bea. The vibe is gentle, respectful, and curious. "
            "They seem comfortable setting the pace."
        ),
        choices=[
            Choice("a", "Offer a hand for a brief dance by the window (comfort ≥ 7).", "dance", adjust_comfort(+1), requires_comfort_at_least(7)),
            Choice("b", "Keep it cozy; plan a future vinyl night.", "future", set_flag("vinyl_night")),
            Choice("m", "Open the menu.", "menu")
        ],
    )

    scenes["walk"] = Scene(
        key="walk",
        title="Rainlight Walk",
        body=(
            "Umbrellas up. Streetlights glow on the wet pavement. You match their pace and keep conversation easy."
        ),
        choices=[
            Choice("a", "End the night with a polite goodbye.", "ending_gentle", adjust_comfort(+1)),
            Choice("b", "Ask if they’d like to meet again soon.", "future", set_flag("meet_again"))
        ],
    )

    scenes["dance"] = Scene(
        key="dance",
        title="Window Waltz",
        body=(
            "A few slow steps near the window. Nothing more than a smile and relaxed shoulders. "
            "When they squeeze your hand back, you both laugh."
        ),
        choices=[
            Choice("a", "Thank them for the moment and return to the table.", "talk", adjust_comfort(+1)),
            Choice("b", "Call it a night on a high note.", "ending_gentle", adjust_comfort(+1))
        ],
    )

    scenes["future"] = Scene(
        key="future",
        title="Plans, Not Pressure",
        body=(
            "You trade numbers and sketch a future plan—vinyl night, maybe a tiny local show. "
            "Everything stays respectful and unrushed."
        ),
        choices=[
            Choice("a", "Wrap up the evening.", "ending_gentle"),
            Choice("m", "Open the menu.", "menu")
        ],
    )

    scenes["menu"] = Scene(
        key="menu",
        title="Menu",
        body=("Options:\n"
              "  [s] Save game\n"
              "  [l] Load game\n"
              "  [c] Check comfort meter\n"
              "  [b] Back to last scene\n"),
        choices=[
            Choice("s", "Save game.", "menu", lambda s: (save(s), print("Saved."))),
            Choice("l", "Load game.", "menu", lambda s: (loaded := load(), (s.__dict__.update(loaded.__dict__) if loaded else None, print("Loaded." if loaded else "No save found.")))),
            Choice("c", "Show comfort meter.", "menu", lambda s: print(f"Comfort: {s.meter['comfort']}/10")),
            Choice("b", "Back.", "back")
        ],
    )

    scenes["ending_gentle"] = Scene(
        key="ending_gentle",
        title="A Gentle Ending",
        body=(
            "You end the night kindly, leaving space for tomorrow. Respect, warmth, and good timing—perfect."
        ),
        choices=[
            Choice("r", "Replay from start.", "intro"),
            Choice("q", "Quit.", "quit")
        ],
    )

    return scenes

def run():
    state = load() or GameState()
    scenes = build_scenes()
    history: List[str] = []

    while True:
        clear()
        scene = scenes[state.scene_key]
        if scene.on_enter:
            scene.on_enter(state)

        print(f"== {scene.title} ==")
        print(scene.body)
        print()

        # Show valid choices considering requirements
        valid_choices = []
        for ch in scene.choices:
            if ch.requires and not ch.requires(state):
                continue
            valid_choices.append(ch)
            print(f"[{ch.key}] {ch.text}")

        # Special handling: "back" pseudo-scene
        choice_key = input("\nChoose: ").strip().lower()
        chosen = next((c for c in valid_choices if c.key == choice_key), None)
        if not chosen:
            print("Invalid choice. Press Enter.")
            input()
            continue

        if chosen.effect:
            chosen.effect(state)

        if chosen.next_scene == "quit":
            print("Goodbye!")
            break
        elif chosen.next_scene == "back":
            # Go back to previous scene if available
            if history:
                state.scene_key = history.pop()
            else:
                print("No previous scene. Press Enter.")
                input()
            continue
        else:
            history.append(state.scene_key)
            state.scene_key = chosen.next_scene

if __name__ == "__main__":
    run()

story = {
    "start": {
        "text": "You wake up in a mysterious forest. What do you do?",
        "image": "forest.jpg",
        "choices": {"Explore": None, "Wait": None},
        "music_tone": "neutral",
        "img_description": "forest in the fog",
    },
}

state = {"scene": "start"}

def get_current_scene():
    scene = story[state["scene"]]
    return scene["text"], scene["image"], scene["choices"].keys()
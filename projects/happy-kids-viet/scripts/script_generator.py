"""
Script Generator - Creates lyrics, metadata and scene descriptions from a topic.
Contains pre-built song templates + can generate new ones.
"""
import json
import os
import re

# === Pre-built Song Library ===
SONG_LIBRARY = {
    "colors": {
        "title": "Colors All Around",
        "series": "Learn Colors",
        "emoji": "🌈",
        "lyrics": [
            {"section": "Verse 1", "lines": [
                "Red like apples, red like fire,",
                "Blue like sky that goes so higher,",
                "Yellow sun shines bright today,",
                "Green like leaves that dance and sway!"
            ]},
            {"section": "Chorus", "lines": [
                "Colors, colors all around!",
                "Colors, colors can be found!",
                "Look with your eyes, what do you see?",
                "Colors make the world happy!"
            ]},
            {"section": "Verse 2", "lines": [
                "Orange pumpkin, orange light,",
                "Purple grapes, so sweet and bright,",
                "Pink flamingo stands so tall,",
                "Brown teddy bear, I love you all!"
            ]},
            {"section": "Chorus", "lines": [
                "Colors, colors all around!",
                "Colors, colors can be found!",
                "Look with your eyes, what do you see?",
                "Colors make the world happy!"
            ]},
            {"section": "Outro", "lines": [
                "Colors, colors, one two three,",
                "Colors make YOU and ME!"
            ]},
        ],
        "scene_descriptions": [
            {"text": "🍎 RED", "sub": "Red like apples!", "bg_colors": [(255,107,107), (220,50,50)]},
            {"text": "💙 BLUE", "sub": "Blue like sky!", "bg_colors": [(77,171,247), (41,128,185)]},
            {"text": "☀️ YELLOW", "sub": "Yellow sun shines!", "bg_colors": [(255,224,102), (243,156,18)]},
            {"text": "🌿 GREEN", "sub": "Green like leaves!", "bg_colors": [(105,219,124), (39,174,96)]},
            {"text": "🎵 COLORS!", "sub": "Colors all around!", "bg_colors": [(218,119,242), (142,68,173)]},
            {"text": "🎃 ORANGE", "sub": "Orange pumpkin!", "bg_colors": [(255,169,77), (230,126,34)]},
            {"text": "🍇 PURPLE", "sub": "Purple grapes!", "bg_colors": [(218,119,242), (155,89,182)]},
            {"text": "🦩 PINK", "sub": "Pink flamingo!", "bg_colors": [(247,131,172), (232,67,147)]},
            {"text": "🧸 BROWN", "sub": "Brown teddy bear!", "bg_colors": [(180,130,80), (139,90,43)]},
            {"text": "🌈 ALL COLORS!", "sub": "Colors make us happy!", "bg_colors": [(77,171,247), (218,119,242)]},
        ],
        "extra_tags": ["learn colors", "colors for kids", "color song", "rainbow colors"],
    },

    "counting": {
        "title": "Counting 1 to 10",
        "series": "Learn Numbers",
        "emoji": "🔢",
        "lyrics": [
            {"section": "Intro", "lines": [
                "One, two, three, let's count with me!"
            ]},
            {"section": "Verse 1", "lines": [
                "One little star up in the sky,",
                "Two little birds that fly so high,",
                "Three little fish swim in the sea,",
                "Four little bees, buzz buzz with me!"
            ]},
            {"section": "Chorus", "lines": [
                "1-2-3-4-5",
                "6-7-8-9-10!",
                "Let's count again, again, again!",
                "Counting is so fun, my friend!"
            ]},
            {"section": "Verse 2", "lines": [
                "Five little ducks go quack quack quack,",
                "Six little frogs go hop hop back,",
                "Seven balloons float up so high,",
                "Eight pretty clouds up in the sky!"
            ]},
            {"section": "Bridge", "lines": [
                "Nine little puppies run and play,",
                "Ten little flowers bloom today!"
            ]},
            {"section": "Outro", "lines": [
                "We counted 1 to 10 - hooray!"
            ]},
        ],
        "scene_descriptions": [
            {"text": "⭐ 1", "sub": "One little star!", "bg_colors": [(77,171,247), (41,128,185)]},
            {"text": "🐦 2", "sub": "Two little birds!", "bg_colors": [(105,219,124), (39,174,96)]},
            {"text": "🐟 3", "sub": "Three little fish!", "bg_colors": [(77,171,247), (52,152,219)]},
            {"text": "🐝 4", "sub": "Four little bees!", "bg_colors": [(255,224,102), (243,156,18)]},
            {"text": "🎵 1-2-3-4-5", "sub": "Let's count!", "bg_colors": [(218,119,242), (142,68,173)]},
            {"text": "🦆 5", "sub": "Five little ducks!", "bg_colors": [(255,169,77), (230,126,34)]},
            {"text": "🐸 6", "sub": "Six little frogs!", "bg_colors": [(105,219,124), (39,174,96)]},
            {"text": "🎈 7", "sub": "Seven balloons!", "bg_colors": [(255,107,107), (231,76,60)]},
            {"text": "☁️ 8", "sub": "Eight pretty clouds!", "bg_colors": [(77,171,247), (174,214,241)]},
            {"text": "🐶 9", "sub": "Nine little puppies!", "bg_colors": [(180,130,80), (139,90,43)]},
            {"text": "🌸 10", "sub": "Ten flowers!", "bg_colors": [(247,131,172), (232,67,147)]},
            {"text": "🎉 1 to 10!", "sub": "Hooray!", "bg_colors": [(255,224,102), (255,169,77)]},
        ],
        "extra_tags": ["counting 1-10", "numbers for kids", "counting song", "learn to count"],
    },

    "brush_teeth": {
        "title": "Brush Your Teeth",
        "series": "Good Habits",
        "emoji": "🦷",
        "lyrics": [
            {"section": "Intro", "lines": [
                "It's time to brush our teeth! Ready?"
            ]},
            {"section": "Verse 1", "lines": [
                "Wake up in the morning, what do we do?",
                "Grab our toothbrush, squeeze paste too!",
                "Up and down, and side to side,",
                "Open wide, there's nothing to hide!"
            ]},
            {"section": "Chorus", "lines": [
                "Brush brush brush your teeth!",
                "Brush them every day!",
                "Brush the front and brush the back,",
                "Shiny teeth - hooray hooray!"
            ]},
            {"section": "Verse 2", "lines": [
                "After breakfast, yummy treat,",
                "Brush those teeth so nice and neat!",
                "Before bedtime, almost done,",
                "Brushing teeth is so much fun!"
            ]},
            {"section": "Outro", "lines": [
                "Shiny teeth, healthy and bright,",
                "Brush in morning, brush at night!"
            ]},
        ],
        "scene_descriptions": [
            {"text": "🦷 BRUSH!", "sub": "Time to brush teeth!", "bg_colors": [(77,171,247), (41,128,185)]},
            {"text": "🌅 MORNING", "sub": "Wake up!", "bg_colors": [(255,224,102), (255,169,77)]},
            {"text": "🪥 TOOTHBRUSH", "sub": "Grab your brush!", "bg_colors": [(105,219,124), (39,174,96)]},
            {"text": "⬆️⬇️ UP DOWN", "sub": "Up and down!", "bg_colors": [(218,119,242), (142,68,173)]},
            {"text": "🎵 BRUSH!", "sub": "Brush every day!", "bg_colors": [(247,131,172), (232,67,147)]},
            {"text": "✨ FRONT", "sub": "Brush the front!", "bg_colors": [(77,171,247), (52,152,219)]},
            {"text": "✨ BACK", "sub": "Brush the back!", "bg_colors": [(255,169,77), (230,126,34)]},
            {"text": "😁 SHINY!", "sub": "Shiny teeth!", "bg_colors": [(255,224,102), (243,156,18)]},
            {"text": "🌙 BEDTIME", "sub": "Brush at night!", "bg_colors": [(44,62,80), (52,73,94)]},
            {"text": "⭐ HOORAY!", "sub": "Great job!", "bg_colors": [(105,219,124), (46,204,113)]},
        ],
        "extra_tags": ["brush teeth song", "dental hygiene kids", "good habits", "healthy habits"],
    },

    "abc": {
        "title": "ABC Phonics Song",
        "series": "Learn ABC",
        "emoji": "📚",
        "lyrics": [
            {"section": "Intro", "lines": [
                "A-B-C, sing with me!"
            ]},
            {"section": "Verse 1", "lines": [
                "A is for Apple, ah-ah-apple,",
                "B is for Ball, b-b-ball,",
                "C is for Cat, c-c-cat,",
                "D is for Dog, d-d-dog!"
            ]},
            {"section": "Verse 2", "lines": [
                "E is for Elephant, eh-eh-elephant,",
                "F is for Fish, f-f-fish,",
                "G is for Goat, g-g-goat,",
                "H is for Hat, h-h-hat!"
            ]},
            {"section": "Final Chorus", "lines": [
                "Now I know my ABC,",
                "Next time won't you sing with me?",
                "Letters help us read and write,",
                "Learning ABC is so bright!"
            ]},
        ],
        "scene_descriptions": [
            {"text": "🍎 A", "sub": "A is for Apple!", "bg_colors": [(255,107,107), (220,50,50)]},
            {"text": "⚽ B", "sub": "B is for Ball!", "bg_colors": [(77,171,247), (41,128,185)]},
            {"text": "🐱 C", "sub": "C is for Cat!", "bg_colors": [(255,169,77), (230,126,34)]},
            {"text": "🐕 D", "sub": "D is for Dog!", "bg_colors": [(180,130,80), (139,90,43)]},
            {"text": "🐘 E", "sub": "E is for Elephant!", "bg_colors": [(149,165,166), (127,140,141)]},
            {"text": "🐟 F", "sub": "F is for Fish!", "bg_colors": [(77,171,247), (52,152,219)]},
            {"text": "🐐 G", "sub": "G is for Goat!", "bg_colors": [(105,219,124), (39,174,96)]},
            {"text": "🎩 H", "sub": "H is for Hat!", "bg_colors": [(218,119,242), (155,89,182)]},
            {"text": "📚 ABC!", "sub": "Sing with me!", "bg_colors": [(255,224,102), (243,156,18)]},
        ],
        "extra_tags": ["abc song", "phonics for kids", "alphabet learning", "learn abc"],
    },

    "vegetables": {
        "title": "Eat Your Vegetables",
        "series": "Good Habits",
        "emoji": "🥕",
        "lyrics": [
            {"section": "Verse 1", "lines": [
                "Carrots are orange, crunchy and sweet,",
                "Broccoli trees are fun to eat,",
                "Green green peas, round and small,",
                "Yummy vegetables, I love them all!"
            ]},
            {"section": "Chorus", "lines": [
                "Veggies, veggies, good for you!",
                "Veggies, veggies, help you grew!",
                "Eat them up, yum yum yum!",
                "Vegetables make you strong!"
            ]},
            {"section": "Verse 2", "lines": [
                "Red tomatoes, round and bright,",
                "Corn so yellow, what a sight!",
                "Spinach leaves so green and good,",
                "Eat your veggies like you should!"
            ]},
            {"section": "Outro", "lines": [
                "Vegetables every day,",
                "Help us run and jump and play!"
            ]},
        ],
        "scene_descriptions": [
            {"text": "🥕 CARROT", "sub": "Orange and crunchy!", "bg_colors": [(255,169,77), (230,126,34)]},
            {"text": "🥦 BROCCOLI", "sub": "Fun to eat!", "bg_colors": [(105,219,124), (39,174,96)]},
            {"text": "🟢 PEAS", "sub": "Round and small!", "bg_colors": [(105,219,124), (46,204,113)]},
            {"text": "🎵 VEGGIES!", "sub": "Good for you!", "bg_colors": [(255,224,102), (243,156,18)]},
            {"text": "💪 STRONG!", "sub": "Yum yum yum!", "bg_colors": [(255,107,107), (231,76,60)]},
            {"text": "🍅 TOMATO", "sub": "Round and bright!", "bg_colors": [(255,107,107), (220,50,50)]},
            {"text": "🌽 CORN", "sub": "Yellow corn!", "bg_colors": [(255,224,102), (241,196,15)]},
            {"text": "🥬 SPINACH", "sub": "Green and good!", "bg_colors": [(105,219,124), (39,174,96)]},
            {"text": "🎉 EAT VEGGIES!", "sub": "Run, jump, play!", "bg_colors": [(77,171,247), (218,119,242)]},
        ],
        "extra_tags": ["eat vegetables song", "healthy food kids", "veggie song", "nutrition for kids"],
    },
}


def get_available_topics():
    """Return list of available pre-built topics."""
    return list(SONG_LIBRARY.keys())


def generate_script(topic):
    """
    Generate full script + metadata for a topic.
    Returns dict with lyrics, scenes, and YouTube metadata.
    """
    topic_key = topic.lower().replace(" ", "_")

    if topic_key not in SONG_LIBRARY:
        available = ", ".join(get_available_topics())
        raise ValueError(
            f"Topic '{topic}' not found. Available: {available}"
        )

    song = SONG_LIBRARY[topic_key]

    # Build full lyrics text
    lyrics_text = ""
    for section in song["lyrics"]:
        lyrics_text += f"[{section['section']}]\n"
        for line in section["lines"]:
            lyrics_text += f"{line}\n"
        lyrics_text += "\n"

    # Build YouTube metadata
    title = f"{song['emoji']} {song['title']} | {song['series']} | Happy Kids Việt"
    description = (
        f"🎵 {song['title']} - Learn {song['series']} with Happy Kids Việt!\n\n"
        f"In this video, kids will learn:\n"
        f"✅ {song['series']} through fun music\n"
        f"✅ New vocabulary words\n"
        f"✅ Important life skills\n\n"
        f"🔔 Subscribe for new videos every week!\n\n"
        f"#NurseryRhymes #KidsLearning #HappyKidsViet #{topic_key.title()}"
    )
    tags = song["extra_tags"] + [
        "nursery rhymes", "kids songs", "children songs",
        "educational videos for kids", "baby songs",
        "Happy Kids Viet",
    ]

    return {
        "topic": topic_key,
        "title": title,
        "raw_title": song["title"],
        "series": song["series"],
        "emoji": song["emoji"],
        "lyrics_text": lyrics_text,
        "lyrics_sections": song["lyrics"],
        "scene_descriptions": song["scene_descriptions"],
        "youtube": {
            "title": title,
            "description": description,
            "tags": tags,
            "category": "22",  # People & Blogs (for kids)
            "made_for_kids": True,
        },
    }


def save_script(script_data, output_dir):
    """Save script files to output directory."""
    # Save lyrics
    lyrics_path = os.path.join(output_dir, "lyrics.txt")
    with open(lyrics_path, "w", encoding="utf-8") as f:
        f.write(script_data["lyrics_text"])

    # Save metadata
    meta_path = os.path.join(output_dir, "metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(script_data["youtube"], f, indent=2, ensure_ascii=False)

    print(f"  ✅ Lyrics saved: {lyrics_path}")
    print(f"  ✅ Metadata saved: {meta_path}")
    return lyrics_path, meta_path


if __name__ == "__main__":
    print("Available topics:", get_available_topics())
    script = generate_script("colors")
    print(f"\nTitle: {script['title']}")
    print(f"\nLyrics:\n{script['lyrics_text']}")
    print(f"\nScenes: {len(script['scene_descriptions'])}")

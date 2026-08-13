import random
import sqlite3
import sys

CATEGORIES = {
    "Building Blocks": ["LegoLike", "MegaBricks", "BuildJoy", "BlockMaster"],
    "Soft Toys": ["CuddleCo", "PlushKing", "SoftHug", "TeddyLand"],
    "Action Figures": ["ActionMax", "PowerPlay", "HeroForce", "FigureWorks"],
    "Educational Toys": ["LearnFun", "SmartKidz", "BrightMind", "EduPlay"],
    "Dolls & Playsets": ["PlayHouse", "DollyWorld", "KidsCastle", "PrettyPlay"],
    "Outdoor & Sports": ["SportyKidz", "OutdoorFun", "JumpNPlay", "PlayActive"],
    "Remote Control Toys": ["AeroPlay", "SpeedX", "FlyHigh", "TurboToys"],
    "Board Games & Puzzles": ["PuzzleMania", "FunTable", "BrainBox", "GameNight"],
    "Art & Craft": ["CreativeHands", "ColorJoy", "CraftyKidz", "ArtSpark"],
    "Musical Toys": ["RhythmToys", "MusicJoy", "MelodyKidz", "SoundPlay"],
}

NAME_PREFIXES = [
    "City Builder Set", "Adventure Pack", "Fun Explorer Kit", "Deluxe Playset",
    "Junior Starter Set", "Classic Edition", "Mega Combo Pack", "Discovery Kit",
]

AGE_GROUPS = ["0-2", "3-5", "6-8", "9-12", "12+"]

DB_PATH = "database/toyshop.db"


def generate_record():
    category = random.choice(list(CATEGORIES.keys()))
    brand = random.choice(CATEGORIES[category])
    name = f"{random.choice(NAME_PREFIXES)}"
    age_group = random.choice(AGE_GROUPS)
    price = round(random.uniform(199.0, 4999.0), 2)
    stock_qty = random.randint(0, 50)
    delivery_days = random.randint(1, 10)
    return (name, category, brand, age_group, price, stock_qty, delivery_days)


def add_records(count: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    records = [generate_record() for _ in range(count)]
    cur.executemany(
        """
        INSERT INTO products (name, category, brand, age_group, price, stock_qty, delivery_days)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        records,
    )

    conn.commit()
    print(f"Inserted {count} records into products.")
    conn.close()


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    add_records(n)

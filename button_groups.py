main = [
        ['โ๏ธ Add Quest', '๐ฏ Add Side Quest'],
        ['๐ List Quests', '๐ List Side Quests'],
        ['๐ Player Status', '๐ Tokens']
        ]

importance = [["๐น Low", "๐ธ Medium", "๐บ High"]]
difficulty = [["๐ Low", "๐ Medium", "๐ High"]]


def quests(cat):
    return [
            ["โ Mark as done"],
            ["๐ Edit Name", "โ ๏ธ Change Priority"],
            ["๐ Change Difficulty", "๐ Delete " +
                {"quest": "Quest", "side_quest": "Side Quest"}[cat]],
            ["โฌ๏ธ Back"]]


tokens = [
        ["๐ List tokens"],
        ["๐ Generate token", "๐งน Delete token"]
        ]

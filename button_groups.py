main = [
        ['❇️ Add Quest', '📯 Add Side Quest'],
        ['📜 List Quests', '📃 List Side Quests'],
        ['🏅 Player Status']
        ]

importance = [["🔹 Low", "🔸 Medium", "🔺 High"]]
difficulty = [["📙 Low", "📘 Medium", "📗 High"]]


def quests(cat):
    return [
            ["✅ Mark as done"],
            ["📝 Edit Name", "⚠️ Change Priority"],
            ["📚 Change Difficulty", "🗑 Delete " +
                {"quest": "Quest", "side_quest": "Side Quest"}[cat]],
            ["⬅️ Back"]]

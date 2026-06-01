import emoji

text = "👨‍⚕️ AI-Augmented Doctor"
raw_words = text.split()
print("raw_words:", raw_words)

for idx, word in enumerate(raw_words):
    is_emoji = emoji.emoji_count(word) > 0
    has_alnum = any(c.isalnum() for c in word)
    print(f"Word '{word}' (length {len(word)}): is_emoji={is_emoji}, has_alnum={has_alnum}")

import emoji

text = "👨‍⚕️ AI-Augmented"
emoji_list = emoji.emoji_list(text)
print("emoji_list matches:")
for match in emoji_list:
    print(match)

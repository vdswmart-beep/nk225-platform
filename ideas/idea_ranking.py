# ideas/idea_ranking.py

class IdeaRanker:
    def __init__(self, long_threshold=70, short_threshold=30):
        self.long_threshold = long_threshold
        self.short_threshold = short_threshold

    def rank(self, df):
        df = df.copy()

        longs = df[df["research_score"] >= self.long_threshold]
        shorts = df[df["research_score"] <= self.short_threshold]

        longs = longs.sort_values("research_score", ascending=False)
        shorts = shorts.sort_values("research_score", ascending=True)

        return longs, shorts

    def compute_conviction(self, score):
        if score > 85:
            return "HIGH"
        elif score > 70:
            return "MEDIUM"
        elif score < 15:
            return "HIGH"
        elif score < 30:
            return "MEDIUM"
        return "LOW"
class RootCauseServices:

    def analyze(
        self,
        correlations: list
    ):

        if not correlations:
            return {
                "root_cause":
                    "No obvious root cause identified",
                "severity":
                    "normal"
            }

        best_match = max(
            correlations,
            key=lambda x: x["confidence"]
        )

        return {
            "root_cause":
                best_match["finding"],

            "severity":
                best_match["severity"],

            "confidence":
                best_match["confidence"]
        }
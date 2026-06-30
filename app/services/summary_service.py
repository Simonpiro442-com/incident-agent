class SummaryService:

    def generate(
        self,
        service_name: str,
        pod_data: dict,
        metrics: dict,
        correlations: list,
        root_cause: dict
    ):

        lines = []

        lines.append(
            "INCIDENT SUMMARY"
        )

        lines.append("")

        lines.append(
            f"Service: {service_name}"
        )

        lines.append("")

        #
        # Findings
        #
        lines.append(
            "Findings:"
        )

        total_restarts = (
            pod_data.get(
                "total_restarts",
                0
            )
        )

        lines.append(
            f"- Pod restarted {total_restarts} times"
        )

        for finding in correlations:

            lines.append(
                f"- {finding['finding']}"
            )

        lines.append("")

        #
        # Metrics
        #
        lines.append(
            "Metrics:"
        )

        memory_mb = round(
            metrics.get(
                "memory_bytes",
                0
            ) / 1024 / 1024,
            2
        )

        cpu_usage = round(
            metrics.get(
                "cpu_usage",
                0
            ),
            4
        )

        network_usage = round(
            metrics.get(
                "network_bytes_per_second",
                0
            ),
            2
        )

        pod_count = (
            metrics.get(
                "pod_count",
                0
            )
        )

        lines.append(
            f"- Pod Count: {pod_count}"
        )

        lines.append(
            f"- Memory Usage: {memory_mb} MB"
        )

        lines.append(
            f"- CPU Usage: {cpu_usage}"
        )

        lines.append(
            f"- Network Usage: {network_usage} bytes/sec"
        )

        lines.append("")

        #
        # Root Cause
        #
        lines.append(
            "Probable Root Cause:"
        )

        lines.append(
            root_cause.get(
                "root_cause",
                "Unknown"
            )
        )

        lines.append("")

        #
        # Confidence
        #
        confidence = (
            root_cause.get(
                "confidence",
                0
            )
        )

        confidence_pct = int(
            confidence * 100
        )

        lines.append(
            f"Confidence: {confidence_pct}%"
        )

        return "\n".join(lines)
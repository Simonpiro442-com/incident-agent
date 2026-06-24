class CorrelationService:

    def correlate(
        self,
        pod_data: dict,
        deployment_data: dict,
        event_data: dict,
        resource_analysis: list
    ):

        findings = []

        total_restarts = pod_data.get(
            "total_restarts",
            0
        )

        deployment_found = deployment_data.get(
            "deployment_found",
            False
        )

        deployment_age_minutes = (
            deployment_data.get(
                "deployment_age_minutes",
                999999
            )
        )

        events = event_data.get(
            "events",
            []
        )

        event_reasons = {
            event["reason"]
            for event in events
        }

        #
        # Rule 1:
        # Recent deployment + restarts
        #
        if (
            deployment_found
            and deployment_age_minutes < 30
            and total_restarts > 5
        ):
            findings.append(
                {
                    "severity": "high",
                    "confidence": 0.90,
                    "finding": (
                        "Recent deployment correlates "
                        "with increased pod restarts"
                    )
                }
            )

        #
        # Rule 2:
        # CrashLoop
        #
        if "BackOff" in event_reasons:

            findings.append(
                {
                    "severity": "critical",
                    "confidence": 0.95,
                    "finding": (
                        "Container crash loop detected"
                    )
                }
            )

        #
        # Rule 3:
        # Scheduling issue
        #
        if "FailedScheduling" in event_reasons:

            findings.append(
                {
                    "severity": "critical",
                    "confidence": 0.95,
                    "finding": (
                        "Pod scheduling issue detected"
                    )
                }
            )

        #
        # Rule 4:
        # Image pull issues
        #
        if (
            "ImagePullBackOff" in event_reasons
            or "ErrImagePull" in event_reasons
        ):
            findings.append(
                {
                    "severity": "critical",
                    "confidence": 0.99,
                    "finding": (
                        "Container image pull failure detected"
                    )
                }
            )

        #
        # Rule 5:
        # OOMKilled
        #
        for pod in resource_analysis:

            if (
                pod.get(
                    "last_termination_reason"
                )
                == "OOMKilled"
            ):

                findings.append(
                    {
                        "severity": "critical",
                        "confidence": 0.98,
                        "finding": (
                            "Application exceeded memory limits"
                        )
                    }
                )

        #
        # Rule 6:
        # Excessive restarts
        #
        if total_restarts > 20:

            findings.append(
                {
                    "severity": "warning",
                    "confidence": 0.75,
                    "finding": (
                        "Excessive pod restarts observed"
                    )
                }
            )

        #
        # Rule 7:
        # Pending pods
        #
        for pod in resource_analysis:

            if pod.get("phase") == "Pending":

                findings.append(
                    {
                        "severity": "warning",
                        "confidence": 0.80,
                        "finding": (
                            "Pods remain pending"
                        )
                    }
                )

        return findings
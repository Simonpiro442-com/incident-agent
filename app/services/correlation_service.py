class CorrelationService:

    def correlate(
        self,
        pod_data: dict,
        deployment_data: dict,
        event_data: dict,
        resource_analysis: list,
        metrics: dict
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

        memory_bytes = (
            metrics.get(
                "memory_bytes",
                0
            )
        )

        cpu_usage = (
            metrics.get(
                "cpu_usage",
                0
            )
        )

        pod_count = (
            metrics.get(
                "pod_count",
                0
            )
        )

        event_reasons = {
            event["reason"]
            for event in events
        }

        #
        # Rule 1
        # Recent deployment + restart spike
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
        # Rule 2
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
        # Rule 3
        # Scheduling failure
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
        # Rule 4
        # Image pull issue
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
        # Rule 5
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

            # Previous container Failure

            if (
                pod.get(
                    "last_termination_reason"
                )
                == "Error"
            ): 
                findings.append(
                    {
                        "severity": "warning", 
                        "confidence": 0.70, 
                        "finding": (
                            "container previously terminated with an error"
                        )
                    }
                )
            
            #Error + Restart Activity
            
            if (
                pod.get(
                    "last_termination_reason"
                )
                == "Error"
                and total_restarts >= 5
            ):
               findings.append(
                  {
                    "severity": "high", 
                    "confidence": 0.85, 
                    "finding": (
                        "Repeated container failure detected"
                    )
                  }
               )
            
            #Non-zero exit code
            exit_code = (
                pod.get(
                    "exit_code"
                )
            )
            if (
                exit_code is not None
                and exit_code != 0
            ): 
               findings.append(
                  {
                    "severity": "warning", 
                    "confidence": 0.75, 
                    "finding": (
                        f"Container exited with code {exit_code}"
                    )
                  }
               )
            
            #Exit code 255

            if (
                pod.get(
                    "exit_code"
                )
                == 255
            ): 
               findings.append(
                  {
                    "severity": "high", 
                    "confidence": 0.90, 
                    "findings": (
                        "Application terminated with exit code 255"
                    )
                  }
               )

            #Exit code 255 + Restarts
            if (
                pod.get(
                    "exit_code"
                )
                == 255
                and total_restarts >= 5
            ): 
               findings.append(
                 {
                    "severity": "critical", 
                    "confidence": 0.95, 
                    "findings": (
                        "Application repeatedly terminated with exit code 255"
                    )
                 }
               )


        #
        # Rule 6
        # High memory + OOMKilled
        #
        if memory_bytes > 500_000_000:

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
                            "confidence": 0.99,
                            "finding": (
                                "Memory exhaustion strongly indicated"
                            )
                        }
                    )

        #
        # Rule 7
        # High memory + restart spike
        #
        if (
            memory_bytes > 500_000_000
            and total_restarts > 5
        ):

            findings.append(
                {
                    "severity": "high",
                    "confidence": 0.90,
                    "finding": (
                        "Memory pressure correlates with restart activity"
                    )
                }
            )

        #
        # Rule 8
        # CPU saturation
        #
        if cpu_usage > 1:

            findings.append(
                {
                    "severity": "warning",
                    "confidence": 0.75,
                    "finding": (
                        "High CPU utilization detected"
                    )
                }
            )

        #
        # Rule 9
        # High CPU after deployment
        #
        if (
            cpu_usage > 1
            and deployment_found
            and deployment_age_minutes < 30
        ):

            findings.append(
                {
                    "severity": "high",
                    "confidence": 0.90,
                    "finding": (
                        "Recent deployment correlates with CPU increase"
                    )
                }
            )

        #
        # Rule 10
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
        # Rule 11
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

        #
        # Rule 12
        # Unexpected pod disappearance
        #
        if pod_count == 0:

            findings.append(
                {
                    "severity": "critical",
                    "confidence": 0.99,
                    "finding": (
                        "No running pods detected"
                    )
                }
            )

        return findings
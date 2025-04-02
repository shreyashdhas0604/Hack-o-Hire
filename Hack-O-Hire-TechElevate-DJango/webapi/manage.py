#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapi.settings')

    DjangoInstrumentor().instrument()
    LoggingInstrumentor().instrument()

    jaeger_exporter = JaegerExporter(
        agent_host_name=os.getenv("TRACING_HOST"),
        # agent_port= int(os.getenv("TRACING_PORT")),
        agent_port = int(os.getenv("TRACING_PORT", "4317"))  # Default to 4317

    )
    trace.set_tracer_provider(TracerProvider(
        resource=Resource.create({SERVICE_NAME: 'webapi'})
    ))
    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

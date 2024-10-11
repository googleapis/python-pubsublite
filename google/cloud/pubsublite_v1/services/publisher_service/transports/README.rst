
transport inheritance structure
_______________________________

`PublisherServiceTransport` is the ABC for all transports.
- public child `PublisherServiceGrpcTransport` for sync gRPC transport (defined in `grpc.py`).
- public child `PublisherServiceGrpcAsyncIOTransport` for async gRPC transport (defined in `grpc_asyncio.py`).
- private child `_BasePublisherServiceRestTransport` for base REST transport with inner classes `_BaseMETHOD` (defined in `rest_base.py`).
- public child `PublisherServiceRestTransport` for sync REST transport with inner classes `METHOD` derived from the parent's corresponding `_BaseMETHOD` classes (defined in `rest.py`).

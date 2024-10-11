
transport inheritance structure
_______________________________

`SubscriberServiceTransport` is the ABC for all transports.
- public child `SubscriberServiceGrpcTransport` for sync gRPC transport (defined in `grpc.py`).
- public child `SubscriberServiceGrpcAsyncIOTransport` for async gRPC transport (defined in `grpc_asyncio.py`).
- private child `_BaseSubscriberServiceRestTransport` for base REST transport with inner classes `_BaseMETHOD` (defined in `rest_base.py`).
- public child `SubscriberServiceRestTransport` for sync REST transport with inner classes `METHOD` derived from the parent's corresponding `_BaseMETHOD` classes (defined in `rest.py`).

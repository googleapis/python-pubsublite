
transport inheritance structure
_______________________________

`CursorServiceTransport` is the ABC for all transports.
- public child `CursorServiceGrpcTransport` for sync gRPC transport (defined in `grpc.py`).
- public child `CursorServiceGrpcAsyncIOTransport` for async gRPC transport (defined in `grpc_asyncio.py`).
- private child `_BaseCursorServiceRestTransport` for base REST transport with inner classes `_BaseMETHOD` (defined in `rest_base.py`).
- public child `CursorServiceRestTransport` for sync REST transport with inner classes `METHOD` derived from the parent's corresponding `_BaseMETHOD` classes (defined in `rest.py`).

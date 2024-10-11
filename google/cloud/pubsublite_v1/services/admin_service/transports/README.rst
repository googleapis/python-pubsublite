
transport inheritance structure
_______________________________

`AdminServiceTransport` is the ABC for all transports.
- public child `AdminServiceGrpcTransport` for sync gRPC transport (defined in `grpc.py`).
- public child `AdminServiceGrpcAsyncIOTransport` for async gRPC transport (defined in `grpc_asyncio.py`).
- private child `_BaseAdminServiceRestTransport` for base REST transport with inner classes `_BaseMETHOD` (defined in `rest_base.py`).
- public child `AdminServiceRestTransport` for sync REST transport with inner classes `METHOD` derived from the parent's corresponding `_BaseMETHOD` classes (defined in `rest.py`).

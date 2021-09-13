# Changelog

### [1.1.2](https://www.github.com/googleapis/python-pubsublite/compare/v1.1.1...v1.1.2) (2021-09-13)


### Bug Fixes

* Enable pytype on Pub/Sub Lite repo and fix all errors ([#214](https://www.github.com/googleapis/python-pubsublite/issues/214)) ([df58fdf](https://www.github.com/googleapis/python-pubsublite/commit/df58fdfc83bdc4f6f753f664365a0ff26d3201e7))
* performance issues with subscriber client ([#232](https://www.github.com/googleapis/python-pubsublite/issues/232)) ([78a47b2](https://www.github.com/googleapis/python-pubsublite/commit/78a47b2817bee4a468f8ce15fe437165be1d1458))

### [1.1.1](https://www.github.com/googleapis/python-pubsublite/compare/v1.1.0...v1.1.1) (2021-09-07)


### Bug Fixes

* Add workaround for https://github.com/grpc/grpc/issues/25364 ([#213](https://www.github.com/googleapis/python-pubsublite/issues/213)) ([e417bf3](https://www.github.com/googleapis/python-pubsublite/commit/e417bf39fe32c995e5ac2e0a807a10fee3f37d9f))
* Numerous small performance and correctness issues ([#211](https://www.github.com/googleapis/python-pubsublite/issues/211)) ([358a1d8](https://www.github.com/googleapis/python-pubsublite/commit/358a1d8a429086ee75373260eb087a9dd171e3e6))

## [1.1.0](https://www.github.com/googleapis/python-pubsublite/compare/v1.0.2...v1.1.0) (2021-08-12)


### Features

* Support seek subscription in AdminClient ([#176](https://www.github.com/googleapis/python-pubsublite/issues/176)) ([fc648ae](https://www.github.com/googleapis/python-pubsublite/commit/fc648ae224c22564fa86fbc0eceaf40a0b109d4c))

### [1.0.2](https://www.github.com/googleapis/python-pubsublite/compare/v1.0.1...v1.0.2) (2021-08-04)


### Bug Fixes

* Backlog never zero despite messages received ([#204](https://www.github.com/googleapis/python-pubsublite/issues/204)) ([b93a0bf](https://www.github.com/googleapis/python-pubsublite/commit/b93a0bf1fda1079900278a022455b001d6fde86f))
* Increment ack generation id ([#203](https://www.github.com/googleapis/python-pubsublite/issues/203)) ([644163d](https://www.github.com/googleapis/python-pubsublite/commit/644163d2adc067372c379c617d570497b3f9354e))

### [1.0.1](https://www.github.com/googleapis/python-pubsublite/compare/v1.0.0...v1.0.1) (2021-07-28)


### Bug Fixes

* enable self signed jwt for grpc ([#199](https://www.github.com/googleapis/python-pubsublite/issues/199)) ([b8b9832](https://www.github.com/googleapis/python-pubsublite/commit/b8b983261eccfe63a5f4c9a77e6958f84bf6c91c))


### Documentation

* add Samples section to CONTRIBUTING.rst ([#196](https://www.github.com/googleapis/python-pubsublite/issues/196)) ([35b7dca](https://www.github.com/googleapis/python-pubsublite/commit/35b7dcabff683196fc4ccc0d0873238e2030a137))


### Miscellaneous Chores

* release as 1.0.1 ([#200](https://www.github.com/googleapis/python-pubsublite/issues/200)) ([51390f3](https://www.github.com/googleapis/python-pubsublite/commit/51390f363ce082dfb35e9a3f0981d8620628b1a3))

## [1.0.0](https://www.github.com/googleapis/python-pubsublite/compare/v0.6.1...v1.0.0) (2021-07-19)


### Features

* bump release level to production/stable ([#146](https://www.github.com/googleapis/python-pubsublite/issues/146)) ([4c294f2](https://www.github.com/googleapis/python-pubsublite/commit/4c294f262d882bcf7adc8ca96a1cbb8268fd39d5))


### Miscellaneous Chores

* release as 1.0.0 ([#193](https://www.github.com/googleapis/python-pubsublite/issues/193)) ([88368c6](https://www.github.com/googleapis/python-pubsublite/commit/88368c6826525ee74fe63efc89dda3acb670c130))

### [0.6.1](https://www.github.com/googleapis/python-pubsublite/compare/v0.6.0...v0.6.1) (2021-07-16)


### Bug Fixes

* Add ClientCache which forces new client creation after 75 uses ([#188](https://www.github.com/googleapis/python-pubsublite/issues/188)) ([089789c](https://www.github.com/googleapis/python-pubsublite/commit/089789c54e876615157ec7e05b79000fc93e2dd9))

## [0.6.0](https://www.github.com/googleapis/python-pubsublite/compare/v0.5.0...v0.6.0) (2021-07-13)


### Features

* add always_use_jwt_access ([6c84e24](https://www.github.com/googleapis/python-pubsublite/commit/6c84e24ce6e3e0c50f2807c2e98db47fe0424715))
* Add SeekSubscription and Operations to API ([#169](https://www.github.com/googleapis/python-pubsublite/issues/169)) ([2e29ba1](https://www.github.com/googleapis/python-pubsublite/commit/2e29ba1f39f299acf97e543db355bf8ebfcdf121))


### Bug Fixes

* **deps:** add packaging requirement ([#162](https://www.github.com/googleapis/python-pubsublite/issues/162)) ([94281c5](https://www.github.com/googleapis/python-pubsublite/commit/94281c5b925b550c0e0905e3f53ec9d23c45b499))
* disable always_use_jwt_access ([#175](https://www.github.com/googleapis/python-pubsublite/issues/175)) ([6c84e24](https://www.github.com/googleapis/python-pubsublite/commit/6c84e24ce6e3e0c50f2807c2e98db47fe0424715))
* exclude docs and tests from package ([#161](https://www.github.com/googleapis/python-pubsublite/issues/161)) ([b8a70d9](https://www.github.com/googleapis/python-pubsublite/commit/b8a70d9bafca7d62351404421c465e9dfc466420))
* is_reset_signal should handle status that is None ([#183](https://www.github.com/googleapis/python-pubsublite/issues/183)) ([4ba484e](https://www.github.com/googleapis/python-pubsublite/commit/4ba484e1c5f8ff458a4ad462167f8907b44ebe28))


### Documentation

* omit mention of Python 2.7 in 'CONTRIBUTING.rst' ([#1127](https://www.github.com/googleapis/python-pubsublite/issues/1127)) ([#165](https://www.github.com/googleapis/python-pubsublite/issues/165)) ([cea99be](https://www.github.com/googleapis/python-pubsublite/commit/cea99be19a5415796eaddf7f51ca4bcd4af9f75f))

## [0.5.0](https://www.github.com/googleapis/python-pubsublite/compare/v0.4.1...v0.5.0) (2021-06-11)


### Features

* Add Pub/Sub Lite Reservation APIs ([#156](https://www.github.com/googleapis/python-pubsublite/issues/156)) ([edbd104](https://www.github.com/googleapis/python-pubsublite/commit/edbd1046e38c14fcce8f4c20822eb124b026d925))
* ComputeTimeCursor RPC for Pub/Sub Lite ([#143](https://www.github.com/googleapis/python-pubsublite/issues/143)) ([036ca2f](https://www.github.com/googleapis/python-pubsublite/commit/036ca2f1a93f9892262c3ac833b10c8345dddeb6))
* Handle out of band seeks ([#158](https://www.github.com/googleapis/python-pubsublite/issues/158)) ([77db700](https://www.github.com/googleapis/python-pubsublite/commit/77db700ad966f0743d1b16897a9423d38dc5099a))


### Bug Fixes

* Add admin interfaces for reservations ([#159](https://www.github.com/googleapis/python-pubsublite/issues/159)) ([ad0f3d2](https://www.github.com/googleapis/python-pubsublite/commit/ad0f3d298ec9979ff558c2bb7fc73b53638db2ac))
* Replace unreleased InitialSubscribeRequest initial_cursor field with initial_location ([#150](https://www.github.com/googleapis/python-pubsublite/issues/150)) ([30fcd3f](https://www.github.com/googleapis/python-pubsublite/commit/30fcd3f6712bf02bc6eb2cce5729751d77e89d8b))
* shutdown event loop if publisher fails to start and set exception on result future ([#124](https://www.github.com/googleapis/python-pubsublite/issues/124)) ([c2c2b00](https://www.github.com/googleapis/python-pubsublite/commit/c2c2b00f0141af6f6d26ff095431de547deab96d))
* Version bump overrides library past fix and undo workarounds ([#137](https://www.github.com/googleapis/python-pubsublite/issues/137)) ([94ae2f0](https://www.github.com/googleapis/python-pubsublite/commit/94ae2f04a85f94b6cffa2241d68068c292157c56))

### [0.4.1](https://www.github.com/googleapis/python-pubsublite/compare/v0.4.0...v0.4.1) (2021-05-05)


### Bug Fixes

* Change type hint on callback to be Callback. ([#135](https://www.github.com/googleapis/python-pubsublite/issues/135)) ([cbf16f8](https://www.github.com/googleapis/python-pubsublite/commit/cbf16f8c1737f1986ff1976e2bc5b2509b974389))
* **deps:** remove duplicate dependencies and add version ranges ([#105](https://www.github.com/googleapis/python-pubsublite/issues/105)) ([d7ee309](https://www.github.com/googleapis/python-pubsublite/commit/d7ee309b2578e375783256df7954d67d238f3ea6))
* do not crash if pubsublite distribution can not be found when extracting semver ([#120](https://www.github.com/googleapis/python-pubsublite/issues/120)) ([811434e](https://www.github.com/googleapis/python-pubsublite/commit/811434ea700e437c28cd97490db7a6f8edc5f47d))
* Remove Future type hint from return type which fails to type check when overridden ([#133](https://www.github.com/googleapis/python-pubsublite/issues/133)) ([abe9b14](https://www.github.com/googleapis/python-pubsublite/commit/abe9b147e1673708bf581fe92d9bf7cef26c7429))

## [0.4.0](https://www.github.com/googleapis/python-pubsublite/compare/v0.3.0...v0.4.0) (2021-03-22)


### Features

* adding ability to create subscriptions at HEAD ([#106](https://www.github.com/googleapis/python-pubsublite/issues/106)) ([4d03d3a](https://www.github.com/googleapis/python-pubsublite/commit/4d03d3a8ae8089fea87f5acd02a170697fa136fc))

## [0.3.0](https://www.github.com/googleapis/python-pubsublite/compare/v0.2.0...v0.3.0) (2021-03-09)


### Features

* Make message_id encode a PublishMetadata which includes the partition ([#90](https://www.github.com/googleapis/python-pubsublite/issues/90)) ([85944e7](https://www.github.com/googleapis/python-pubsublite/commit/85944e786908d0dd240b6c099cfd969045eecbd3))


### Bug Fixes

* remove absl dependency ([#94](https://www.github.com/googleapis/python-pubsublite/issues/94)) ([0573edb](https://www.github.com/googleapis/python-pubsublite/commit/0573edbefdf2612b2006b51829d1fd8fa636de3c))
* Rename PublishMetadata to MessageMetadata ([#92](https://www.github.com/googleapis/python-pubsublite/issues/92)) ([a744441](https://www.github.com/googleapis/python-pubsublite/commit/a7444418d1e2822bcaee0da3aa036c6a14cf8a6e))


### Documentation

* remove multiprocessing note ([#82](https://www.github.com/googleapis/python-pubsublite/issues/82)) ([a8d26a1](https://www.github.com/googleapis/python-pubsublite/commit/a8d26a11db301d7dc7a97ff7f7405d82bcf0a910))

## [0.2.0](https://www.github.com/googleapis/python-pubsublite/compare/v0.1.0...v0.2.0) (2020-12-14)


### Features

* Add support for increasing partitions in python ([#74](https://www.github.com/googleapis/python-pubsublite/issues/74)) ([e117a1a](https://www.github.com/googleapis/python-pubsublite/commit/e117a1aab8abe70f5b867395e3349053c7592aa7))


### Bug Fixes

* Fix type hints in paths now that string projects are allowed. ([#75](https://www.github.com/googleapis/python-pubsublite/issues/75)) ([b5ffc42](https://www.github.com/googleapis/python-pubsublite/commit/b5ffc423685596a309a7cee63f92c80ad5d74f07))

## 0.1.0 (2020-11-19)


### Features

* generate v1 ([4624ac7](https://www.github.com/googleapis/python-pubsublite/commit/4624ac7f6fb3fed3795222afce068c9b3de9be0f))
* Implement a single partition publisher ([#8](https://www.github.com/googleapis/python-pubsublite/issues/8)) ([fd1d76f](https://www.github.com/googleapis/python-pubsublite/commit/fd1d76fd4147b499be225b2085dbfe4b114f288d))
* Implement AckSetTracker which tracks message acknowledgements. ([#19](https://www.github.com/googleapis/python-pubsublite/issues/19)) ([7f88458](https://www.github.com/googleapis/python-pubsublite/commit/7f88458a5d1b97065eb725edaa1aa60a1c467fcc))
* Implement admin client. ([#17](https://www.github.com/googleapis/python-pubsublite/issues/17)) ([3068da5](https://www.github.com/googleapis/python-pubsublite/commit/3068da54f78de7e9c0e5a14b328c290f446bac82))
* Implement assigner, which handles partition-subscriber assignment. ([#14](https://www.github.com/googleapis/python-pubsublite/issues/14)) ([b2d0d36](https://www.github.com/googleapis/python-pubsublite/commit/b2d0d36ee08249caa7a1d7f16aa7eb3bdb454cd0))
* implement assigning subscriber ([#23](https://www.github.com/googleapis/python-pubsublite/issues/23)) ([6afd477](https://www.github.com/googleapis/python-pubsublite/commit/6afd477e2f17cc534b8bf8a2f4fc30cca951e248))
* Implement committer ([#13](https://www.github.com/googleapis/python-pubsublite/issues/13)) ([aa9aca8](https://www.github.com/googleapis/python-pubsublite/commit/aa9aca83f7a02fc92a87ec49c4d050e6e3137d15))
* Implement CPS non-asyncio subscriber ([#25](https://www.github.com/googleapis/python-pubsublite/issues/25)) ([a9293c1](https://www.github.com/googleapis/python-pubsublite/commit/a9293c14303e0fa045a15af3e8dde99260cabece))
* implement Flow control batcher ([#15](https://www.github.com/googleapis/python-pubsublite/issues/15)) ([0a09bb3](https://www.github.com/googleapis/python-pubsublite/commit/0a09bb3170f06532d5e5d8e1b5f8f3fddd516f98))
* Implement make_publisher which creates a routing publisher. ([#11](https://www.github.com/googleapis/python-pubsublite/issues/11)) ([baeb0f6](https://www.github.com/googleapis/python-pubsublite/commit/baeb0f6b5bf6032ad7d5ad9af523afe0ff72c235))
* Implement Publisher and subscriber factories ([#24](https://www.github.com/googleapis/python-pubsublite/issues/24)) ([4890cae](https://www.github.com/googleapis/python-pubsublite/commit/4890cae26a8e8dae222ef2e24c169b67f7987295))
* Implement Publisher API ([#21](https://www.github.com/googleapis/python-pubsublite/issues/21)) ([58fda6f](https://www.github.com/googleapis/python-pubsublite/commit/58fda6fb7041cd05b7ac6fb8915e1588d2200651))
* Implement python retrying connection, which generically retries stream errors ([#4](https://www.github.com/googleapis/python-pubsublite/issues/4)) ([11c9a69](https://www.github.com/googleapis/python-pubsublite/commit/11c9a690abbc648a57b801458f6193d02d5262d2))
* Implement RoutingPolicy ([#5](https://www.github.com/googleapis/python-pubsublite/issues/5)) ([f72a2f0](https://www.github.com/googleapis/python-pubsublite/commit/f72a2f0b8452b4598ae901073cfc06ca017079fe)), closes [#4](https://www.github.com/googleapis/python-pubsublite/issues/4)
* Implement RoutingPublisher which routes between publishers. ([#10](https://www.github.com/googleapis/python-pubsublite/issues/10)) ([7aa39a1](https://www.github.com/googleapis/python-pubsublite/commit/7aa39a13d557d1fa50c0573e2bf7c1f9107885b2))
* Implement SerialBatcher which helps with transforming single writes into batch writes. ([#7](https://www.github.com/googleapis/python-pubsublite/issues/7)) ([a6dc15f](https://www.github.com/googleapis/python-pubsublite/commit/a6dc15fb654a21374daecbfc1d24e72d555f4f8a))
* Implement SinglePartitionSubscriber. ([#22](https://www.github.com/googleapis/python-pubsublite/issues/22)) ([bb76d90](https://www.github.com/googleapis/python-pubsublite/commit/bb76d90ca9de7704c8bfee968af222b34d5b0306))
* Implement Subscriber, which handles flow control and batch message processing. ([#16](https://www.github.com/googleapis/python-pubsublite/issues/16)) ([697df4a](https://www.github.com/googleapis/python-pubsublite/commit/697df4a604c5b03378fbb9327f4f041c2d1949ce))
* Implement transforms to/from Cloud Pub/Sub Messages ([#20](https://www.github.com/googleapis/python-pubsublite/issues/20)) ([903070d](https://www.github.com/googleapis/python-pubsublite/commit/903070df3f57220745cf1588287a3ad6de21a046))
* Wire batching settings through publisher client factories ([#42](https://www.github.com/googleapis/python-pubsublite/issues/42)) ([a037d0b](https://www.github.com/googleapis/python-pubsublite/commit/a037d0b8073724aea144bf08c1bd78080df6f0d9))


### Bug Fixes

* Assorted fixes to the publish layer and internals. ([#39](https://www.github.com/googleapis/python-pubsublite/issues/39)) ([4276882](https://www.github.com/googleapis/python-pubsublite/commit/4276882d3fa81ddd5476ace630c2b6ee2221fdfc))
* Enforce that __enter__ is called on all user interfaces before use ([#70](https://www.github.com/googleapis/python-pubsublite/issues/70)) ([eb8d63a](https://www.github.com/googleapis/python-pubsublite/commit/eb8d63ad5bfc8ef54b724dfe81ec5e84ac8d60cd))
* Ensure tasks are always awaited to remove shutdown errors ([#57](https://www.github.com/googleapis/python-pubsublite/issues/57)) ([7735d2f](https://www.github.com/googleapis/python-pubsublite/commit/7735d2fa4132c08afd76b599b3b6e8b4960c5d20))
* fix circular import due to make_admin_client and AdminClient being in the same file ([#34](https://www.github.com/googleapis/python-pubsublite/issues/34)) ([d631626](https://www.github.com/googleapis/python-pubsublite/commit/d6316263c727669a41e61c49c72f3549aec9942a))
* import from types ([#52](https://www.github.com/googleapis/python-pubsublite/issues/52)) ([e4199ff](https://www.github.com/googleapis/python-pubsublite/commit/e4199ff294c69df0a94c8afb807a9ab5374d6cbf))
* Make public API more similar to generated clients ([#56](https://www.github.com/googleapis/python-pubsublite/issues/56)) ([7cf02ae](https://www.github.com/googleapis/python-pubsublite/commit/7cf02aee1f36aa3657bab80bdd702dd4dc53a34e))
* Move FlowControlSettings to types ([#53](https://www.github.com/googleapis/python-pubsublite/issues/53)) ([457a74d](https://www.github.com/googleapis/python-pubsublite/commit/457a74d68ba62f8311838f7db9c6bc0179b51a2c))
* Move types to common directory ([#51](https://www.github.com/googleapis/python-pubsublite/issues/51)) ([45a8a71](https://www.github.com/googleapis/python-pubsublite/commit/45a8a714fb1ed8722466336651b2d860da9febf4))
* remaining issues with subscriber client ([#43](https://www.github.com/googleapis/python-pubsublite/issues/43)) ([ec19dfc](https://www.github.com/googleapis/python-pubsublite/commit/ec19dfc8192b9c85e28b7ae025792c226789528a))
* update cps async clients ([#41](https://www.github.com/googleapis/python-pubsublite/issues/41)) ([f41c228](https://www.github.com/googleapis/python-pubsublite/commit/f41c22841748b66af6429b7c61ba3186faa11102))
* update pubsub_context to correctly modify proto map fields ([#38](https://www.github.com/googleapis/python-pubsublite/issues/38)) ([860c443](https://www.github.com/googleapis/python-pubsublite/commit/860c443fe99dbb932dfdc946620423aa4357109c))


### Documentation

* add documentation ([#66](https://www.github.com/googleapis/python-pubsublite/issues/66)) ([fda26bc](https://www.github.com/googleapis/python-pubsublite/commit/fda26bcb2cbf91edb6061884d18a7401ad2c72cd))
* add documentation that Publisher and Subscriber must be used in a `with` block ([#55](https://www.github.com/googleapis/python-pubsublite/issues/55)) ([32bc302](https://www.github.com/googleapis/python-pubsublite/commit/32bc302cabe988ebe7b1ce8fe186dacf9a096e5a))

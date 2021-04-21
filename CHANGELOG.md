# Changelog

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

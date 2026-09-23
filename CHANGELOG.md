# Changelog

## [0.9.0](https://github.com/harshitpawar64/chessvision/compare/v0.8.0...v0.9.0) (2026-09-23)


### Features

* **board:** add pgn property to BoardPrediction ([8a33321](https://github.com/harshitpawar64/chessvision/commit/8a333217c98247a6c2f3991ae1097fed44257600))
* **cli:** add clipboard image fallback to board command ([db1db6b](https://github.com/harshitpawar64/chessvision/commit/db1db6ba97093876f56948868c83cffe2f06d11c))
* **cli:** add output option to pdf command for pgn export ([aeff387](https://github.com/harshitpawar64/chessvision/commit/aeff38718b5e8ce9f38fdab62fa95a015233225b))
* **pdf:** implement PDFPredictor for multi-page board prediction ([113d8e9](https://github.com/harshitpawar64/chessvision/commit/113d8e9eb252ff6c9eb9c19bb5512afe355acef0))
* **project:** support Python &gt;=3.11 ([e5a2094](https://github.com/harshitpawar64/chessvision/commit/e5a2094570716a82f63d776985568c785e62aecd))


### Performance Improvements

* **init:** implement lazy loading for top-level exports ([91e8ba9](https://github.com/harshitpawar64/chessvision/commit/91e8ba94f215fb7ebe273c333320c06fde19773d))


### Refactor

* **cli:** delegate pdf prediction to PDFPredictor ([1fc1167](https://github.com/harshitpawar64/chessvision/commit/1fc1167e9097eae2a11ca2342202bdea541af2c9))


### Documentation

* **readme:** update API usage examples ([48e3785](https://github.com/harshitpawar64/chessvision/commit/48e378563e8b735050f3dfd093d069dde9df9836))

## [0.8.0](https://github.com/harshitpawar64/chessvision/compare/v0.7.0...v0.8.0) (2026-09-19)


### Features

* **board:** infer turn automatically from piece positions ([f05dfda](https://github.com/harshitpawar64/chessvision/commit/f05dfda0ab470a3a12034a57e6e38e2e9abfbcf1))
* **cli:** add pdf command for multi-page board prediction ([f87ac43](https://github.com/harshitpawar64/chessvision/commit/f87ac4379b18b873eff7284e30445faf59651251))
* **cli:** default turn option to auto ([a6ae778](https://github.com/harshitpawar64/chessvision/commit/a6ae77836c82ffdcec305a4a25993754920e1592))
* **constants:** add AUTO to Turn enum with validation guard ([0df6223](https://github.com/harshitpawar64/chessvision/commit/0df6223179d931028d41d1014d15aa3c34772eec))
* **detector:** add hierarchical contour detection, otsu thresholding, and nms deduplication ([5993ab6](https://github.com/harshitpawar64/chessvision/commit/5993ab62f0ab28b5485f3bc4d69a111686478885))


### Refactor

* **cli:** modularize cli and test suite ([3d31040](https://github.com/harshitpawar64/chessvision/commit/3d31040bd1e74ff9bb030989dc009efc40f1a2e8))
* **cli:** support string labels in validation error reporting ([8f290fe](https://github.com/harshitpawar64/chessvision/commit/8f290fec5ad271c920eb4af8966bc802f19b103d))

## [0.7.0](https://github.com/harshitpawar64/chessvision/compare/v0.6.0...v0.7.0) (2026-09-18)


### Features

* **board:** infer castling rights automatically from piece positions ([66ecab0](https://github.com/harshitpawar64/chessvision/commit/66ecab0203a1b7fbdce9fab095c3a4d20fa4224e))
* **board:** infer orientation automatically from piece positions ([e37f57e](https://github.com/harshitpawar64/chessvision/commit/e37f57e3d8c7f565a7f45e781f6bea42dd6e6f81))
* **cli:** default castling option to auto ([fac4a52](https://github.com/harshitpawar64/chessvision/commit/fac4a52f24172f6386851570f1eee96b5ec9a40d))
* **cli:** default orientation option to auto ([c47b123](https://github.com/harshitpawar64/chessvision/commit/c47b123bb3210051a1a1e5a149e884f66db6ff15))
* **constants:** add AUTO to orientation enum with validation guards ([049ddec](https://github.com/harshitpawar64/chessvision/commit/049ddec95f5e1ba79fba8e0beff1b87066061cdf))


### Bug Fixes

* **classifier:** disable appauthor to prevent duplicate directories on Windows ([aca82bf](https://github.com/harshitpawar64/chessvision/commit/aca82bf0a23782ee8b506082ee9f42791172119f))


### Refactor

* **board:** decouple orientation from slice_board ([f4a7aa5](https://github.com/harshitpawar64/chessvision/commit/f4a7aa59b56cb0c784b4839c398e5142fb3d440d))
* replace Castling enum with string representation and CLI validation ([e247880](https://github.com/harshitpawar64/chessvision/commit/e247880ab552c2c99df236707c0e301e8a658ac8))

## [0.6.0](https://github.com/harshitpawar64/chessvision/compare/v0.5.0...v0.6.0) (2026-09-16)


### Features

* **board:** add board property to BoardPrediction ([6be97f4](https://github.com/harshitpawar64/chessvision/commit/6be97f4c554d44b781c5690572d5edb38d7359bb))
* **board:** add box borders and column alignment to render_board ([6b77b05](https://github.com/harshitpawar64/chessvision/commit/6b77b05d5ba7493c7a603045b22c0cb281ea9266))
* **board:** add validation_errors property to BoardPrediction ([7074d6e](https://github.com/harshitpawar64/chessvision/commit/7074d6ec1e3ecbbe6cee4f3fa4dfaa740b911af4))
* **classifier:** add name property to SquarePrediction ([f331d5a](https://github.com/harshitpawar64/chessvision/commit/f331d5a8af07553f25bbe19a295b976f15542605))
* **cli:** report validation errors at the end of board prediction ([a911986](https://github.com/harshitpawar64/chessvision/commit/a911986e2170065afa891208087b48943d900333))
* **cli:** use piece name in square command and center multi-board header ([6da2fd3](https://github.com/harshitpawar64/chessvision/commit/6da2fd3ec4b34e39d82513c78b7ae188ed5ad949))
* **constants:** add PIECE_NAMES mapping for human-readable labels ([3550e05](https://github.com/harshitpawar64/chessvision/commit/3550e05014eb8404a7d2affe2da9b25aa2705e0b))
* **detector:** fallback to full image when no contour candidates found ([83cdad7](https://github.com/harshitpawar64/chessvision/commit/83cdad7c951bb4e48e37809f6037bbb8a95208af))


### Documentation

* **readme:** update API usage examples ([e3b00d7](https://github.com/harshitpawar64/chessvision/commit/e3b00d725549d2af0b037ad876086258ee5a5b4c))

## [0.5.0](https://github.com/harshitpawar64/chessvision/compare/v0.4.0...v0.5.0) (2026-09-09)


### Features

* **board:** add is_valid property to BoardPrediction ([fdfc466](https://github.com/harshitpawar64/chessvision/commit/fdfc4666d973293c9bec6da54d254a23a0814339))
* **classifier:** support custom model path and cache directory ([cfca7e8](https://github.com/harshitpawar64/chessvision/commit/cfca7e8d4b040f2336702f36dd106da71fb7945a))
* **cli:** warn if illegal chess position is detected ([c83dc46](https://github.com/harshitpawar64/chessvision/commit/c83dc4628b2ba1da94d227b7321cc63c7895e20f))
* **detector:** add 8x8 chessboard verification and adaptive thresholding ([eb924f5](https://github.com/harshitpawar64/chessvision/commit/eb924f58ebe1bce7ec1f491a50c1f6492d7282b6))


### Documentation

* **readme:** add codecov and hugging face badges ([81b7e52](https://github.com/harshitpawar64/chessvision/commit/81b7e522459513f59dcfb8e3421cd5b84c11551a))
* **readme:** add pytest badge ([240836d](https://github.com/harshitpawar64/chessvision/commit/240836de50949d03e4c4e435a335cf43b6ca2c75))

## [0.4.0](https://github.com/harshitpawar64/chessvision/compare/v0.3.0...v0.4.0) (2026-09-05)


### Features

* **board:** add url property to BoardPrediction ([9756156](https://github.com/harshitpawar64/chessvision/commit/97561564e004de7631c810396a5430594405d000))
* **board:** use Turn enum for active color parameter ([4220604](https://github.com/harshitpawar64/chessvision/commit/42206049715b6320b2182458898aad2bb137dba8))
* **cli:** add --open flag to open position in lichess editor ([b57e74d](https://github.com/harshitpawar64/chessvision/commit/b57e74d18d0af2dd8c04bb07b930cc5556926d23))
* **cli:** add --turn flag to specify side to move ([f0d4204](https://github.com/harshitpawar64/chessvision/commit/f0d4204e8aea591b3317b10d90f4173da85bda21))
* **cli:** support multi-board detection in board prediction command ([5d124d6](https://github.com/harshitpawar64/chessvision/commit/5d124d671786496cd2e0ae74179022c1e65c8be9))
* **constants:** add turn enum to specify side to move ([2eb1e48](https://github.com/harshitpawar64/chessvision/commit/2eb1e480ce0a788574e2d622a88fb31613ebb340))
* **detector:** implement BoardDetector for multi-board detection ([d2df679](https://github.com/harshitpawar64/chessvision/commit/d2df679cdc496368fe6f5614505189589f891bd1))

## [0.3.0](https://github.com/harshitpawar64/chessvision/compare/v0.2.0...v0.3.0) (2026-09-01)


### Features

* **board:** implement BoardPredictor and FEN generation pipeline ([e2845f9](https://github.com/harshitpawar64/chessvision/commit/e2845f9cc65e2d9ab9b2ebb14764055e86e2b390))
* **cli:** add board prediction command ([f9e68b4](https://github.com/harshitpawar64/chessvision/commit/f9e68b49a4f2a45f8af63c667f7d7f0d6be67181))
* **constants:** add orientation and castling enums with piece symbol mappings ([302ed87](https://github.com/harshitpawar64/chessvision/commit/302ed875f7c7fa7d3f7bacf3cc83861b55130a94))


### Refactor

* **classifier:** clean up redundant type casts ([32c97d7](https://github.com/harshitpawar64/chessvision/commit/32c97d77d2f8e4b5b9fc54ba637448585a8be3e3))


### Documentation

* **readme:** update README and add demo assets ([66b55e6](https://github.com/harshitpawar64/chessvision/commit/66b55e6de749851dd8b0365292c0229b94b48586))

## [0.2.0](https://github.com/harshitpawar64/chessvision/compare/v0.1.0...v0.2.0) (2026-08-29)


### Features

* **classifier:** implement PieceClassifier with onnx inference and model caching ([7b691d4](https://github.com/harshitpawar64/chessvision/commit/7b691d4aa181d488fc1bb981582dad881a9ddec8))
* **cli:** add square prediction command ([a971379](https://github.com/harshitpawar64/chessvision/commit/a971379560e50b3afc57c25f00ac973aceeaf89d))
* **constants:** add piece classes and lookup mapping ([ee2c988](https://github.com/harshitpawar64/chessvision/commit/ee2c9887e0ecd9ac91199bc732bf737bdcd433e7))
* **train:** add piece classifier training pipeline and image transforms ([ad0f3dc](https://github.com/harshitpawar64/chessvision/commit/ad0f3dc71022e46a1a7302135693141bd16c9c6e))
* **train:** add synthetic dataset generator and training assets ([8db6306](https://github.com/harshitpawar64/chessvision/commit/8db630620a4fd5fa4415d097a0303333dfbd1731))
* **train:** embed metadata in model and remove max batch size constraint ([4743e2b](https://github.com/harshitpawar64/chessvision/commit/4743e2b9180483c898ef71a7eaa2b5024ea81e22))

## 0.1.0 (2026-08-23)


### Features

* **cli:** add initial cli entrypoint and project scaffolding ([09593ba](https://github.com/harshitpawar64/chessvision/commit/09593ba8a3f4c6c72a71d347d9b187fdc7837348))

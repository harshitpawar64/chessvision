# Changelog

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

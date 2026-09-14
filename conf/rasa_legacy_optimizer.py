#!/usr/bin/env python3
"""Launch Rasa with the optimizer graph used by Apple-ARM training.

The production checkpoint was trained locally on Apple Silicon with
TensorFlow/Keras 2.12. Keras automatically substitutes ``legacy.Adam`` on
Apple ARM, but does not do so on Linux. Rasa 3.6.21 otherwise accepts a
partial checkpoint restore on Linux, leaving DIET/TED weights uninitialised
and making every intent fall back.

Keep this launcher coupled to the pinned Rasa/TensorFlow/Keras 2.12 runtime.
Remove it only after retraining without this shim (using Linux's native
optimizer graph) and validating that artifact, or after an explicit
compatibility test during a framework upgrade.
"""

from __future__ import annotations

import keras.optimizers


def _use_legacy_optimizer() -> bool:
    return True


if not hasattr(keras.optimizers, "is_arm_mac"):
    raise RuntimeError(
        "Unsupported Keras runtime: missing keras.optimizers.is_arm_mac. "
        "Retest the production checkpoint before upgrading Rasa/TensorFlow."
    )

# This must happen before importing Rasa model classes.
keras.optimizers.is_arm_mac = _use_legacy_optimizer

from rasa.__main__ import main  # noqa: E402  (import order is intentional)


if __name__ == "__main__":
    main()

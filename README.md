# Software

This repo contains **SoftStrange-ImageEditor**, a folder-based image processing tool for Charlie's World.

It processes images from repo folders, cleans near-white AI image backgrounds, and moves batches through a conveyor structure:

```text
image-pipeline/inbox -> processing -> processed/accepted|review|rejected -> archive/originals -> reports -> previews
```

## Commands

```bash
python -m pip install -e .
ss-image validate-direction --direction directions/white-clean.json
ss-image run --input image-pipeline/inbox/test-batch --direction directions/white-clean.json --output artifacts/test-run
ss-image repo-process --repo-root . --input-folder image-pipeline/inbox/test-batch --direction directions/white-clean.json --pipeline-root image-pipeline
```

## Workflows

- `process-images-manual.yml` manually processes a folder input.
- `process-image-inbox.yml` processes files added under `image-pipeline/inbox/**` and moves them along.
- `test-image-editor.yml` validates the tool and runs a smoke pass.

## Test images

The workflow can generate a few synthetic test images into `image-pipeline/inbox/test-batch` when the inbox is empty, then move them through the pipeline.

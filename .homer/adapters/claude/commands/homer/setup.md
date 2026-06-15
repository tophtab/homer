Initialize or repair this directory as one Homer book project.

Follow the `homer-setup` skill. After infrastructure exists, run:

```bash
python3 .homer/scripts/homer.py init --scan
python3 .homer/scripts/homer.py generate-adapters
python3 .homer/scripts/homer.py status
```

Do not guess imported chapter status when the current user instruction does not make it clear.

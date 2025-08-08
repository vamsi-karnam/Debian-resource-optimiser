# Debian-resource-optimiser
A lightweight, self-learning background daemon for Debian that continuously monitors system state (memory, CPU, swap, services, power) and uses tabular Q-learning to suggest (or apply) optimisations - suspending low-priority services and renicing memory-heavy processes - while respecting protected system components and active I/O workloads.

\# 🛰️ A.R.C. Nexus: Universal Media Ingestion Engine (v4.1.0)



!\[Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)

!\[License](https://img.shields.io/badge/License-MIT-green)

!\[Engine](https://img.shields.io/badge/Core-yt--dlp-red)



\*\*A.R.C. Nexus\*\* is a hardened, platform-agnostic media ingestion engine designed for high-res archival and batch processing. Built with an "Input-Guard" architecture, it proactively handles common user errors and system constraints to ensure 100% uptime during mass data ingestion.



\---



\## 🏛️ Architectural Framework (The Council of Three)

This engine was designed by simulating three expert perspectives:

1\.  \*\*The Visionary:\*\* Aiming for a universal, platform-agnostic scraper supporting 1000+ sites.

2\.  \*\*The Pragmatist:\*\* Focuses on memory efficiency, hardware constraints (FFmpeg), and error containment.

3\.  \*\*The Strategist:\*\* Prioritizes clean telemetry, metadata embedding, and scalable batch processing.



\---



\## 🚀 Key Features

\*   \*\*Self-Healing Logic:\*\* Automatically detects and repairs swapped URL/Path inputs, preventing NTFS directory crashes.

\*   \*\*Universal Ingestion:\*\* Supports YouTube, TikTok, X (Twitter), Instagram, Vimeo, and more.

\*   \*\*Batch Processing:\*\* Ingest infinite targets via a simple `.txt` file with isolated error containment.

\*   \*\*FFmpeg Fusion:\*\* Automated stream merging for 1080p+ and high-bitrate MP3 extraction.

\*   \*\*Advanced Telemetry:\*\* Real-time progress bars and session reports powered by the `Rich` library.



\---



\## 📦 Installation \& Setup



\### 1. Clone the Architecture

```bash

git clone \[https://github.com/aviwenotununu4-max/ARC-Nexus-Engine.git](https://github.com/aviwenotununu4-max/ARC-Nexus-Engine.git)

cd ARC-Nexus-Engine


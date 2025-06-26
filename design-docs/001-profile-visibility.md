# 001 - Profile Visibilities

| <!-- -->               |  <!-- -->  |
| ---------------------- | :--------: |
| **Last modified date** | 2025-06-26 |
| **Author(s)**          | @kisamoto  |
| **Status**             |  Approved  |

## Decision & Rationale

Profile visibility should vary depending on a combination of user preferences and whether they have subscribed or not. The visibility options are summarised below.

| Visibility Status  | Requires active subscription | Appears in search results | What it means                                                          |
| ------------------ | :--------------------------: | :-----------------------: | ---------------------------------------------------------------------- |
| Public             |              ✅              |            ✅             | Profile can be viewed by both authenticated and unauthenticated users. |
| Hidden (_default_) |              ❌              |            ❌             | Only authenticated users can view profile.                             |
| Private            |              ❌              |            ❌             | Only authenticated and approved users can view profile.                |

## Changelog

### 2025-06-26

Initial doc.
